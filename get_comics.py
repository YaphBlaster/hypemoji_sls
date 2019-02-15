try:
  import unzip_requirements
except ImportError:
  pass
  
import json
import requests

def get_comics(event, context):
    try:
        body = {
            "message": "Go Serverless v1.0! Your function executed successfully!",
            "input": event
        }

        response = {
            "statusCode": 200,
            "body": requests.get('https://api.bitmoji.com/content/templates').json()
        }

    except Exception as e:
        response = {
            "statusCode": 500,
            "body": e
        }

    return response


if __name__ == "__main__":
    print(get_comics('', ''))
