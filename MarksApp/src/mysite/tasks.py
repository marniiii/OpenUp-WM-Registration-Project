# tasks.py
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_email_task():
    # Your email sending logic here
    send_mail('Subject', 'Message', 'from@example.com', ['to@example.com'])
