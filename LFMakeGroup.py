# This file is designed for the lambda function to make new groups
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

    # # mock input data
    # input_data = {
    #     "master_user_id":1,
    #     "guest_user_id":2,
    # }

    # TODO implement
    print(f"{event = }")
    print(f"{context = }")

    input_data = event['body']
    input_data = json.loads(input_data)

    master_user_id = input_data["groupLeader"]
    guest_user_id = input_data["groupLeader"]
    opensearch_client = opensearch_init()

    # generate group_id
    rm_document = {"type": "group_id", "max":1}
    rm_res = opensearch_client.index(index=INDEX0, id = 1, body=rm_document, refresh=True)


    print("1. getting groupid and update")
    result = search_by_index(INDEX0,"type","group_id")
    print(f"\t{result = }")
    if len(result) == 0:
        group_id = 1
    else:
        group_id = result[0]['max'] + 1
        print(f"UPDATED: {group_id}")
    user_document = {"max": group_id, "type":"group_id"}
    print(f"\t{user_document = }")
    ins_by_index(INDEX0,user_document,1)
    print(f"{group_id = }")

    # adding it to user-group, group-user
    orginal_data={}
    updated_data={}
    print("2. adding it to user-group, group-user")
    result = search_by_index(INDEX1,"user_id",master_user_id)
    results1=result[0]['group_id']
    print(f"\tBefore user - Group id: {results1}")
    orginal_data["orginal_master_user_group_id"]=results1

    results1.append(group_id)
    user_document = {"user_id": master_user_id, "group_id": results1}
    if master_user_id not in results1:
        ins_by_index(INDEX1,user_document,master_user_id)

    
    result = search_by_index(INDEX1,"user_id",master_user_id)
    check_group_id=result[0]['group_id']
    print(f"\tAfter user -Group id: {check_group_id}")
    updated_data["user_master_group_id"]=check_group_id


    result = search_by_index(INDEX1,"user_id",guest_user_id)
    results1=result[0]['group_id']
    print(f"\tBefore user - Group id: {results1}")
    orginal_data["orginal_guest_user_group_id"]=results1

    results1.append(group_id)
    user_document = {"user_id": guest_user_id, "group_id": results1}
    ins_by_index(INDEX1,user_document,guest_user_id)

    result = search_by_index(INDEX1,"user_id",guest_user_id)
    check_group_id=result[0]['group_id']
    print(f"\tAfter user -Group id: {check_group_id}")
    updated_data["guest_user_group_id"]=check_group_id

    results2=[]
    print(f"\tBefore Group to user_id: {results2}")
    orginal_data["orginal_group_user_id"]=results2
    
    results2.append(guest_user_id)
    group_document = {"group_id":group_id, "leader_id": master_user_id,"user_id": results2}
    ins_by_index(INDEX2,group_document,group_id)

    result = search_by_index(INDEX2,"group_id",group_id)
    check_group_id=result[0]['user_id']
    print(f"\tAfter Group to user_id: {check_group_id}")
    updated_data["group_user_id"]=check_group_id
    updated_data = result[0]
    
    response = {"message":f"Group {group_id} created", "input":input_data, "new_data":updated_data}
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }



