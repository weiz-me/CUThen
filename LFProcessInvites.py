# This file is designed for the lambda function to handle group invites
# in the project CUThen, the final project for COMSE6998_010_2023_3,
# Topics in Computer Science: Cloud Computing and Big Data.

import json

def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
