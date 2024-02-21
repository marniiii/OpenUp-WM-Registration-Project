# tasks.py
from time import sleep
from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task

# imports for token and API
import json
from pip._vendor import requests
from datetime import datetime, timedelta
from personal.credentials import token, secret_key
import concurrent.futures


# variables for API
last_token_generation_time = None
cred_url = 'https://openapi.it.wm.edu/auth/v1/login'
access_token = None
headers = None
weekly_subject = None
weekly_term = None



@shared_task()
def get_classes(url):
    global last_token_generation_time
    global access_token
    global headers

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


@shared_task()
def get_subject_and_term(subject_url, term_url):
    global weekly_subject
    global weekly_term

    # Check if today is Monday (weekday() returns 0 for Monday or if No data is stored
    if datetime.today().weekday() == 0 or weekly_subject is None or weekly_term is None:
        set_headers()
        try:
            # Make the requests concurrently using threads to improve efficiency
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Submit the requests for subject and term data
                subj_future = executor.submit(requests.get, subject_url, headers=headers)
                term_future = executor.submit(requests.get, term_url, headers=headers)

                # Get the results of the requests
                subj_response = subj_future.result()
                term_response = term_future.result()

                # Check for errors in the responses
                subj_response.raise_for_status()
                term_response.raise_for_status()

                # Parse the JSON data from the responses
                subjJsonData = subj_response.json()
                termJsonData = term_response.json()

                # Store the retrieved data for the week
                weekly_subject = subjJsonData
                weekly_term = termJsonData

        except requests.exceptions.RequestException as e:
            print("Request failed:", e)
            subjJsonData = None
            termJsonData = None

        except ValueError as e:
            print("Invalid JSON response:", e)
            subjJsonData = None
            termJsonData = None

    else:
        subjJsonData = weekly_subject
        termJsonData = weekly_term

    return subjJsonData, termJsonData



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
