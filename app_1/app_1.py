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
        
def get_products():
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
    products = json.loads(r.data.decode('utf-8'))
    products = products['products']
    print(type)
    return products

def load_sup_db(suplist, tablename):
    client = boto3.client('dynamodb') 
    for p in suplist:
        Item = {}
        for key in p:
            if key == 'id': value = p[key]; value = str(value); Item[key] = {'N' : value}
            elif key == 'product_id': value = p[key]; value = str(value); Item[key] = {'N' : value}
        try: response = client.get_item(TableName=os.environ[tablename],Key={'id':{'S':p.id}})
        except: response = client.put_item(TableName=os.environ[tablename],Item=Item)
        
def load_sup_db_variants(suplist, tablename):
    client = boto3.client('dynamodb') 
    for p in suplist:
        Item = {}
        for key in p:
            if key == 'id': value = p[key]; value = str(value); Item[key] = {'N' : value}
            elif key == 'product_id': value = p[key]; value = str(value); Item[key] = {'N' : value}
            elif key == 'title': value = p[key]; value = str(value); Item[key] = {'S' : value}
            elif key == 'price': value = p[key]; value = str(value); Item[key] = {'S' : value}
        try: response = client.get_item(TableName=os.environ[tablename],Key={'id':{'S':p.id}})
        except: response = client.put_item(TableName=os.environ[tablename],Item=Item)

def load_image_db(img_dict, tablename):
    client = boto3.client('dynamodb') 
    Item = {}
    Item['id'] = { 'N' : str(img_dict['id'])}
    Item['product_id'] = { 'N' : str(img_dict['product_id'])}
    Item['src'] = { 'S' : str(img_dict['src'])}
    try: response = client.get_item(TableName=os.environ[tablename],Key={'id':{'S':img_dict.id}})
    except: response = client.put_item(TableName=os.environ[tablename],Item=Item)

def update_table():
    client = boto3.client('dynamodb')
    products = get_products()
    products_list = []
    for p in products:
        Item = {}
        for key in p:
            if key == 'id': Item[key] = {'N' : str(p[key])}
            elif key == 'variants': variants = p[key]; load_sup_db_variants(variants, 'TableName2')
            elif key == 'options': options = p[key]; load_sup_db(options, 'TableName3')
            elif key == 'images': images = p[key]; load_sup_db(images, 'TableName4')
            elif key == 'image': image = p[key]; load_image_db(image, 'TableName5')
            else: Item[key] = {'S' : p[key]}
        try: response = client.get_item(TableName=os.environ['TableName1'],Key={'id':{'S':p.id}})
        except: response = client.put_item(TableName=os.environ['TableName1'],Item=Item)
        products_list.append(response)
    return products_list                

def lambda_handler(event, context):
    t = update_table()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
        'output' : t
    }
