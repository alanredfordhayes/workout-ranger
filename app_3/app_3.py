import json
import urllib3
from urllib.parse import urlencode
import boto3
import base64
from botocore.exceptions import ClientError
import os

http = urllib3.PoolManager()

def get_secret():
    secret_name = "workout_ranger_instagram"
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
        

def get_instagram_business_account_id(facebook_page_id, instagram_access_token):
    facebook_api = 'https://graph.facebook.com/v15.0/'
    url = facebook_api + facebook_page_id + '?fields=instagram_business_account&access_token=' + instagram_access_token
    r = http.request('GET', url)
    instagram_ids = json.loads(r.data.decode('utf-8'))
    instagram_business_account_id = instagram_ids['instagram_business_account']['id']
    return instagram_business_account_id

def instagram_media_container(facebook_api, instagram_business_account_id, instagram_access_token, image_url):
    encoded_args = urlencode(
        {
            'image_url' : image_url,
            'caption' : 'WorkoutRanger',
            'access_token' : instagram_access_token
        }
    )
    
    url = facebook_api + instagram_business_account_id + '/media?' + encoded_args
    r = http.request('POST', url )
    creation_id = json.loads(r.data.decode('utf-8'))
    creation_id = creation_id['id']
    return creation_id

def processing_messages():
    #sqs
    QueueName = os.environ['QueueName']
    client = boto3.client('sqs')
    response = client.get_queue_url(QueueName=QueueName)
    QueueUrl = response['QueueUrl']
    response = client.receive_message(QueueUrl=QueueUrl, AttributeNames=['SentTimestamp'], MaxNumberOfMessages=1, MessageAttributeNames=['All'], VisibilityTimeout=0, WaitTimeSeconds=0)
    Body = json.loads(response['Messages'][0]['Body'].replace("'", '"'))
    title = Body['title']
    print(title)

    #instagram 
    text_secret_data = get_secret()
    facebook_page_id = text_secret_data['page_id']
    instagram_access_token = text_secret_data['access_token']
    instagram_business_account_id = get_instagram_business_account_id(facebook_page_id, instagram_access_token)
    facebook_api = 'https://graph.facebook.com/v15.0/'
    image_url_1= 'https://s3-placid.s3.eu-central-1.amazonaws.com/production/rest-images/b3y0kkhnt/rest-e1ab7132136b4e94d547d64334a7b429-ruglxtfd.jpg'
    image_url_2 = 'https://s3-placid.s3.eu-central-1.amazonaws.com/production/rest-images/ysr4e4n8l/rest-8e3fca0d0b27038775977a8c92b053ea-esferi2w.jpg'
    image_urls = [image_url_1, image_url_2]
    creation_ids = str()
    for image_url in image_urls:
        creation_id = instagram_media_container(facebook_api, instagram_business_account_id, instagram_access_token, image_url)
        creation_ids = creation_ids + creation_id + '%'
    creation_ids = creation_ids.rstrip(creation_ids[-1])
    print(creation_ids)
    encoded_args = urlencode(
        {
            'media_type' : 'CAROUSEL',
            'children' : creation_ids,
            'access_token' : instagram_access_token
        }
    )
    
    url = facebook_api + instagram_business_account_id + '/media_publish?' + encoded_args
    r = http.request('POST', url )
    data = json.loads(r.data.decode('utf-8'))
    print(data)
    return 
    

def lambda_handler(event, context):
    output = processing_messages()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
        'output' : output
    }