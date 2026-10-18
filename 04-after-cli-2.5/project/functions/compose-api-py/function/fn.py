"""Composición XPocCliApiService en Python (función embebida del proyecto).

Misma lógica que la composición go-templating, pero con modelos tipados generados por
`crossplane dependency add` (providers) y `crossplane xrd generate` (el propio XR):
el editor autocompleta y Pydantic valida tipos/enums antes de emitir nada.
Los XRs generales (XAPIGatewayRestStack, XAPIGatewayIntegration, XKMS) van como dict
porque aún no se publican como paquete (no hay modelos para ellos).
"""

import json

import grpc
from crossplane.function import logging, resource, response
from crossplane.function.proto.v1 import run_function_pb2 as fnv1
from crossplane.function.proto.v1 import run_function_pb2_grpc as grpcv1

from models.com.nequi.platform.cli.poc.xpoccliapiservice import v1alpha1 as xapi
from models.io.upbound.m.aws.apigateway.deployment import v1beta1 as deployment
from models.io.upbound.m.aws.apigateway.stage import v1beta1 as stage
from models.io.upbound.m.aws.cloudwatch.metricalarm import v1beta1 as alarm
from models.io.upbound.m.aws.cloudwatchlogs.group import v1beta1 as group

ACCESS_LOG_FORMAT = json.dumps({
    "requestId": "$context.requestId", "ip": "$context.identity.sourceIp", "method": "$context.httpMethod",
    "path": "$context.resourcePath", "status": "$context.status", "latency": "$context.responseLatency",
})


def _observed(req, name):
    if name not in req.observed.resources:
        return {}
    return resource.struct_to_dict(req.observed.resources[name].resource)


def _is_ready(obj):
    return any(c.get("type") == "Ready" and c.get("status") == "True" for c in obj.get("status", {}).get("conditions", []))


class FunctionRunner(grpcv1.FunctionRunnerService):
    """A FunctionRunner handles gRPC RunFunctionRequests."""

    def __init__(self):
        self.log = logging.get_logger()

    async def RunFunction(self, req: fnv1.RunFunctionRequest, _: grpc.aio.ServicerContext) -> fnv1.RunFunctionResponse:
        log = self.log.bind(tag=req.meta.tag)
        rsp = response.to(req)

        xr = xapi.XPocCliApiService.model_validate(resource.struct_to_dict(req.observed.composite.resource))
        p = xr.spec.parameters
        base = f"{p.capacity}-{p.country}-{p.functionality}-{p.env}"
        api_name = f"apigw-{base}"
        log_group = f"/aws/apigateway/access-{base}"
        log_group_arn = f"arn:aws:logs:{p.region}:{p.accountId}:log-group:{log_group}"
        labels = dict(xr.metadata.labels or {}) if xr.metadata else {}
        identity = {"serviceid": p.serviceid, "capacity": p.capacity, "country": p.country, "env": p.env}
        tags = {**identity, "deployment": "jarvis", **(p.tags or {})}
        pc = {"name": p.providerConfigName, "kind": "ClusterProviderConfig"}

        def child_xr(name, kind, meta_name, params):
            resource.update(rsp.desired.resources[name], {
                "apiVersion": "aws.platform.nequi.com/v1alpha1", "kind": kind,
                "metadata": {"name": meta_name, "labels": labels},
                "spec": {"parameters": params},
            })

        # 1. API REST regional (bloque general)
        c = p.classification
        child_xr("api", "XAPIGatewayRestStack", f"poc-api-{base}", {
            **identity, "deployment": "jarvis", "region": p.region, "accountId": p.accountId, "standardName": True,
            "providerConfigRef": {"name": p.providerConfigName}, "tags": p.tags or {}, "apiName": api_name,
            "description": f"API {p.functionality} publicada por la plataforma", "endpointType": "REGIONAL",
            "confidentiality": c.confidentiality, "integrity": c.integrity, "availability": c.availability, "pci": bool(c.pci),
        })

        # 2. /health (bloque general) cuando la API tiene id
        api_status = _observed(req, "api").get("status", {}).get("atProvider", {})
        api_id, root_id = api_status.get("restApiId"), api_status.get("rootResourceId")
        if api_id and root_id:
            child_xr("health", "XAPIGatewayIntegration", f"poc-health-{base}", {
                "region": p.region, "env": p.env, "providerConfigRef": {"name": p.providerConfigName},
                "apiId": api_id, "managementPolicies": ["*"],
                # Claves únicas por servicio: el bloque general nombra recursos con la clave (sin prefijo)
                "pathResources": {f"health-{p.functionality}": {"parentId": root_id, "pathPart": "health"}},
                "apiResources": {f"health-get-{p.functionality}": {
                    "resourceId": f"@health-{p.functionality}", "httpMethod": "GET", "authorization": "NONE", "apiKeyRequired": False,
                    # MOCK no es viable con el bloque general (uri vacío): backend HTTP público de AWS
                    "integrationType": "HTTP", "integrationUri": "https://checkip.amazonaws.com/",
                    "integrationHttpMethod": "GET", "statusCode": 200,
                }},
            })

        # 3. CMK propia (bloque general)
        key_policy = {"Version": "2012-10-17", "Statement": [
            {"Sid": "RootAccount", "Effect": "Allow", "Principal": {"AWS": f"arn:aws:iam::{p.accountId}:root"},
             "Action": "kms:*", "Resource": "*"},
            {"Sid": "CloudWatchLogs", "Effect": "Allow", "Principal": {"Service": f"logs.{p.region}.amazonaws.com"},
             "Action": ["kms:Encrypt*", "kms:Decrypt*", "kms:ReEncrypt*", "kms:GenerateDataKey*", "kms:Describe*"],
             "Resource": "*", "Condition": {"ArnEquals": {"kms:EncryptionContext:aws:logs:arn": log_group_arn}}},
        ]}
        child_xr("kms", "XKMS", f"poc-kms-{base}", {
            **identity, "deployment": "jarvis", "region": p.region, "standardName": True,
            "providerConfigRef": {"name": p.providerConfigName},
            "key": {"name": p.functionality, "description": f"CMK access logs de {api_name}", "enableKeyRotation": True,
                    "deletionWindowInDays": 7, "policy": json.dumps(key_policy)},
        })

        # 4. Log group cifrado (directo, tipado) cuando la llave existe
        key_arn = _observed(req, "kms").get("status", {}).get("atProvider", {}).get("keyArn")
        retention = (p.logs.retentionInDays if p.logs and p.logs.retentionInDays else (90 if p.env == "pdn" else 14))
        if key_arn:
            resource.update(rsp.desired.resources["logs"], group.Group(
                metadata={"name": f"poc-logs-{base}", "namespace": p.providerConfigName, "labels": labels,
                          "annotations": {"crossplane.io/external-name": log_group}},
                spec=group.Spec(providerConfigRef=pc, forProvider=group.ForProvider(
                    region=p.region, retentionInDays=retention, kmsKeyId=key_arn, tags=tags)),
            ))

        # 5. Deployment + Stage con access logs (directos, tipados)
        if api_id and _is_ready(_observed(req, "health")):
            resource.update(rsp.desired.resources["deployment"], deployment.Deployment(
                metadata={"name": f"poc-deploy-{base}", "namespace": p.providerConfigName},
                spec=deployment.Spec(providerConfigRef=pc, forProvider=deployment.ForProvider(
                    region=p.region, restApiId=api_id, description="Despliegue de la plataforma",
                    triggers={"redeployment": "health-get-http-v1"})),
            ))
        deployment_id = _observed(req, "deployment").get("status", {}).get("atProvider", {}).get("id")
        logs_ready = bool(_observed(req, "logs").get("status", {}).get("atProvider", {}).get("arn"))
        if deployment_id and logs_ready:
            resource.update(rsp.desired.resources["stage"], stage.Stage(
                metadata={"name": f"poc-stage-{base}", "namespace": p.providerConfigName},
                spec=stage.Spec(providerConfigRef=pc, forProvider=stage.ForProvider(
                    region=p.region, restApiId=api_id, deploymentId=deployment_id, stageName=p.env,
                    xrayTracingEnabled=False, tags=tags,
                    accessLogSettings=stage.AccessLogSettings(destinationArn=log_group_arn, format=ACCESS_LOG_FORMAT))),
            ))

        # 6. Alarmas (directas, tipadas) cuando el stage existe
        if "stage" in req.observed.resources:
            latency = p.alarms.latencyP99Ms if p.alarms and p.alarms.latencyP99Ms else 2000
            specs = [("5xx", "5XXError", {"statistic": "Sum"}, 0, 60, "Errores 5XX en la API"),
                     ("latency", "Latency", {"extendedStatistic": "p99"}, latency, 300, "Latencia p99 sobre el umbral")]
            for aid, metric, stat, threshold, period, desc in specs:
                resource.update(rsp.desired.resources[f"alarm-{aid}"], alarm.MetricAlarm(
                    metadata={"name": f"poc-alarm-{base}-{aid}", "namespace": p.providerConfigName,
                              "annotations": {"crossplane.io/external-name": f"alarm-{base}-{aid}"}},
                    spec=alarm.Spec(providerConfigRef=pc, forProvider=alarm.ForProvider(
                        region=p.region, alarmDescription=f"{desc} {api_name}", namespace="AWS/ApiGateway",
                        metricName=metric, dimensions={"ApiName": api_name, "Stage": p.env},
                        comparisonOperator="GreaterThanThreshold", threshold=threshold, period=period,
                        evaluationPeriods=1, treatMissingData="notBreaching", tags=tags, **stat)),
                ))

        # 7. Status del XR
        status = {}
        if api_id:
            status.update(restApiId=api_id, invokeUrl=f"https://{api_id}.execute-api.{p.region}.amazonaws.com/{p.env}/health")
        if key_arn:
            status["kmsKeyArn"] = key_arn
        if logs_ready:
            status["logGroupName"] = log_group
        if status:
            resource.update(rsp.desired.composite, {"status": status})

        log.info("Composed", resources=len(rsp.desired.resources))
        return rsp
