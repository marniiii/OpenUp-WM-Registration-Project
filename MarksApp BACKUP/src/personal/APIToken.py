import json
from pip._vendor import requests
from datetime import datetime, timedelta, timezone
from personal.credentials import token, secret_key

last_token_generation_time = None
cred_url = 'https://openapi.it.wm.edu/auth/v1/login'
access_token = None
headers = None
url = ""

def is_token_valid():

    #check pyJWT look at exp field and parse time to make sure its valid.
    #check exp to see when the token actually expires to make sure its robust
    #jwt.io
    
    global last_token_generation_time
    global access_token

    if access_token is None or last_token_generation_time is None:
        return False

    current_time = datetime.now()
    time_since_generation = current_time - last_token_generation_time

    if time_since_generation < timedelta(hours=0.5):
        return True
    else:
        return False


def get_access_token():
    global last_token_generation_time
    global access_token

    if is_token_valid():
        return access_token
    else:
        #Posting the user and pass for access token
        r = requests.post(cred_url, json = {
            "client_id": token,
            "secret_id": secret_key
        })
        data = json.loads(r.text)
        access_token = data["access_token"]
        return access_token
    
def set_headers():
    global headers
    if is_token_valid():
        return
    else:
        da_token = get_access_token()
        headers = {
            "accept": "text/json",
            "Authorization": "Bearer " + da_token
}
        
def get_jsonData():
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()  # Check if the request was successful (status code 200)
        jsonData = r.json()
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        jsonData = None
    except ValueError as e:
        print("Invalid JSON response:", e)
        jsonData = None
    return jsonData