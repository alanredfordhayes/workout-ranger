import json
from re import template
import requests
import base64
import time
from collections import OrderedDict
import boto3
import urllib3
from urllib.parse import urlencode
from botocore.exceptions import ClientError
import openai

spotify_api = 'https://api.spotify.com/v1/'
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

def get_access_token():
    text_secret_data = get_secret("workout_ranger_spotify_shopify")
    client_id = text_secret_data['client_id']
    client_secret = text_secret_data['client_secret']
    b64Val = base64.b64encode((client_id + ":" + client_secret).encode("ascii")).decode()
    Authorization = 'Basic ' + b64Val
    data = {'grant_type' : 'client_credentials'}
    headers= {'Authorization' : Authorization, 'Content-Type' : 'application/x-www-form-urlencoded'}
    url = 'https://accounts.spotify.com/api/token'
    response = requests.post( url, headers=headers, data=data).json()
    time.sleep(0.1)
    return response['access_token']

def shopify_get(access_token, url):
    Authorization = 'Bearer ' + access_token
    headers = {'Authorization' : Authorization, 'Content-Type' : 'application/json'}
    response = requests.get(url=url, headers=headers).json()
    time.sleep(0.1)
    return response

def get_new_releases(access_token):
    url = 'https://api.spotify.com/v1/browse/new-releases'
    Authorization = 'Bearer ' + access_token
    headers = {'Authorization' : Authorization, 'Content-Type' : 'application/json'}
    response = requests.get(url=url, headers=headers).json()
    time.sleep(0.1)
    return response['albums']["items"]

def get_album(id, access_token):
    url = 'https://api.spotify.com/v1/albums/' + id
    response = shopify_get(access_token, url)
    return response

def get_tracks_audio_analysis(id, access_token):
    url = spotify_api + 'audio-analysis/'  + id
    response = shopify_get(access_token, url)
    return response

def get_tracks_audio_features(id, access_token):
    url = spotify_api + 'audio-features/'  + id
    response = shopify_get(access_token, url)
    return response

def get_tracks(id, access_token):
    url = spotify_api + 'tracks/'  + id
    response = shopify_get(access_token, url)
    return response

def get_playlist(id, access_token):
    url = spotify_api + 'playlists/'  + id
    response = shopify_get(access_token, url)
    return response

def get_playlist(id, access_token):
    url = spotify_api + 'playlists/'  + id
    response = shopify_get(access_token, url)
    return response

def add_items_to_playlist(id, access_token, data):
    url = spotify_api + 'playlists/'  + id + '/tracks'
    Authorization = 'Bearer ' + access_token
    headers = {'Authorization' : Authorization, 'Content-Type' : 'application/json'}
    data = { 'uris' : data }
    response = requests.post( url, headers=headers, data=data).json()
    time.sleep(0.1)
    return response

def songs_from_new_releases(access_token):
    songs_to_workout = []
    new_releases = get_new_releases(access_token=access_token)
    for albmum_item in new_releases:
        if albmum_item['album_type'] == 'single':
            album = get_album(id=albmum_item['id'], access_token=access_token)
            album_track_items_list = album['tracks']['items']
            for item in album_track_items_list:
                tracks_audio_features = get_tracks_audio_features(id = item['id'], access_token=access_token)
                if tracks_audio_features != {'error': {'status': 404, 'message': 'analysis not found'}}:
                    if tracks_audio_features['danceability'] >= 0.8:
                        if tracks_audio_features['energy'] >= 0.8:
                            songs_to_workout.append(item['id']) 
    return songs_to_workout

def songs_from_playlist(access_token, id):
    songs_to_workout = []
    playlist = get_playlist(id=id, access_token=access_token) 
    for playlist_item in playlist['tracks']['items']:
        track_id = playlist_item['track']['id']
        tracks_audio_features = get_tracks_audio_features(id = track_id, access_token=access_token)
        if tracks_audio_features != {'error': {'status': 404, 'message': 'analysis not found'}}:
            if tracks_audio_features['danceability'] >= 0.8:
                if tracks_audio_features['energy'] >= 0.7:
                    songs_to_workout.append(track_id)
    return songs_to_workout 

def create_image (img_1, img_2, img_3, img_4, template):
    text_secret_data = get_secret("placid")
    token = text_secret_data['placid_token']
    encoded_body = json.dumps( { "create_now": True, "layers": { "img_1": { "image": img_1 }, "img_2": { "image": img_2 }, "img_3": { "image": img_3 }, "img_4": { "image": img_4 } } } )
    url = 'https://api.placid.app/api/rest/' + template
    authorization = 'Bearer ' + token
    r = http.request('POST', url , headers={'Content-Type': 'application/json', 'Authorization': authorization }, body=encoded_body)
    return(r.data.decode('utf-8'))

def generateSocialMediaPost(prompt1):
    text_secret_data = get_secret("openai")
    openai.api_key = text_secret_data['secret_key']
    response = openai.Completion.create(
        engine="davinci-instruct-beta-v3", temperature=0.7, max_tokens=100, top_p=1, frequency_penalty=0,presence_penalty=0,
        prompt="Generate a social media to promote the Ranger Radio playlist on spotify featuring these artists: {}.".format(prompt1)
    )
    return response['choices'][0]['text']

def generateHastags(prompt1):
    text_secret_data = get_secret("openai")
    openai.api_key = text_secret_data['secret_key']
    response = openai.Completion.create(
        engine="davinci-instruct-beta-v3", temperature=0.6, max_tokens=100, top_p=1, frequency_penalty=0, presence_penalty=0,
        prompt="Generate hashtags for this social media post: {}".format(prompt1),
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
    encoded_args = urlencode({'image_url' : image_url,'is_carousel_item' : 'true','access_token' : instagram_access_token})
    url = facebook_api + instagram_business_account_id + '/media?' + encoded_args
    r = http.request('POST', url )
    creation_id = json.loads(r.data.decode('utf-8'))
    creation_id = creation_id['id']
    return creation_id

def instagram_carousel_container(facebook_api, instagram_business_account_id, instagram_access_token, songs_to_post):
    sorted_songs_to_post = OrderedDict(sorted(songs_to_post.items(), reverse=True))
    sorted_song_to_post_keys = sorted_songs_to_post.keys()
    image_urls = []
    placid_images = {}
    artists = []
    caption_tracks = []
    count = 0
    for key in sorted_song_to_post_keys:
        count = count + 1
        placid_images[count] = sorted_songs_to_post[key]['track_images']
        artists.append(sorted_song_to_post_keys[key]['track_artists'])
        caption_track = sorted_song_to_post_keys[key]['track_name'] + ' by ' + sorted_song_to_post_keys[key]['track_artists'] + ', Listen Here: ' + sorted_song_to_post_keys[key]['track_external_urls']
        caption_tracks.append(caption_track)
    img_1 = placid_images[1]
    img_2 = placid_images[2]
    img_3 = placid_images[3]
    img_4 = placid_images[4]
    template = 'tuebewt1a'
    placid_create_image = create_image (img_1, img_2, img_3, img_4, template)
    title = ', '.join(artists)
    placid_image_url = placid_create_image['image_url']
    image_urls.insert(0, placid_image_url)
    creation_ids = []
    for image_url in image_urls:
        creation_id = instagram_media_container(facebook_api, instagram_business_account_id, instagram_access_token, image_url)
        creation_ids.append(creation_id)
    children = '%2C'.join(creation_ids)
    caption_track = '\n'.join(caption_track)
    caption = generateSocialMediaPost(title)
    caption = caption + generateHastags(caption)
    caption = caption +  "\n\n" + caption_track + "\n\nhttps://wwww.workoutranger.com" + "\nRanger Radio: https://open.spotify.com/playlist/5YAAetoRA0Z2ty3OkGspxM" 
    encoded_args = urlencode({'caption' : caption, 'media_type' : 'CAROUSEL', 'access_token' : instagram_access_token})
    encoded_args = 'children=' + children + '&' + encoded_args 
    url = facebook_api + instagram_business_account_id + '/media?' + encoded_args
    r = http.request('POST', url )
    data = json.loads(r.data.decode('utf-8'))
    data = data['id']
    return data

def instagram_media_publish(facebook_api, instagram_business_account_id, creation_id, instagram_access_token):
    encoded_args = urlencode({'creation_id' : creation_id, 'access_token' : instagram_access_token})
    url = facebook_api + instagram_business_account_id + '/media_publish?' + encoded_args
    r = http.request('POST', url )
    data = json.loads(r.data.decode('utf-8'))
    data = data['id']
    return data

def main():
    access_token = get_access_token()
    songs_to_workout = []
    top_songs_usa = '37i9dQZEVXbLp5XoPON0wI'
    top_songs_global = '37i9dQZEVXbNG2KDcFcKOF'
    viral_50_usa = '37i9dQZEVXbKuaTI1Z1Afx'
    viral_50_global = '37i9dQZEVXbLiRSasKsNU9'
    new_music_friday = '37i9dQZF1DX4JAvHpjipBk'
    try: songs_to_workout.extend(songs_from_new_releases(access_token=access_token))
    except: pass
    try: songs_to_workout.extend(songs_from_playlist(access_token=access_token, id=top_songs_usa))
    except: pass
    try: songs_to_workout.extend(songs_from_playlist(access_token=access_token, id=top_songs_global))
    except: pass
    try: songs_to_workout.extend(songs_from_playlist(access_token=access_token, id=viral_50_usa))
    except: pass
    try: songs_to_workout.extend(songs_from_playlist(access_token=access_token, id=viral_50_global))
    except: pass
    try: songs_to_workout.extend(songs_from_playlist(access_token=access_token, id=new_music_friday))
    except: pass
    songs_to_workout= [*set(songs_to_workout)]
    songs_to_post = {}
    for song in songs_to_workout:
        track = get_tracks(id=song, access_token=access_token)
        track_external_urls = track['external_urls']['spotify']
        track_artists = track['artists']
        track_images = track['album']['images'][2]['url']
        track_name = track['name']
        track_popularity = track['popularity']
        items = {}
        items['track_name'] = track_name
        artists_name = []
        for artist in track_artists:
            artists_name.append(artist['name'])
        items['track_artist'] = ', '.join(artists_name)
        items['track_external_urls'] = track_external_urls    
        items['track_images'] = track_images
        items['track_popularity'] = track_popularity
        songs_to_post[track_popularity] = items
    text_secret_data = get_secret("workout_ranger_instagram")
    facebook_page_id = text_secret_data['page_id']
    instagram_access_token = text_secret_data['access_token']
    facebook_api = 'https://graph.facebook.com/v15.0/'
    instagram_business_account_id = get_instagram_business_account_id(facebook_page_id, instagram_access_token)
    instagram_carousel_container_id = instagram_carousel_container(facebook_api, instagram_business_account_id, instagram_access_token, songs_to_post)
    instagram_media_id = instagram_media_publish(facebook_api, instagram_business_account_id, instagram_carousel_container_id, instagram_access_token)
    return instagram_media_id
    
def lambda_handler(event, context):
    t = main()
    print(t)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
    }
