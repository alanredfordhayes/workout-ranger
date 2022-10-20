from cgitb import text
from email import header
import json
import urllib3
from urllib.parse import urlencode
import resource
import boto3
import base64
import os
import openai
from botocore.exceptions import ClientError

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

def retrieve_a_list_of_all_blogs():
    text_secret_data = get_secret("workoutranger_shopify_admin_api_access_token")
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
    print(blogs)
    return blogs

def retrieves_a_list_of_all_articles_from_a_blog(blog_id):
    'curl -X GET "https://your-development-store.myshopify.com/admin/api/2022-10/blogs/241253187/articles.json?since_id=134645308" -H "X-Shopify-Access-Token: {access_token}"'
    text_secret_data = get_secret("workoutranger_shopify_admin_api_access_token")
    workoutranger_shopify_admin_api_access_token = text_secret_data['workoutranger_shopify_admin_api_access_token']
    store_name = text_secret_data['store_name']
    api_resource = 'blogs/'
    
    url = 'https://' + store_name + '.myshopify.com/admin/api/2022-07/' + api_resource + str(blog_id) + "/articles.json"
    r = http.request('GET', 
                     url,
                     headers={
                         'Content-Type' : 'application/json',
                          'X-Shopify-Access-Token' : workoutranger_shopify_admin_api_access_token
                     }
    )
    articles = json.loads(r.data.decode('utf-8'))
    return articles
    
def create_image (title, subline, template):
    text_secret_data = get_secret("placid")
    token = text_secret_data['placid_token']
    encoded_body = json.dumps( { "create_now": True, "layers": { "title": { "text": title }, "subline": { "text": subline } } } )
    url = 'https://api.placid.app/api/rest/' + template
    authorization = 'Bearer ' + token
    r = http.request('POST', url , headers={'Content-Type': 'application/json', 'Authorization': authorization }, body=encoded_body)
    return(r.data.decode('utf-8'))

def generateSocialMediaPost(prompt1):
    text_secret_data = get_secret("openai")
    openai.api_key = text_secret_data['secret_key']
    response = openai.Completion.create(
      engine="davinci-instruct-beta-v3",
      prompt="Generate a social media to promote this blog: {}.".format(prompt1),
      temperature=0.7,
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
    
def instagram_media_container(facebook_api, instagram_business_account_id, instagram_access_token, image_url, caption):
    print(caption)
    encoded_args = urlencode(
        {
            'image_url' : image_url,
            'caption' : caption,
            'access_token' : instagram_access_token
        }
    )
    
    url = facebook_api + instagram_business_account_id + '/media?' + encoded_args
    r = http.request('POST', url )
    creation_id = json.loads(r.data.decode('utf-8'))
    print(creation_id)
    creation_id = creation_id['id']
    return creation_id

def instagram_media_publish(facebook_api, instagram_business_account_id, creation_id, instagram_access_token):
    encoded_args = urlencode({'creation_id' : creation_id, 'access_token' : instagram_access_token})
    url = facebook_api + instagram_business_account_id + '/media_publish?' + encoded_args
    r = http.request('POST', url )
    data = json.loads(r.data.decode('utf-8'))
    data = data['id']
    return data

def main():
    url = 'workoutranger.com/'
    blogs = retrieve_a_list_of_all_blogs()
    blogs = blogs['blogs']
    post_article_title = None
    post_article_url = None
    post_article_tags = None
    post_date = '2022-10-19T11:19:37-04:00'
    template = 's4nnaneym'
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
        url = url + blog_title.lower() + '/'
        
        articles = retrieves_a_list_of_all_articles_from_a_blog(blog_id)
        articles = articles['articles']
        for article in articles:
            article_id = article["id"]
            article_title = article["title"]
            article_created_at = article["created_at"]
            article_body_html = article["body_html"]
            article_blog_id = article["blog_id"]
            article_author = article["author"]
            article_user_id = article["user_id"]
            article_published_at = article["published_at"]
            article_updated_at = article["updated_at"]
            article_summary_html = article["summary_html"]
            article_template_suffix = article["template_suffix"]
            article_handle = article["handle"]
            article_tags = article["tags"]
            article_admin_graphql_api_id = article["admin_graphql_api_id"]
            url = url + article_title.lower().replace(' ','-')
            if article_published_at > post_date:
                post_date = article_published_at
                post_article_title = article_title
                post_article_url = url
                article_tags = '#' + article_tags.replace(', ',', #')
                article_tags = article_tags.replace(' ','')
                article_tags = article_tags.replace(',',', ')
                post_article_tags = article_tags
                
    placid_create_image = json.loads(create_image (post_article_title, post_article_url, template))
    prompt1 = post_article_title + ' ' + post_article_tags
    caption = generateSocialMediaPost(prompt1)
    caption = caption + "\n\n" + post_article_tags + "\n\nworkoutranger.com" + "\n" + post_article_url
    placid_image_url = placid_create_image['image_url']
    text_secret_data = get_secret("workout_ranger_instagram")
    facebook_page_id = text_secret_data['page_id']
    instagram_access_token = text_secret_data['access_token']
    facebook_api = 'https://graph.facebook.com/v15.0/'
    instagram_business_account_id = get_instagram_business_account_id(facebook_page_id, instagram_access_token)
    creation_id = instagram_media_container(facebook_api, instagram_business_account_id, instagram_access_token, placid_image_url, caption)
    instagram_media_id = instagram_media_publish(facebook_api, instagram_business_account_id, creation_id, instagram_access_token)
    return instagram_media_id

def lambda_handler(event, context):
    t = main()
    print(t)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
    }
