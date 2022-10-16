import json
import urllib3
import boto3
import base64
from botocore.exceptions import ClientError
import os

def processing_messages():
    QueueName = os.environ['QueueName']
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=QueueName)
    messages = queue.receive_messages()
    return messages
    

def lambda_handler(event, context):
    output = processing_messages()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
        'output' : s
    }