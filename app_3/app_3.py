import json
from re import template
import urllib3
from urllib.parse import urlencode
import boto3
import base64
from botocore.exceptions import ClientError
import os
import openai

http = urllib3.PoolManager()

def get_secret(secret_name):
    secret_name = secret_name
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
        
def generateSocialMediaPost(prompt1):
    text_secret_data = get_secret("openai")
    openai.api_key = text_secret_data['secret_key']
    response = openai.Completion.create(
      engine="davinci-instruct-beta-v3",
      prompt="Generate a funny social media post about how exercise relates to: {}.".format(prompt1),
      temperature=0.7,
      max_tokens=100,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )

    return response['choices'][0]['text']

def generateHastags(prompt1):
    text_secret_data = get_secret("openai")
    openai.api_key = text_secret_data['secret_key']
    response = openai.Completion.create(
      engine="davinci-instruct-beta-v3",
      prompt="Generate hashtags for this social media post: {}".format(prompt1),
      temperature=0.6,
      max_tokens=100,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )

    return response['choices'][0]['text']

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
            'is_carousel_item' : 'true',
            'access_token' : instagram_access_token
        }
    )
    
    url = facebook_api + instagram_business_account_id + '/media?' + encoded_args
    r = http.request('POST', url )
    creation_id = json.loads(r.data.decode('utf-8'))
    creation_id = creation_id['id']
    return creation_id

def instagram_carousel_container(creation_ids, facebook_api, instagram_business_account_id, instagram_access_token, title):
    children = '%2C'.join(creation_ids)
    caption = generateSocialMediaPost(title)
    caption = caption + generateHastags(caption)
    encoded_args = urlencode({'caption' : caption, 'media_type' : 'CAROUSEL', 'access_token' : instagram_access_token})
    encoded_args = 'children=' + children + '&' + encoded_args 
    url = facebook_api + instagram_business_account_id + '/media?' + encoded_args
    r = http.request('POST', url )
    data = json.loads(r.data.decode('utf-8'))
    data = data['id']
    return data

def instagram_media_publish(facebook_api, instagram_business_account_id, instagram_carousel_container_id, instagram_access_token):
    encoded_args = urlencode({'creation_id' : instagram_carousel_container_id, 'access_token' : instagram_access_token})
    url = facebook_api + instagram_business_account_id + '/media_publish?' + encoded_args
    r = http.request('POST', url )
    data = json.loads(r.data.decode('utf-8'))
    data = data['id']
    return data

def get_sqs_message():
    QueueName = os.environ['QueueName']
    client = boto3.client('sqs')
    response = client.get_queue_url(QueueName=QueueName)
    QueueUrl = response['QueueUrl']
    response = client.receive_message(QueueUrl=QueueUrl, AttributeNames=['SentTimestamp'], MaxNumberOfMessages=1, MessageAttributeNames=['All'], VisibilityTimeout=0, WaitTimeSeconds=0)
    return response

def create_image (title, img, template):
    text_secret_data = get_secret("placid")
    token = text_secret_data['placid_token']
    encoded_body = json.dumps( { "create_now": True, "layers": { "title": { "text": title }, "img": { "image": img, "image_viewport": "1200x1200" } } } )
    url = 'https://api.placid.app/api/rest/' + template
    authorization = 'Bearer ' + token
    r = http.request('POST', url , headers={'Content-Type': 'application/json', 'Authorization': authorization }, body=encoded_body)
    return(r.data.decode('utf-8'))

def processing_messages():
    item_range = range(1)
    image_urls = []
    messages = []
    for item in item_range:
        response = get_sqs_message()
        print(response)
        messages.append(response)
        
        Body = json.loads(response['Messages'][0]['Body'].replace("'", '"'))
        title = Body['title']
        img = Body['image']
        template = '1fcgfm1ks'
        variants = Body['variants'].split(", ")
        placid_create_image = json.loads(create_image(title, img, template))
        placid_image_url = placid_create_image['image_url']
        image_urls.append(placid_image_url)
        image_urls.extend(variants)
    
    #instagram 
    text_secret_data = get_secret("workout_ranger_instagram")
    facebook_page_id = text_secret_data['page_id']
    instagram_access_token = text_secret_data['access_token']
    facebook_api = 'https://graph.facebook.com/v15.0/'

    instagram_business_account_id = get_instagram_business_account_id(facebook_page_id, instagram_access_token)
    creation_ids = []
    for image_url in image_urls:
        creation_id = instagram_media_container(facebook_api, instagram_business_account_id, instagram_access_token, image_url)
        creation_ids.append(creation_id)
    instagram_carousel_container_id = instagram_carousel_container(creation_ids, facebook_api, instagram_business_account_id, instagram_access_token, title)
    instagram_media_id = instagram_media_publish(facebook_api, instagram_business_account_id, instagram_carousel_container_id, instagram_access_token)
    return instagram_media_id

def lambda_handler(event, context):
    output = processing_messages()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
        'output' : output
    }