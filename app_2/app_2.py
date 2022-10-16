import json
import urllib3
import boto3
import base64
from botocore.exceptions import ClientError
import os

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
        data = variant_dict['Data']['S']
        num = num + 1
        sm_post[num] = {
            'number' : num,
            'title' : item['title']['S'],
            'id' : item['id']['N'],
            'image' : img_dict['Item']['src']['S']
        }
        
        send_messages_sqs(sm_post[num], os.environ['QueueName'])
    return sm_post

def get_secret():
    secret_name = "placid"
    region_name = "us-east-1"
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)
    try: get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException': raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException': raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException': raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException': raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException': raise e
    else:
        if 'SecretString' in get_secret_value_response: 
            text_secret_data = json.loads(get_secret_value_response['SecretString']); return text_secret_data
        else: decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary']); return decoded_binary_secret

def lambda_handler(event, context):
    s = create_social_media_post()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
        'output' : s
    }