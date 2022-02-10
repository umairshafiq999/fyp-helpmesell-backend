from celery import shared_task
from .models import *
import xlrd


@shared_task
def LocalSellerFileUpload(request):
    file = request.FILES['ls_product_file']
    fileRead = xlrd.open_workbook(file)

    fileSheet = fileRead.sheet_by_index(0)

    for row in fileSheet.rows:
        try:
            product = Product.objects.get(product_name=row.value['product_name'])
            Price.objects.create(
                product_price=row.value['product_price'],
            )
        except Product.DoesNotExist:
            Product.objects.create(
                product_name=row.value(['product_name'])

            )
            Price.objects.create(
                product_price=row.value(['product_price'])
            )
            return None

