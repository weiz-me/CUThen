

import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

REGION = 'us-east-1'
HOST = 'search-cuthen-temp-5fyo5fvs7x7t2myle4ztwa7swa.us-east-1.es.amazonaws.com'

INDEX0 = 'max_id'

def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)

def opensearch_init():
    opensearch_client = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
    }],
                        http_auth=get_awsauth(REGION, 'es'),
                        use_ssl=True,
                        verify_certs=True,
                        connection_class=RequestsHttpConnection)
    return opensearch_client
def del_by_index(INDEX):
    opensearch_client=opensearch_init()
    delete_query = {
        "query": {
            "match_all": {}
        }
    }
    opensearch_client.delete_by_query(index=INDEX, body=delete_query, refresh=True)

def ins_by_index(INDEX,document,id):
    opensearch_client=opensearch_init()
    # document = {"user_id": 1,"group_id": [2]}
    rm_res = opensearch_client.index(index=INDEX, id = id, body=document, refresh=True)

def search_by_index(INDEX,field,user_id):
    opensearch_client=opensearch_init()
    # field = "user_id"
    q3 = {
        "query": {
            "query_string": {
              "query": user_id,
                "fields": [field]
                }
            }
        }
    res3 = opensearch_client.search(index=INDEX, body=q3)
    
    hits = res3['hits']['hits']
    results = []
    for hit in hits:
        results.append(hit['_source'])

    print(f"{results =}")
    return results

def lambda_handler(event, context):
    print(event)

    # input_data = {
    #     "send": 1,
    #     "group_id": 1,
    #     "user_id": 3,
    #     "message":"hello, wei testing"
    # }
    
    input_data = event['body']
    input_data = json.loads(input_data)
    
    send = input_data['send']
    group_id = input_data['group_id']

    # mock database
    # messages_data = [
    #     {'chat_id': 1, 'group_id': 1, 'user_id': 1, 'message': "Hello, it's Tim.", 'time': datetime.now().isoformat()},
    #     {'chat_id': 2, 'group_id': 1, 'user_id': 2, 'message': "Hi, it's Chengyu.", 'time': (datetime.now() + timedelta(minutes=1)).isoformat()},
    #     {'chat_id': 3, 'group_id': 1, 'user_id': 3, 'message': "Hi, It's Wei.", 'time': (datetime.now() + timedelta(minutes=2)).isoformat()}
    # ]
    # insert_data(messages_data, table="chat_table")

    if send:
        user_id = input_data['user_id']
        message = input_data['message']
    
        print("0. getting chat id")
        result = search_by_index(INDEX0,"type","chat_id")
        chat_id = result[0]['max'] + 1
        user_document = {"max": chat_id, "type":"chat_id"}
        ins_by_index(INDEX0,user_document,3)
        print(f"{chat_id = }")

        
        print("1. inserting into database")
        messages_data = [
            {'chat_id': chat_id, 'group_id': group_id, 'user_id': user_id, 'message': message, 'time': (datetime.now()).isoformat()}
        ]
        insert_data(messages_data, table="chat_table")
    
    print("2. getting the chat data")

    result = lookup_data(group_id, db=None, table='chat_table')
    # print(result)
    result = sorted(result, key=lambda x: x['time'])
    
    if len(result) > 10:
        result = result[-9:]

    chat_data= [[res["message"],lookup_user({"user_id":int(res["user_id"])}, db=None, table='user_table')] for res in result]    
    print(f"{chat_data =}")
    

    
    return {
        'statusCode': 200,
        'body': json.dumps(chat_data)
    }

def lookup_user(key, db=None, table='6998Demo'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    try:
        response = table.get_item(Key=key)


    except ClientError as e:
        print('Error', e.response['Error']['Message'])
    else:
        res = response['Item']

        print(f"{res =}")
        return response['Item']["first_name"]
        

def lookup_data(key, db=None, table='6998Demo'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    try:
        response = table.scan(
            FilterExpression='group_id = :g',
            ExpressionAttributeValues={
                ':g': key
            }
        )

    except ClientError as e:
        print('Error', e.response['Error']['Message'])
    else:
        res = response['Items']

        print(f"{res =}")
        return response['Items']
        
def update_item_list(key, feature_dict, db=None, table='6998Demo'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)

    for feature_name, feature in feature_dict.items():
        if feature_name == "user_id":
            continue
        
        response = table.update_item(
            Key=key,
            UpdateExpression="set #feature=:f",
            ExpressionAttributeValues={
                ':f': feature
            },
            ExpressionAttributeNames={
                "#feature": feature_name
            },
            ReturnValues="UPDATED_NEW"
        )

    return


def insert_data(data_list, db=None, table='6998Demo'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    # overwrite if the same index is provided
    for data in data_list:
        response = table.put_item(Item=data)
    print('@insert_data: response', response)
    return response



