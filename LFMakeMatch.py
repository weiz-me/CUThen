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

def lambda_handler(event, context):
    print(event)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
