# This file is designed for the lambda function to make new groups
# in the project CUThen, the final project for COMSE6998_010_2023_3,
# Topics in Computer Science: Cloud Computing and Big Data.

import json

def lambda_handler(event, context):
    print(event)
    # FOR TESTING ONLY
    dummy_response = {
        "groupId": 3,
        "groupLeader": {
            "userId": "1",
            "userName": "test name",
            "userFeatures": []
        },
        "groupMembers": [{
            "userId": "2",
            "userName": "test name 1",
            "userFeatures": []
        }]
    }
    return {
        'statusCode': 200,
        'body': json.dumps(dummy_response)
    }