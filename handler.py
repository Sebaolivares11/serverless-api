import json
import boto3
import logging
import os

from custom_encoder import CustomEncoder
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodbTableName ='test-api'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodbTableName)

getMethod = 'GET'
postmethod = 'POST'
patchMethod = 'PATCH'
deleteMethod = 'DELETE'

usersPath = '/users'


def post_users(event, context):
    logger.info(event['body'])
    httpmethod = event['httpMethod']
    path = event['path']
    if httpmethod == getMethod and path == usersPath:
        response = buildResponse(200)
    if httpmethod == postmethod and path == usersPath:
        response = saveUser(json.loads(event['body']))
    #elif httpmethod == patchMethod and path == usersPath:
    #    requestBody = json.loads(event['body'])
    #    response = modifyUser(requestBody['id'], requestBody['updateKey'], requestBody['updateValue'])
    else:
        response = buildResponse(404, 'Not Found')
    return response


def saveUser(requestBody):
    try:
        table.put_item(Item=requestBody)
        body= {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'item': requestBody
        }
        return buildResponse(200, body)
    except:
        logger.exception('Error creating user')


def modifyUser(userId, updateKey,updateValue):
    try:
        response = table.update_item(
            key={ 'id': userId },
            UpdateExpression = 'set %s = :value '% updateKey,
            ExpressionAttributeValues={ ':value': updateValue },
            returnValues= 'UPDATED_NEW'
        )
        body={
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'UpdatedAttributes': response
        }
        return buildResponse(200, body)
    except:
        logger.exception('Error updating the attributes of this user')

def buildResponse(status_code, body=None):
    response = {
        'statusCode': status_code,
        'headers': {
            'Context-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
    return response

