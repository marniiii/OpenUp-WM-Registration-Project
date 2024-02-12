# tasks.py
from time import sleep
from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task

# imports for token and API
import json
from pip._vendor import requests
from datetime import datetime, timedelta, timezone
from personal.credentials import token, secret_key

# variables for API
last_token_generation_time = None
cred_url = 'https://openapi.it.wm.edu/auth/v1/login'
access_token = None
headers = None
url = ""



@shared_task()
def get_jsonData():
    global last_token_generation_time
    global access_token
    global headers
    global url

    if not is_token_valid():
        set_headers()
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



@shared_task()
def send_feedback_email_task(email_address, message):
    print("Inside of send_feedback_email")
    """Sends an email when the feedback form has been submitted."""
    send_mail(
        "Your Feedback",
        f"\t{message}\n\nThank you!",
        settings.EMAIL_HOST_USER,
        [email_address],
        fail_silently=False,
    )
