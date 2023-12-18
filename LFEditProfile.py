import json
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import json

REGION = 'us-east-1'
HOST = 'search-cuthen-temp-5fyo5fvs7x7t2myle4ztwa7swa.us-east-1.es.amazonaws.com'
INDEX1 = 'max_id'
INDEX2 = 'user_to_inv'
INDEX3 = 'user_to_group'

def lambda_handler(event, context):
    # uni is the primary/paritition key
    # note they all have unique attributes
    print(event)
    user_data = event['body']
    user_data = json.loads(user_data)

    print(f"{user_data}")

    # mock
    # user_data = {   
    #     "user_id": 1,
    #     "first_name": "Timothy",
    #     "last_name": "Wang",
    #     "uni": "tjw2145",
    #     "email": "tjw2145@columbia.edu",
    #     "hobbies": "none",
    #     "major": "none",
    #     "school": "none",
    #     "academic_interests": "none",
    #     "class_schedule": "none",
    #     "exam_schedule": "none",
    #     "phone_number": "none",
    #     "zipcode": "12345"
    # }

    orginal = lookup_data({'user_id': user_data["currentUser"]}, table="user_table")
    if orginal == None:
        new_id = create_user(user_data["newFeatures"], table="user_table")
        print(f"new_id: {new_id}")
        updated_Data = lookup_data({'user_id': new_id}, table="user_table")
        response = {"message":"insert success","input": user_data , "updated_Data":updated_Data}
        resp = {
                'statusCode': 200,
                'body': json.dumps(response)
        }
        return resp
    else:
        update_item_list({'user_id': int(user_data["currentUser"])},user_data["newFeatures"],table="user_table")
        updated_Data = lookup_data({'user_id': user_data["currentUser"]}, table="user_table")
        response = {"message":"update success","input": user_data , "updated_Data":updated_Data}
        resp = {
                'statusCode': 200,
                'body': json.dumps(response)
        }
        return resp

def lookup_data(key, db=None, table='6998Demo'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    try:
        response = table.get_item(Key=key)
    except ClientError as e:
        print('Error', e.response['Error']['Message'])
    else:
        # if user not in table
        if 'Item' not in response:
            return None
        res = response['Item']
        res['user_id'] = int(res['user_id']) 
        print(f"{res =}")
        return response['Item']
        
def update_item_list(key, feature_dict_list, db=None, table='6998Demo'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)

    for feature_dict in feature_dict_list:
        feature_name, feature = list(feature_dict.items())[0]
        print(f"feature_name: {feature_name}, feature: {feature}")
        if feature_name == "user_id":
            continue
        
        print(f"Key: {key}")
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

def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)

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
    print(f"hits on max user id: {hits[0]['_source']}")
    return hits[0]['_source']

def create_user(features, db=None, table='6998Demo'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)

    os_client = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
    }],
                        http_auth=get_awsauth(REGION, 'es'),
                        use_ssl=True,
                        verify_certs=True,
                        connection_class=RequestsHttpConnection)

    # get max user id
    max_id = int(query(client=os_client, index=INDEX1, field='type', term='user_id')['max'])
    item = {}

    for feature_dict in features:
        feature_name, feature = list(feature_dict.items())[0]
        item[feature_name] = str(feature)
    item['user_id'] = max_id + 1
    print(f"item to be inserted into dynamodb: {item}")

    response = table.put_item(Item = item)
    print("user created and inserted into dynamodb")

    # update max user id
    max_id_document = {"max": max_id + 1, "type": "user_id"}
    os_client.index(index=INDEX1, id = 2, body=max_id_document, refresh=True)

    # create new user_to_inv and user_to_group entry
    inv_document = {"user_id": max_id + 1, "pending_inv_ids": []}
    os_client.index(index=INDEX2, id = max_id + 1, body=inv_document, refresh=True)

    group_document = {"user_id": max_id + 1, "group_id": []}
    os_client.index(index=INDEX3, id = max_id + 1, body=group_document, refresh=True)
    return max_id + 1