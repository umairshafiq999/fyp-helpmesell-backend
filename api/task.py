from celery import shared_task
from .models import *
import pandas
import requests
import nltk
import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from .constants import walmart_ids_list

def DataCleaningOfPakistaniStores(product, price):
    product.product_name.replace('USA', '')  # Pakistani Stores Mobile Removals
    product.product_name.replace('Without PTA Approved', '')
    product.product_name.replace('(PTA Approved)', '')
    price.product_price.replace('\n', '')


def DataCleaningOfShophive(price):
    price.product_price.replace('Special Price', '').replace(' ', '')


@shared_task
def LocalSellerFileUpload(file):
    fileSheet = pandas.read_excel(file, sheet_name=0, index_col=0, header=0)
    for row in fileSheet.iterrows():
        try:
            product = Product.objects.get(product_name=row[0])
            Price.objects.create(
                product=product,
                reference_site="Local Seller Data",
                product_price=[int(s) for s in str(row[1]).split() if s.isdigit()][0]
            )
        except Product.DoesNotExist:
            [category_name, subcategory_name] = row[0].split(" ", 1)
            product = Product.objects.create(
                product_name=row[0],
                product_description='Great Phone',
                product_image=GetImage(row[0]),
                min_price=20000,
                max_price=30000,
                offered_by=3,
                category_id=2 if row[0].lower() in ['Samsung', 'Apple'] else 1,
                category_name=subcategory_name[0:12]

            )
            Price.objects.create(
                product_id=product.id,
                reference_site="Local Seller Data",
                product_price=[int(s) for s in str(row[1]).split() if s.isdigit()][0]


            )


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
            if 'laptops' in url:
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
                    [category_name, subcategory_name] = row[0].split(" ", 1)
                    product = Product.objects.create(
                        product_name=row[0],
                        product_description='Great Phone',
                        product_image=GetImage(row[0]),
                        category_id=1,
                        category_name=subcategory_name[0:12]

                    )
                    Price.objects.create(
                        product_id=product.id,
                        reference_site="shophive.com",
                        product_price=row[1].replace('Special Price', '').replace(' ', '')

                    )
            if 'mobiles' or 'apple' in url:
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
                    [category_name,subcategory_name] = row[0].split(" ",1)
                    product = Product.objects.create(
                        product_name=row[0],
                        product_description='Great Phone',
                        product_image=GetImage(row[0]),
                        category_id=2,
                        category_name=subcategory_name[0:12]

                    )
                    Price.objects.create(
                        product_id=product.id,
                        reference_site="shophive.com",
                        product_price=row[1].replace('Special Price', '').replace(' ', '')

                    )


def GetImage(ProductName):
    url = 'https://www.google.com/search?q={0}&tbm=isch'.format(ProductName)
    content = requests.get(url).content
    soup = BeautifulSoup(content, 'lxml')
    ProductImage = soup.findAll('img')
    imgSrc = ''
    i=0
    for image in ProductImage:
        imgSrc = image.get('src')
        i = i + 1
        if(i >= 2):
            break
    return imgSrc

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
                [category_name, subcategory_name] = row[0].split(" ", 1)
                product = Product.objects.create(
                    product_name=row[0],
                    product_description='Great Phone',
                    product_image=row[2]['data-src'],
                    category_id=1,
                    category_name=subcategory_name[0:12]

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
                [category_name, subcategory_name] = row[0].split(" ", 1)
                product = Product.objects.create(
                    product_name=row[0],
                    product_description='Great Phone',
                    product_image=row[2]['data-src'],
                    category_id=2,
                    category_name=subcategory_name[0:12]

                )
                Price.objects.create(
                    product_id=product.id,
                    reference_site="pakistanistores.com",
                    product_price=row[1].replace('\n', '').replace(' ', '')

                )

@shared_task
def MegaPkScraper(url):
    r = requests.get(url)
    htmlContent = r.content
    # print(htmlContent)
    soup = BeautifulSoup(htmlContent, 'html.parser')
    # print(soup.prettify)
    title = soup.title
    # print(title)
    for x in range(1, 30):
        url = "https://www.mega.pk/laptop-dell/?p=" + str(x)
        urlList = soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-4 col-lg-3")
        for li in urlList:
            try:
                name = li.find('h3').text
            except:
                name = ""
            try:
                price = li.find('div', class_="cat_price").text
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
                    Price.objects.get(product_id=product.id, reference_site="mega.pk")
                    pass
                except:
                    Price.objects.create(
                        product=product,
                        reference_site="mega.pk",
                        product_price=row[1].replace('\n', '').replace(' ', '')
                    )
            except Product.DoesNotExist:
                [category_name, subcategory_name] = row[0].split(" ", 1)
                product = Product.objects.create(
                    product_name=row[0],
                    product_description='Great Phone',
                    product_image=row[2]['data-original'],
                    category_id=2,
                    category_name=subcategory_name[0:12]

                )
                Price.objects.create(
                    product_id=product.id,
                    reference_site="mega.pk",
                    product_price=row[1].replace('\n', '').replace(' ', '')

                )

@shared_task
def pull_reviews():
    url = "https://walmart.p.rapidapi.com/reviews/v2/list"
    product_list = list(Product.objects.filter().values('walmart_id', 'product_name', 'id').distinct())
    for product in product_list:
        if product['walmart_id'] == '':
            for walmart_const in walmart_ids_list:
                if walmart_const['product_name'].upper() in product['product_name'].upper():
                    Product.objects.filter(pk=product['id']).update(walmart_id=walmart_const['walmart_id'])
                    continue
    product_list = list(Product.objects.filter().exclude(walmart_id='').values('walmart_id', 'id').distinct())
    for product in product_list:
        querystring = {"usItemId": product['walmart_id'], "limit": "50", "page": "1", "sort": "relevancy"}
        headers = {
            "X-RapidAPI-Host": "walmart.p.rapidapi.com",
            "X-RapidAPI-Key": "26fb418dfbmsh1b4e826435e387dp118bb5jsn096722e71d21"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
        for review in json.loads(response.text)['data']['reviews']['customerReviews']:
            if review['reviewText'] and len(review['reviewText']) > 0:
                for product_walmart in Product.objects.filter(walmart_id=product['walmart_id']):
                    obj, created = ProductReview.objects.get_or_create(
                        product_id=product_walmart.id,
                        product_reviews=review['reviewText'],
                        review_type=3 if int(review['rating']) <= 2 else 2 if int(review['rating']) == 3 else 1
                    )
                    if created:
                        fetch_review_type.delay(review['reviewText'], 3 if int(review['rating']) <= 2 else 2 if int(review['rating']) == 3 else 1, product_walmart.id)


@shared_task
def fetch_review_type(review, review_type, product_id):
    TrainingData.objects.get_or_create(
        review_text=review,
        review_type=review_type
    )
    positive_reviews = list(TrainingData.objects.filter(review_type=1).values_list('review_text', 'review_type'))
    negative_reviews = list(TrainingData.objects.filter(review_type=3).values_list('review_text', 'review_type'))

    reviews = []

    for (words, sentiment) in positive_reviews + negative_reviews:
        words_filtered = [e.lower() for e in words.split() if len(e) >= 3]
        reviews.append((words_filtered, sentiment))

    def get_words_in_reviews(reviews):
        all_words = []
        for (words, sentiment) in reviews:
            all_words.extend(words)
        return all_words

    def get_word_features(wordlist):
        wordlist = nltk.FreqDist(wordlist)
        word_features = wordlist.keys()
        return word_features

    def extract_features(document):
        document_words = set(document)
        features = {}
        for word in word_features:
            features['contains(%s)' % word] = (word in document_words)
        return features

    word_features = get_word_features(get_words_in_reviews(reviews))
    training_set = nltk.classify.apply_features(extract_features, reviews)
    classifier = nltk.NaiveBayesClassifier.train(training_set)
    result = classifier.classify(extract_features(review.split()))
    print(result)
    if result == 1:
        try:
            product_review_stat = ProductReviewStats.objects.get(product_id=product_id)
            product_review_stat.positive = product_review_stat.positive + 1
            product_review_stat.save()
        except:
            product_review_stat = ProductReviewStats.objects.create(product_id=product_id)
            product_review_stat.positive =product_review_stat.positive + 1
            product_review_stat.save()
    elif result == 2:
        try:
            product_review_stat = ProductReviewStats.objects.get(product_id=product_id)
            product_review_stat.neutral =product_review_stat.neutral + 1
            product_review_stat.save()
        except:
            product_review_stat = ProductReviewStats.objects.create(product_id=product_id)
            product_review_stat.neutral = product_review_stat.neutral + 1
            product_review_stat.save()
    else:
        try:
            product_review_stat = ProductReviewStats.objects.get(product_id=product_id)
            product_review_stat.negative =product_review_stat.negative + 1
            product_review_stat.save()
        except:
            product_review_stat = ProductReviewStats.objects.create(product_id=product_id)
            product_review_stat.negative = product_review_stat.negative + 1
            product_review_stat.save()


@shared_task
def FetchWalmartIDs(product):
    option = webdriver.ChromeOptions()
    driver = webdriver.Chrome(
        executable_path=r'D:\BNU\Sem7\Project Part-2\Scraper2\chromedriver_win32\chromedriver.exe',
        options=option)
    driver.maximize_window()
    url = 'https://www.walmart.com/search?q='+ product
    driver.get(url)
    time.sleep(2)
    page1 = driver.page_source
    soup1 = BeautifulSoup(page1, 'lxml')
    url_list = soup1.find_all("a", class_="absolute w-100 h-100 z-1")
    local_list = []
    for item in url_list:
        local_list.append({
            'product_name': item.text,
            'walmart_id': item['link-identifier']
        })
    products = Product.objects.all().values_list('id','category_name')
    for product in products:
        for local in local_list:
            if product[1].lower() in local['product_name'].lower():
                Product.objects.filter(id=product[0]).update(walmart_id=local['walmart_id'])
