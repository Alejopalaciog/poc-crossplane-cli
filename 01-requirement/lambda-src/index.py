import json


def lambda_handler(event, context):
    """Lambda de prueba de la PoC Crossplane CLI 2.5."""
    return {"statusCode": 200, "body": json.dumps({"poc": "crossplane-cli-2.5", "ok": True})}
