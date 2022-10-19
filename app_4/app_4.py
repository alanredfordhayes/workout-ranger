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
    api_resource = 'blogs'
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

def retrieves_a_list_of_all_articles_from_a_blog(blog_id):
    'curl -X GET "https://your-development-store.myshopify.com/admin/api/2022-10/blogs/241253187/articles.json?since_id=134645308" -H "X-Shopify-Access-Token: {access_token}"'
    text_secret_data = get_secret()
    workoutranger_shopify_admin_api_access_token = text_secret_data['workoutranger_shopify_admin_api_access_token']
    store_name = text_secret_data['store_name']
    api_resource = 'blogs/'
    
    url = 'https://' + store_name + '.myshopify.com/admin/api/2022-07/' + api_resource + blog_id + "/articles.json"
    r = http.request('GET', 
                     url,
                     headers={
                         'Content-Type' : 'application/json',
                          'X-Shopify-Access-Token' : workoutranger_shopify_admin_api_access_token
                     }
    )
    articles = json.loads(r.data.decode('utf-8'))
    return articles

def main():
    blogs = retrieve_a_list_of_all_blogs()
    list_of_articles = []
    for blog in blogs:
        blog_id = blog['id']
        blog_handle = blog['handle']
        blog_title = blog['title']
        blog_updated_at = blog['updated_at']
        blog_commentable = blog['commentable']
        blog_feedburner = blog['feedburner']
        blog_feedburner_location = blog['feedburner_location']
        blog_created_at = blog['created_at']
        blog_template_suffix = blog['template_suffix']
        blog_tags = blog['tags']
        blog_admin_graphql_api_id = blog['admin_graphql_api_id']
        
        articles = retrieves_a_list_of_all_articles_from_a_blog(blog_id)
        return articles

def lambda_handler(event, context):
    t = main()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
        'output' : t
    }
