from celery import shared_task
from .models import *
from .views import *
import pandas
from django.conf import settings
import requests
import html5lib
from bs4 import BeautifulSoup

@shared_task
def Hello():
    print("Hello World")


@shared_task
def LocalSellerFileUpload(file):
    fileSheet = pandas.read_excel(file, sheet_name=0, index_col=0, header=0)

    for row in fileSheet.iterrows():
        try:
            product = Product.objects.get(product_name=row[0])
            Price.objects.create(
                product=product,
                reference_site="shophive.com",
                product_price=row[1]
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
                product_price=row[1]

            )
    # print("Hello", file)

@shared_task
def ShopHiveScraper(url):
    r = requests.get(url)
    htmlContent = r.content
    # print(htmlContent)
    soup = BeautifulSoup(htmlContent, 'html.parser')
    # print(soup.prettify)
    title = soup.title
    # print(title)

    # print(urlList)
    for x in range(1, 30):
        urlList = soup.find_all("li", class_="item-inner")
        for li in urlList:
            try:
                name = li.find('h3').text
            except:
                name = ""
            try:
                price = li.find('span', class_='price-container').text
            except:
                price = ""
            try:
                image = li.find('img')
            except:
                image = ""

            row = [name, price, image]
            print(row)

            try:
                product = Product.objects.get(product_name=row[0])
                Price.objects.create(
                    product=product,
                    reference_site="shophive.com",
                    product_price=row[1].replace('Special Price','').replace(' ','')
                )
            except Product.DoesNotExist:
                product = Product.objects.create(
                    product_name=row[0],
                    product_description='Great Phone',
                    product_image= row[2]['src']

                )
                Price.objects.create(
                    product_id=product.id,
                    reference_site="shophive.com",
                    product_price=row[1].replace('Special Price','').replace(' ','')

                )





