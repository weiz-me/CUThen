# This file is designed for the lambda function to delete groups
# in the project CUThen, the final project for COMSE6998_010_2023_3,
# Topics in Computer Science: Cloud Computing and Big Data.

import json

def lambda_handler(event, context):
    print(event)
    # FOR TESTING ONLY
    dummy_response = "TEST SUCCESS"
    return {
        'statusCode': 200,
        'body': json.dumps(dummy_response)
    }