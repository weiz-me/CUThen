# This file is designed for the lambda function to get group information
# in the project CUThen, the final project for COMSE6998_010_2023_3,
# Topics in Computer Science: Cloud Computing and Big Data.

import os
import json
import string
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from botocore.exceptions import ClientError

# question: what is userfeatures returned with userid? Should dynamodb store it?

REGION = 'us-east-1'
HOST_USER_GROUP = '' # TODO: fill in host
INDEX_USER_GROUP = '' # TODO: fill in index
HOST_GROUP_USER = '' # TODO: fill in host
INDEX_GROUP_USER = '' # TODO: fill in index
HOST_GROUP_LEADER = '' # TODO: fill in host
INDEX_GROUP_LEADER = '' # TODO: fill in index

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

def lambda_handler(event, context):
    print(event)
    userID = event['UserId']
    userFeatures = event['UserFeatures']

    groupIDs = query(userID, HOST_USER_GROUP, INDEX_USER_GROUP)
    groups = []
    for gid in groupIDs:
        group = {}
        group['GroupId'] = gid # TODO: confirm opensearch entry format and modify
        gleader = query(gid, HOST_GROUP_LEADER, INDEX_GROUP_LEADER)
        group['GroupLeader'] = gleader # TODO: confirm opensearch entry format and modify
        gmember = query(gid, HOST_GROUP_USER, HOST_GROUP_USER)
        group['GroupMembers'] = gmember # TODO: confirm opensearch entry format and modify

    resp = {
            'statusCode': 200,
            'body': "Get group call success!",
            'Groups': groups
    }
