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
    update_item_list({'user_id':user_data['user_id']},user_data,table="user_table")
    updated_Data = lookup_data({'user_id': user_data["currentUser"]}, table="user_table")

    response = {"message":"success","input": user_data , "updated_Data":updated_Data}
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
        res = response['Item']
        res['user_id'] = int(res['user_id']) 
        print(f"{res =}")
        return response['Item']
        
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

