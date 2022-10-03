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
        response = client.get_item(TableName=os.environ['TableName5'],Key={'id': item['id']['N']})
        num = num + 1
        sm_post[num] = {
            'number' : num,
            'title' : item['title']['S'],
            'id' : item['id']['N'],
            'image' : response
        }
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

def create_image (image, cta, price, title, token):
    http = urllib3.PoolManager()
    encoded_body = json.dumps(
        {
            "create_now": True,
            "layers": {
                "img": {
                    "image": image,
                    "image_viewport": "1200x1200"
                },
                "cta": {
                    "text": cta
                },
                "price": {
                    "text": price
                },
                "title": {
                    "text": title
                }
            }
        }
    )
    bearer_token = 'Bearer ' + token
    r = http.request('POST', 'https://api.placid.app/api/rest/b3y0kkhnt', headers={'Content-Type': 'application/json', 'Authorization': bearer_token }, body=encoded_body)
    return(r.data)

def lambda_handler(event, context):
    s = create_social_media_post()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
        'output' : s
    }