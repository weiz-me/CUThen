
import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta

def lambda_handler(event, context):
    print(event)

    # input_data = {
    #     "send": 1,
    #     "group_id": 1,
    #     "user_id": 1,
    #     "message":"hello, testing, testing"
    # }
    
    input_data = event['body']
    input_data = json.loads(input_data)
    
    send = input_data['send']
    # mock database
    # messages_data = [
    #     {'chat_id': 1, 'group_id': 1, 'user_id': 1, 'message': "Hello, it's Tim.", 'time': datetime.now().isoformat()},
    #     {'chat_id': 2, 'group_id': 1, 'user_id': 2, 'message': "Hi, it's Chengyu.", 'time': (datetime.now() + timedelta(minutes=1)).isoformat()},
    #     {'chat_id': 3, 'group_id': 1, 'user_id': 3, 'message': "Hi, It's Wei.", 'time': (datetime.now() + timedelta(minutes=2)).isoformat()}
    # ]
    # insert_data(messages_data, table="chat_table")

    if send:
        group_id = input_data['group_id']
        user_id = input_data['user_id']
        message = input_data['message']

        
        
        print("1. inserting into database")
        messages_data = [
            {'chat_id': 5, 'group_id': group_id, 'user_id': user_id, 'message': message, 'time': (datetime.now()).isoformat()}
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

