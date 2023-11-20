import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import json
from boto3.dynamodb.conditions import Key, Attr



def lambda_handler(event, context):
    # uni is the primary/paritition key
    # note they all have unique attributes

    print(event)
    # body json format
    update_data = {
            'user_id': 1,
            'first_name': 'Timothy',
            'last_name': 'Wang',
            'uni': 'tjw2145',
            'email': 'tjw2145@columbia.edu',
            'hobbies': 'test',
            'major': 'CS',
            'school': 'test',
            'academic_interests': 'none',
            'class_schedule': 'none',
            'exam_schedule': 'none',
            'phone_number': 'none',
            'zipcode': 'none'
        }
    
    # # 1
    # insert_data(user_data, table="user_table")
    # insert_data(messages_data, table="chat_table")
    # 2
    # lookup_data({'user_id': 1}, table="user_table")
    # lookup_chat(1)
    # 3
    # update_item({'uni': 'xx777'}, 'Canada')
    update_item_list({'user_id':update_data['user_id']},update_data,table="user_table")
    lookup_data({'user_id': 1}, table="user_table")

    # 4
    # delete_item({'uni': 'xx777'})

    return


def insert_data(data_list, db=None, table='user_table'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    # overwrite if the same index is provided
    for data in data_list:
        response = table.put_item(Item=data)
    print('@insert_data: response', response)
    return response


def lookup_data(key, db=None, table='user_table'):
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
        
        
def lookup_chat(key, db=None, table='chat_table'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)

    try:
        # response = table.query(
        #     IndexName='chat_id-index',
        #     KeyConditionExpression=Key('chat_id').eq(key)
        #     )
        response = table.get_item(Key={'chat_id': 1})
        print(f"{response =}")
    except ClientError as e:
        print('Error', e.response['Error']['Message'])
    else:
        print(response['Item'])
        return response['Item']


def update_item(key, feature, db=None, table='user_table'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    
    
    # change student location
    response = table.update_item(
        Key=key,
        UpdateExpression="set #feature=:f",
        ExpressionAttributeValues={
            ':f': feature
        },
        ExpressionAttributeNames={
            "#feature": "from"
        },
        ReturnValues="UPDATED_NEW"
    )
    print(response)
    return response

def update_item_list(key, feature_dict, db=None, table='user_table'):
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


def delete_item(key, db=None, table='user_table'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    try:
        response = table.delete_item(Key=key)
    except ClientError as e:
        print('Error', e.response['Error']['Message'])
    else:
        print(response)
        return response
