from celery import shared_task
from .models import *
import xlrd


@shared_task
def LocalSellerFileUpload():
    print("Hello World")
