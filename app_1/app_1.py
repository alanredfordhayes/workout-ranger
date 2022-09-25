import json
import boto3
import base64
from botocore.exceptions import ClientError

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
            text_secret_data = json.loads(get_secret_value_response['SecretString']); workoutranger_shopify_admin_api_access_token = text_secret_data['workoutranger_shopify_admin_api_access_token']; return workoutranger_shopify_admin_api_access_token
        else: decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary']); return decoded_binary_secret

def lambda_handler(event, context):
    s = get_secret()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
