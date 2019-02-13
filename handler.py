import json


def hello(event, context):
    try:
        body = {
            "message": "Go Serverless v1.0! Your function executed successfully!",
            "input": event
        }

        response = {
            "statusCode": 200,
            "body": "hello"
        }

    except Exception as e:
        response = {
            "statusCode": 500,
            "body": e
        }

    return response
