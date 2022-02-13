from celery import shared_task
from .models import *
import pandas

@shared_task
def Hello():
    print("Hello World")


@shared_task
def LocalSellerFileUpload(file):
    print("Hello",file)
    fileSheet = pandas.read_excel(file, sheet_name=0, index_col=0, header=0)

    for row in fileSheet.iterrows():
        try:
            product = Product.objects.get(product_name=row[0])
            Price.objects.create(
                product=product,
                reference_site="shophive.com",
                product_price=row[1],
                min_price=20000,
                max_price=30000,
                offered_by=3
            )
        except Product.DoesNotExist:
            product = Product.objects.create(
                product_name=row[0],
                product_description='Great Phone',
                product_image="https://www.apple.com/newsroom/images/product/iphone/standard/Apple_announce-iphone12pro_10132020.jpg.landing-big_2x.jpg",
                min_price=20000,
                max_price=30000,
                offered_by=3

            )
            Price.objects.create(
                product_id=product.id,
                reference_site="shophive.com",
                product_price=row.value(['product_price']),

            )
