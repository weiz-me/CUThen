import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import json

def lambda_handler(event, context):
    # uni is the primary/paritition key
    # note they all have unique attributes
    print(event)
    user_data = event['body']
    user_data = json.loads(user_data)

    print(f"{user_data}")

    # user_data = {
    #         'user_id': 1,
    #         'first_name': 'Timothy',
    #         'last_name': 'Wang',
    #         'uni': 'tjw2145',
    #         'email': 'tjw2145@columbia.edu',
    #         'hobbies': 'none',
    #         'major': 'none',
    #         'school': 'none',
    #         'academic_interests': 'none',
    #         'class_schedule': 'none',
    #         'exam_schedule': 'none',
    #         'phone_number': 'none',
    #         'zipcode': 'none'
    #     }

    update_item_list({'user_id':user_data['user_id']},user_data,table="user_table")
    lookup_data({'user_id': 1}, table="user_table")

    # 4
    # delete_item({'uni': 'xx777'})


    resp = {
            'statusCode': 200,
            'body': "profile updated"
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
        print(response['Item'])
        return response['Item']
        
def update_item_list(key, feature_dict, db=None, table='6998Demo'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    
    responses = "Update feature :"
    # change student location
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
        print(response)
        responses += (" " +feature_name)
    print(f"{responses =}")
    return responses