# This file is designed for the lambda function to make invitations
# in the project CUThen, the final project for COMSE6998_010_2023_3,
# Topics in Computer Science: Cloud Computing and Big Data.

import os
import json
import string
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from botocore.exceptions import ClientError

REGION = 'us-east-1'
HOST = 'search-cuthen-temp-5fyo5fvs7x7t2myle4ztwa7swa.us-east-1.es.amazonaws.com'
INDEX1 = 'user_to_group'
INDEX2 = 'user_to_inv'
INDEX3 = 'group_to_user'

def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)

def lookup_data(key, db=None, table='user_table'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    try:
        response = table.get_item(Key=key)
    except ClientError as e:
        print('Error', e.response['Error']['Message'])
        return False
    else:
        ret = response['Item']
        ret['user_id'] = int(ret['user_id'])
        return ret

def query(client, index, field, term):
    q = {"query": {
            "bool": {
                "must": {
                    "match": {
                        field: term
                    }
                }
            }
        }
    }

    res = client.search(index=index, body=q)
    print(res)

    hits = res['hits']['hits']
    return hits[0]['_source']

def get_user(userId):
    user = {}
    userInfo = lookup_data(key = {"user_id": userId}, table='user_table')
    user['userId'] = userInfo['user_id']
    user['userName'] = userInfo['first_name'] + ' ' + userInfo['last_name']
    user['userFeatures'] = [{k: v} for k, v in userInfo.items()]
    return user

def sendEmail(email, groupId):
    client = boto3.client('ses', region_name='us-east-1')
    emailmsg = ("Dear CUThen user,\n\nYou have an invitation to join group #" + str(groupId)
                + "!\n\nPlease log in to CUThen to accept or reject the invitation.\n\nBest,\nCUThen Team")
    message = {
        'Subject': {
            'Data': "CUThen - You have an invitation to join group #" + str(groupId) + "!"
        },
        'Body': {
            'Text': {
                'Data': emailmsg
            }
        }
    }
    response = client.send_email(Source='chengyu.sun@columbia.edu', 
                                 Destination={
                                    'ToAddresses': [email],
                                    'BccAddresses': [],
                                    'CcAddresses': []
                                    },
                                Message=message)
    return response

def lambda_handler(event, context):
    print(event)

    inv = json.loads(event['body']['o_inv'])
    userId = int(inv['invitee'])
    groupId = int(inv['currentGroup'])

    os_client = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
    }],
                        http_auth=get_awsauth(REGION, 'es'),
                        use_ssl=True,
                        verify_certs=True,
                        connection_class=RequestsHttpConnection)

    user_inv = query(client=os_client, index=INDEX2, field='user_id', term=str(userId))

    if groupId in user_inv['pending_inv_ids']:
        return {
            'statusCode': 403,
            'body': json.dumps("Already invited!")
        }
    
    user_info = get_user(userId)
    email = ""
    for d in user_info['userFeatures']:
        if 'email' in d:
            email = d['email']
            break
    
    # sending emails
    sendEmail(email, groupId)

    inv_document = {"user_id": userId, "pending_inv_ids": user_inv['pending_inv_ids'] + [groupId]}
    os_client.index(index=INDEX2, id = int(userId), body=inv_document, refresh=True)

    return {
        'statusCode': 200,
        'body': json.dumps("Invitation sent!")
    }
