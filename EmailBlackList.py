import boto3
import json

print('Loading function')
dynamo = boto3.client('dynamodb')

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def lambda_handler(event, context):
    operations = {
        'GET': lambda dynamo, x: dynamo.get_item(**x),
        'POST': lambda dynamo, x: dynamo.put_item(**x)
    }
    operation = event['httpMethod']
    if operation in operations:
        payload = event['queryStringParameters'] if operation == 'GET' else json.loads(event['body'])
        if operation == "GET":
            query = {"TableName":"EmailBlackList",
                "Key":{
                    "Email":{"S":payload["Email"]}
                }
            }
            payload = query
            if "Item" in operations[operation](dynamo, payload):
                return respond(None,"esta en la lista negra")
            else :
                return respond(None,"No esta en la lista negra")
        elif operation == "POST":
            payload["Item"]["Ip"] = {"S":event["requestContext"]["identity"]["sourceIp"]}
            payload["Item"]["Hora_agregado"] = {"S":event["requestContext"]["requestTime"]}
            return respond(None, operations[operation](dynamo, payload))
    else:
        return respond(ValueError('Metodo no permitido "{}"'.format(operation)))
        