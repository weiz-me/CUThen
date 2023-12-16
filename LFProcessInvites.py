import json
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3


REGION = 'us-east-1'
HOST = 'search-cuthen-temp-5fyo5fvs7x7t2myle4ztwa7swa.us-east-1.es.amazonaws.com'
INDEX1 = 'user_to_group'
INDEX2 = 'group_to_user'
INDEX3 = 'user_to_inv'

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
    
    
    # mock input
    # user_data = {
    #     "user_id":3,
    #     "accepted_inv_id":2,
    #     "accept":1
    #     }

    # TODO implement
    print(f"{event = }")
    print(f"{context = }")

    user_data = event['body']
    user_data = json.loads(user_data)
    user_id = user_data["user_id"]
    accepted_inv_id = user_data["accepted_inv_id"]
    accept = user_data["accept"]
    
    print("0. Opening Opensearch client")
    opensearch_client = opensearch_init()
    # mock data
    # rm_document = {"user_id": 1,"group_id": [2]}
    # rm_res = opensearch_client.index(index=INDEX1, id = 1, body=rm_document, refresh=True)
    # rm_document = {"user_id": 2,"group_id": [2]}
    # rm_res = opensearch_client.index(index=INDEX1, id = 2, body=rm_document, refresh=True)
    # rm_document = {"user_id": 3,"group_id": []}
    # rm_res = opensearch_client.index(index=INDEX1, id = 3, body=rm_document, refresh=True)

    # rm_document = {"group_id": 2,"user_id": [1,2]}
    # rm_res = opensearch_client.index(index=INDEX2, id = 2, body=rm_document, refresh=True)
    
    # rm_document = {"user_id": 3,"pending_inv_ids": [1,2,3]}
    # rm_res = opensearch_client.index(index=INDEX3, id = 3, body=rm_document, refresh=True)
    
    
    print("1. Removing pending_inv_id")

    result = search_by_index(INDEX3,"user_id",user_id)
    pending_inv_ids =result[0]['pending_inv_ids']
    print(f"\tBefore pending_inv_id {pending_inv_ids}")
    orginal_pending = pending_inv_ids

    # remove it from pending_invitation:
    print("\tremove it from pending_invitation:\n")
    pending_inv_ids.remove(accepted_inv_id)
    document = {"user_id": user_id,"pending_inv_ids": pending_inv_ids}
    ins_by_index(INDEX3,document,user_id)

    result = search_by_index(INDEX3,"user_id",user_id)
    check_pending_inv_ids =result[0]['pending_inv_ids']
    print(f"\tAfter pending_inv_id {check_pending_inv_ids}")

    input_Data={"user_id":user_id,"accepted_inv_id":accepted_inv_id,"accept":accept}
    orginal_data={"orginal_pending_inv_ids":orginal_pending}
    updated_data={"pending_inv_ids":pending_inv_ids}
    if accept:
        # adding it to user-group, group-user
        print("2. adding it to user-group, group-user")

        result = search_by_index(INDEX1,"user_id",user_id)
        results1=result[0]['group_id']
        print(f"\tBefore user - Group id: {results1}")
        orginal_data["orginal_user_group_id"]=results1

        results1.append(accepted_inv_id)
        user_document = {"user_id": user_id, "group_id": results1}
        ins_by_index(INDEX1,user_document,user_id)
    
        result = search_by_index(INDEX1,"user_id",user_id)
        check_group_id=result[0]['group_id']
        print(f"\tAfter user -Group id: {check_group_id}")
        updated_data["user_group_id"]=check_group_id

        result = search_by_index(INDEX2,"group_id",accepted_inv_id)
        results2=result[0]['user_id']
        results3=result[0]['leader_id']
        print(f"\tBefore Group to user_id: {results2}")
        orginal_data["orginal_group_user_id"]=results2
        
        results2.append(user_id)
        group_document = {"group_id":accepted_inv_id, "leader_id":results3, "user_id": results2}
        ins_by_index(INDEX2,group_document,accepted_inv_id)
    
        result = search_by_index(INDEX2,"group_id",accepted_inv_id)
        check_group_id=result[0]['user_id']
        print(f"\tAfter user -Group id: {check_group_id}")
        updated_data["group_user_id"]=check_group_id

    response_data = {"message":"accept successful","input":user_data, "orginal_data":orginal_data, "updated_data":updated_data}
    return {
        'statusCode': 200,
        'body': json.dumps(response_data)
    }