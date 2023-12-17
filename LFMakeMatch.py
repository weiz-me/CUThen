# This file is designed for the lambda function to make matches
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

def scan_data(db=None, table='user_table'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    try:
        response = table.scan()
    except ClientError as e:
        print('Error', e.response['Error']['Message'])
        return False
    else:
        ret = response['Items']
        return ret

def query(index, field, term):
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

    client = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
    }],
                        http_auth=get_awsauth(REGION, 'es'),
                        use_ssl=True,
                        verify_certs=True,
                        connection_class=RequestsHttpConnection)

    res = client.search(index=index, body=q)
    print(res)

    hits = res['hits']['hits']
    return hits[0]['_source']

def get_user(userId):
    user = {}
    userInfo = lookup_data(key = userId, table='user_table')
    user['userId'] = userInfo['user_id']
    user['userName'] = userInfo['first_name'] + ' ' + userInfo['last_name']
    user['userFeatures'] = [{k: v} for k, v in userInfo.items()]
    return user

def get_group(groupId):
    group = {}
    gobj = query(index=INDEX3, field='group_id', term=str(groupId))
    gleader = get_user(gobj['leader_id'])
    gmember = []
    for mid in gobj['user_id']:
        gmember.append(get_user(mid))
    group['groupId'] = int(groupId)
    group['groupLeader'] = gleader
    group['groupMembers'] = gmember
    return group

def lambda_handler(event, context):
    print(event)
    currentUser = get_user("user_id": {"N":event['userId']}) # N denotes that the string value should be interpreted as a number

    all_users = scan_data(table='user_table')

    other_users = [user for user in all_users if int(user['user_id']) != int(currentUser['user_id'])]

    # FOR TESTING ONLY
    return {
        'statusCode': 200,
        'body': json.dumps(other_users)
    }
