import json
import logging
import uuid

import boto3

from custom_encoder import CustomEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodbTableName ='test-api'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodbTableName)

getMethod = 'GET'
postMethod = 'POST'
patchMethod = 'PATCH'
deleteMethod = 'DELETE'

usersPath = '/users'


def manage_request(event, context):
    logger.info(event['body'])
    httpmethod = event['httpMethod']
    path = event['path']
    if httpmethod == getMethod and path == usersPath:
        response = buildResponse(200)
    elif httpmethod == postMethod and path == usersPath:
        requestBody = json.loads(event['body'])
        response = saveUser(requestBody['username'])
    elif httpmethod == patchMethod and path == usersPath:
        requestBody = json.loads(event['body'])
        response = modifyUser(requestBody['id'], requestBody['updateKey'], requestBody['updateValue'])
    else:
        response = buildResponse(404, 'Not Found')
    return response


def saveUser(requestBody):
    """ function that saves a new user in the dynamo table db
    Args:
        requestBody (string): username at least for now for the new user

    Returns:
        httpResponse
    """
    try:
        key = uuid.uuid4().hex
        table.put_item(
            Item={
                'id': key,
                'username': requestBody
                })
        body= {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'item': { 'id': key, 'username': requestBody }
        }
        return buildResponse(200, body)
    except:
        logger.exception('Error creating user')


def modifyUser(userId, updateKey, updateValue):
    """ modify a username from a dynamo db table

    Args:
        userId (string): unique key from de db
        updateKey (string): update key value to be updated
        updateValue (string): value to change the curren username to
    Returns:
        httpResponse
    """
    try:
        response = table.update_item(
            Key={ 'id': userId },
            UpdateExpression = 'set %s = :value '% updateKey,
            ExpressionAttributeValues={ ':value': updateValue },
            ReturnValues= 'UPDATED_NEW'
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

