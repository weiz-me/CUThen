# This file is designed for the lambda function to handle group invites
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

def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)
    

def lambda_handler(event, context):
    # TODO implement
    print(event)
    print(context)

    user_data = event['body']
    user_data = json.loads(user_data)
    user_id = user_data["user_id"]
    accepted_inv_id = user_data["accepted_inv_id"]
    accept = user_data["accept"]

    # input (placehodler)
    # user_id = 3
    # accepted_inv_id = 2
    # accept = 1
    # pending_inv_ids = [1,2]
    
    
    opensearch_client = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
    }],
                        http_auth=get_awsauth(REGION, 'es'),
                        use_ssl=True,
                        verify_certs=True,
                        connection_class=RequestsHttpConnection)
                        
    #delete all existing data
    
    # # Delete all documents in the specified index
    delete_query = {
        "query": {
            "match_all": {}
        }
    }
    
    opensearch_client.delete_by_query(index=INDEX1, body=delete_query, refresh=True)
    opensearch_client.delete_by_query(index=INDEX2, body=delete_query, refresh=True)
    opensearch_client.delete_by_query(index=INDEX3, body=delete_query, refresh=True)
    
    # sample data
    rm_document = {"user_id": 3,"pending_inv_ids": [1,2,3]}
    rm_res = opensearch_client.index(index=INDEX3, id = 3, body=rm_document, refresh=True)

    rm_document = {"group_id": 2,"user_id": [1,2]}
    rm_res = opensearch_client.index(index=INDEX2, id = 2, body=rm_document, refresh=True)
    rm_document = {"user_id": 1,"group_id": [2]}
    rm_res = opensearch_client.index(index=INDEX1, id = 1, body=rm_document, refresh=True)
    rm_document = {"user_id": 2,"group_id": [2]}
    rm_res = opensearch_client.index(index=INDEX1, id = 2, body=rm_document, refresh=True)
    rm_document = {"user_id": 3,"group_id": []}
    rm_res = opensearch_client.index(index=INDEX1, id = 3, body=rm_document, refresh=True)
    
    q3 = {
        "query": {
            "query_string": {
              "query": user_id,
                "fields": ["user_id"]
                }
            }
        }
    res3 = opensearch_client.search(index=INDEX3, body=q3)
    
    hits = res3['hits']['hits']
    results3 = []
    for hit in hits:
        results3.append(hit['_source']['pending_inv_ids'])

    print(f"{results3 =}")
    pending_inv_ids =results3[0]


    # remove it from pending_invitation:
    print("remove it from pending_invitation:\n")
    pending_inv_ids.remove(accepted_inv_id)
    rm_document = {"pending_inv_ids": pending_inv_ids}
    rm_res = opensearch_client.index(index=INDEX3, id = user_id, body=rm_document, refresh=True)

    if accept:
        # adding it to user-group, group-user
        print("adding it to user-group, group-user")
        q1 = {
            "query": {
                "query_string": {
                  "query": user_id,
                    "fields": ["user_id"]
                    }
                }
            }
        res1 = opensearch_client.search(index=INDEX1, body=q1)
        
        hits = res1['hits']['hits']
        results1 = []
        for hit in hits:
            results1.append(hit['_source']['group_id'])
    
        results1=results1[0]
        print(f"{results1 =}")
        results1.append(accepted_inv_id)
        user_document = {"user_id": user_id, "group_id": results1}
        up_res1 = opensearch_client.index(index=INDEX1, id = user_id, body=user_document, refresh=True)
    
        
        q2 = {
            "query": {
                "query_string": {
                  "query": accepted_inv_id,
                    "fields": ["group_id"]
                    }
                }
            }
        res2 = opensearch_client.search(index=INDEX2, body=q2)
        
        hits = res2['hits']['hits']
        results2 = []
        for hit in hits:
            results2.append(hit['_source']['user_id'])
        
        results2=results2[0]
        print(f"{results2 =}")
        
        results2.append(user_id)
        group_document = {"group_id":accepted_inv_id, "user_id": results2}
        up_res1 = opensearch_client.index(index=INDEX2, id = accepted_inv_id, body=group_document, refresh=True)
    
    
    
        #
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


def query(term):
    q = {'size': 5, 'query': {'multi_match': {'query': term}}}

    client = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
    }],
                        http_auth=get_awsauth(REGION, 'es'),
                        use_ssl=True,
                        verify_certs=True,
                        connection_class=RequestsHttpConnection)

    res = client.search(index=INDEX, body=q)
    print(res)

    hits = res['hits']['hits']
    results = []
    for hit in hits:
        results.append(hit['_source'])

    return results