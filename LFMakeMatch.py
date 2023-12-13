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
HOST_USER_GROUP = '' # TODO: fill in host
INDEX_USER_GROUP = '' # TODO: fill in index
HOST_GROUP_USER = '' # TODO: fill in host
INDEX_GROUP_USER = '' # TODO: fill in index
HOST_GROUP_LEADER = '' # TODO: fill in host
INDEX_GROUP_LEADER = '' # TODO: fill in index
HOST_USER_INVITATION = '' # TODO: fill in host
INDEX_USER_INVITATION = '' # TODO: fill in index

def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)

# query from opensearch instance
def query(term, host, index):
    q = {'query': {'multi_match': {'query': term}}}

    client = OpenSearch(hosts=[{
        'host': host,
        'port': 443
        }],
        http_auth=get_awsauth(REGION, 'es'),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection)

    res = client.search(index=index, body=q)

    hits = res['hits']['hits']

    return hits

# get data from dynamodb
def lookup_data(key, db=None, table=''):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    try:
        response = table.get_item(Key=key)
    except ClientError as e:
        print('Error', e.response['Error']['Message'])
        return False
    else:
        #print(response['Item'])
        return response['Item']

def lambda_handler(event, context):
    print(event)
    # FOR TESTING ONLY
    dummy_response = {
        "compatibleUsers": []
    }
    return {
        'statusCode': 200,
        'body': json.dumps(dummy_response)
    }
