from celery import shared_task
from .models import *
from .views import *
import pandas
from django.conf import settings
import requests
import html5lib
from bs4 import BeautifulSoup


def DataCleaning(product):
    product.product_name.replace('USA','') #Pakistani Stores Mobile Removals
    product.product_name.replace('Without PTA Approved', '')
    product.product_name.replace('(PTA Approved)', '')



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
                try:
                    Price.objects.get(product_id=product.id, reference_site="shophive.com")
                    pass
                except:
                    Price.objects.create(
                        product=product,
                        reference_site="shophive.com",
                        product_price=row[1].replace('Special Price', '').replace(' ', '')
                    )

            except Product.DoesNotExist:
                product = Product.objects.create(
                    product_name=row[0],
                    product_description='Great Phone',
                    product_image=row[2]['src']

                )
                Price.objects.create(
                    product_id=product.id,
                    reference_site="shophive.com",
                    product_price=row[1].replace('Special Price', '').replace(' ', '')

                )


@shared_task
def PakistaniStoresLaptopScraper(url):
    r = requests.get(url)
    htmlContent = r.content
    # print(htmlContent)
    soup = BeautifulSoup(htmlContent, 'html.parser')
    # print(soup.prettify)
    title = soup.title
    # print(title)
    for x in range(1, 30):
        url = "https://pakistanistores.com/prices/laptops-and-pc/laptops/dell?p=" + str(x)
        urlList = soup.find_all("li", class_="col-md-3 col-md-3 col-sm-6 col-xs-6")
        for li in urlList:
            try:
                name = li.find('h5').text
            except:
                name = ""
            try:
                price = li.find('div', class_="primary-color price").text
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
                try:
                    Price.objects.get(product_id=product.id, reference_site="pakistanistores.com")
                    pass
                except:
                    Price.objects.create(
                        product=product,
                        reference_site="pakistanistores.com",
                        product_price=row[1].replace('\n', '').replace(' ', '')
                    )
            except Product.DoesNotExist:
                product = Product.objects.create(
                    product_name=row[0],
                    product_description='Great Phone',
                    product_image=row[2]['data-src']

                )
                Price.objects.create(
                    product_id=product.id,
                    reference_site="pakistanistores.com",
                    product_price=row[1].replace('\n', '').replace(' ', '')

                )


@shared_task
def PakistaniStoresMobileScraper(url):
    r = requests.get(url)
    htmlContent = r.content
    # print(htmlContent)
    soup = BeautifulSoup(htmlContent, 'html.parser')
    # print(soup.prettify)
    title = soup.title
    # print(title)

    # print(urlList)
    for x in range(1, 30):
        url = "https://pakistanistores.com/products/iphone?p=" + str(x)
        urlList = soup.find_all("li", class_="col-md-3 col-md-3 col-sm-6 col-xs-6")
        for li in urlList:
            try:
                name = li.find('h5').text
            except:
                name = ""
            try:
                price = li.find('div', class_='primary-color price').text
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
                try:
                    Price.objects.get(product_id=product.id, reference_site="pakistanistores.com")
                    pass
                except:
                    Price.objects.create(
                        product=product,
                        reference_site="pakistanistores.com",
                        product_price=row[1].replace('\n', '').replace(' ', '')
                    )
            except Product.DoesNotExist:
                product = Product.objects.create(
                    product_name=row[0],
                    product_description='Great Phone',
                    product_image=row[2]['data-src']

                )
                Price.objects.create(
                    product_id=product.id,
                    reference_site="pakistanistores.com",
                    product_price=row[1].replace('\n', '').replace(' ', '')

                )
