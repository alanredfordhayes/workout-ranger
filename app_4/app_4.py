from cgitb import text
from email import header
import json
import urllib3
import resource
import boto3
import base64
import os
from botocore.exceptions import ClientError

http = urllib3.PoolManager()

def get_secret():
    secret_name = "workoutranger_shopify_admin_api_access_token"
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

def retrieve_a_list_of_all_blogs():
    text_secret_data = get_secret()
    workoutranger_shopify_admin_api_access_token = text_secret_data['workoutranger_shopify_admin_api_access_token']
    store_name = text_secret_data['store_name']
    api_resource = 'products'
    url = 'https://' + store_name + '.myshopify.com/admin/api/2022-07/' + api_resource + '.json'
    r = http.request('GET', 
                     url,
                     headers={
                         'Content-Type' : 'application/json',
                          'X-Shopify-Access-Token' : workoutranger_shopify_admin_api_access_token
                     }
    )
    blogs = json.loads(r.data.decode('utf-8'))
    return blogs

def lambda_handler(event, context):
    t = retrieve_a_list_of_all_blogs()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
        'output' : t
    }