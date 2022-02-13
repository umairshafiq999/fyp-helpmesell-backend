from celery import shared_task
from .models import *
import pandas

@shared_task
def Hello():
    print("Hello World")


@shared_task
def LocalSellerFileUpload(file):
    print("Hello",file)
