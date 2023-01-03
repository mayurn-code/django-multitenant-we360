from .serializers import ClientSerializer
from celery import shared_task
from time import sleep

from config.sendemail import send_email

@shared_task()
def create_new_tenant(data):
    sleep(1)
    serializer = ClientSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return {"data":serializer.data, "status":201}
    return {"data":serializer.errors, "status":400}

@shared_task()
def send_mail_celery(email,encoded_token):
    sleep(1)
    send_email(email,encoded_token)
    