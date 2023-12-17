# This file is designed for the lambda function to delete groups
# in the project CUThen, the final project for COMSE6998_010_2023_3,
# Topics in Computer Science: Cloud Computing and Big Data.


import json
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3


REGION = 'us-east-1'
HOST = 'search-cuthen-temp-5fyo5fvs7x7t2myle4ztwa7swa.us-east-1.es.amazonaws.com'
INDEX1 = 'user_to_group'
INDEX2 = 'group_to_user'
INDEX3 = 'user_to_inv'
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

opensearch_client = opensearch_init()

def del_by_index(INDEX):
    # opensearch_client=opensearch_init()
    delete_query = {
        "query": {
            "match_all": {}
        }
    }
    opensearch_client.delete_by_query(index=INDEX, body=delete_query, refresh=True)

def del_by_group(group_id):
    # opensearch_client=opensearch_init()

    opensearch_client.delete(
        index = INDEX2,
        id = str(group_id)
    )

def ins_by_index(INDEX,document,id):
    # opensearch_client=opensearch_init()
    # document = {"user_id": 1,"group_id": [2]}
    rm_res = opensearch_client.index(index=INDEX, id = id, body=document, refresh=True)

def search_by_index(INDEX,field,user_id):
    # opensearch_client=opensearch_init()
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

    # mock input data
    # input_data = {
    #     "group_id":1,
    # }

    # TODO implement
    print(f"{event = }")
    print(f"{context = }")

    input_data = event['body']
    input_data = json.loads(input_data)

    group_id = input_data["group_id"]
    opensearch_client = opensearch_init()

    print("1. opening opensearch")
    opensearch_client = opensearch_init()

    # adding it to user-group, group-user
    # orginal_data={}
    # updated_data={}
    print("2. deleting from group-user")
    result = search_by_index(INDEX2,"group_id",group_id)
    results2=result[0]['user_id']
    results3=result[0]['leader_id']
    print(f"\tGroup user_id: {results2}")
    print(f"\tGroup leader_id: {results3}")
    deleted_data = [result[0]]
    # orginal_data["group_user_id"]=results2
    # orginal_data["group_leader_id"]=results3
    del_by_group(group_id)
    
    print("3. deleting from user-group")
    if results3 not in results2:
        results2.append(results3)
    
    # orginal_data["user_data"]=[]
    # updated_data["user_data"]=[]
    for user_id in results2:
        result = search_by_index(INDEX1,"user_id",user_id)
        results1=result[0]['group_id']
        print(f"\tBefore user - Group id: {results1}")
        # orginal_data["user_data"].append(result[0])

        print(f"RESULTS1: {results1}")
        results1.remove(int(group_id))
        user_document = {"user_id": user_id, "group_id": results1}
        ins_by_index(INDEX1,user_document,user_id)
    
        result = search_by_index(INDEX1,"user_id",user_id)
        check_group_id=result[0]['group_id']
        print(f"\tAfter user -Group id: {check_group_id}")
        # updated_data["user_data"].append(result[0])

    
    response = {"message": "group removed","input":input_data,"deleted_data":deleted_data}
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }


