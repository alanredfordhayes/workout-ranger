import json
import urllib3
import boto3
import base64
from botocore.exceptions import ClientError
import os
import ast

def scan_products_db():
    client = boto3.client('dynamodb')
    try: response = client.scan(TableName=os.environ['TableName1'])
    except: response = 'Could not scan items'
    return response

def send_messages_sqs(message, QueueName):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=QueueName)
    response = queue.send_message(MessageBody=str(message))

def create_social_media_post():
    client = boto3.client('dynamodb')
    product_list = scan_products_db()
    product_list_items = product_list['Items']
    product_list_count = product_list['Count']
    product_list_scannedcount = product_list['ScannedCount']
    product_list_responseMetadata = product_list['ResponseMetadata']
    sm_post = {}
    num = 0
    for item in product_list_items: 
        img_dict = client.get_item(TableName=os.environ['TableName5'],Key={'product_id': {'N': str(item['id']['N']) } } )
        variant_dict = client.get_item(TableName=os.environ['TableName4'],Key={'product_id': {'N': str(item['id']['N']) } } )
        data = ast.literal_eval(variant_dict['Item']['Data']['S'].replace("'", '"'))
        variants = []
        for d in data:
            if len(d['variant_ids']) >=1: variants.append(d['src'])
        num = num + 1
        sm_post[num] = {
            'number' : num,
            'title' : item['title']['S'],
            'id' : item['id']['N'],
            'image' : img_dict['Item']['src']['S'],
            'variants' : ", ".join(variants)
        }
        
        send_messages_sqs(sm_post[num], os.environ['QueueName'])
    return sm_post

def lambda_handler(event, context):
    s = create_social_media_post()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
        'output' : s
    }