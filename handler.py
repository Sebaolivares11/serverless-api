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
    logger.info(event['Records'])
    method = event['Records'][0]['body']
    if method == postMethod:
        #crear un usuario en la cola
        eventAtributes = event['Records'][0]['messageAttributes']
        parsedData = parseQueue(eventAtributes, method)
        response = saveUser(parsedData)
    elif method == patchMethod:
        #modify an existing user 
        eventAtributes = event['Records'][0]['messageAttributes']
        parsedData = parseQueue(eventAtributes, method)
        response = modifyUser(parsedData[0],parsedData[1],parsedData[2])
    else:
        response = buildResponse(404, 'Not Found')
    return response

def parseQueue(messageAtributtes, method):
    if method == postMethod:
        formated = messageAtributtes['username']['stringValue']
    elif method == patchMethod:
        updateKey = messageAtributtes['updateKey']['stringValue']
        updateValue = messageAtributtes['updateValue']['stringValue']
        userId = messageAtributtes['id']['stringValue']
        formated = [userId, updateKey, updateValue]
    return formated

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

