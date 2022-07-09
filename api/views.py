from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import *
import random, string
from django.shortcuts import render, redirect
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .task import *
from django.conf import settings
import stripe
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


# Create your views here.
class UserAPIView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        user_serializer = UserSerializer(data=request.data)

        if user_serializer.is_valid():
            user_serializer.save(password=make_password(request.data['password']))
            user = User.objects.get(id=user_serializer.data['id'])
            user.is_subscribed = True
            user.save()
            PackageConsumedDetail.objects.get_or_create(
                package_id=1,
                user_id=user_serializer.data['id'],
                Keywords_count=0,
                state=1
            )
            return Response(user_serializer.data, status.HTTP_201_CREATED)

        return Response(user_serializer.errors, status.HTTP_400_BAD_REQUEST)


class GetUserAPIView(APIView):
    def get(self, request, id):
        user = User.objects.get(id=id)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class ForgetPasswordAPIView(APIView):
    def post(self, request):
        user_email = request.data['email']
        try:
            user = User.objects.get(email=user_email)
            token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
            user.reset_password_token = token
            user.reset_password_token_valid = True
            user.save()
        except User.DoesNotExist:
            return Response("Kindly enter the correct email", status.HTTP_400_BAD_REQUEST)
        message = Mail(
            from_email='helpmesell5@gmail.com',
            to_emails=user.email,
            subject='Password Change Request',
            html_content='Kindly reset your password using the given link ' + 'http://172.20.146.105:8000/api/EmailTokenVerification/' +
                         token)
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)
        return Response(
            'Email has been sent',
            status.HTTP_200_OK
        )


class GetTokenAPIView(APIView):
    def get(self, request, reset_password_token):
        try:
            user = User.objects.get(reset_password_token=reset_password_token, reset_password_token_valid=True)
            user.reset_password_token_valid = False
            user.save()
            return redirect(settings.FRONT_END_URL + '/ResetPassword/' + str(user.id))
        except:
            return redirect(settings.FRONT_END_URL + '/ResetPassword/')


class ResetPasswordAPIView(APIView):
    def post(self, request):
        User.objects.filter(id=request.data['user_id']).update(password=make_password(request.data["password"]))
        return Response("Successfully password changed", status.HTTP_200_OK)


class LocalSellerSignUpAPIView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = UserSerializer(data=request.data)

        if user.is_valid():
            local_seller = user.save(password=make_password(request.data["password"]), state=2)
            LocalSellerDetail.objects.create(
                local_seller=local_seller,
                shop_name=request.data["shop_name"],
                shop_address=request.data["shop_address"]
            )

            return Response(user.data, status.HTTP_201_CREATED)
        return Response(user.errors, status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'id': user.id,
            'token': token.key,
            'username': user.username,
            'first_name': user.first_name,
            'state': user.state,
            'is_subscribed': user.is_subscribed
        })


class ProductAPIView(APIView):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        products = Product.objects.all()
        # serializer = ProductSerializer(products, many=True)
        # return Response(serializer.data)
        product_list = []
        for product in products:
            if not len([p for p in product_list if p['product_name'][:15] in product.product_name]):
                product_list.append({
                    "id": product.id,
                    "product_name": product.product_name,
                    "product_description": "Great Phone",
                    "product_image": product.product_image,
                    "min_price": 0,
                    "max_price": 0,
                    "offered_by": 0,
                    "category": product.category.id,
                    "category_name": product.category_name,
                    "subcategory": product.subcategory.id,
                    "price": ''.join(i for i in product.price_set.all()[0].product_price if i.isdigit())
                })
        return Response(product_list, status.HTTP_200_OK)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class ProductDetailAPIView(APIView):
    def get(self, request, id):
        # if Package.package_name == 'Basic' and Package.package_keywords < request.POST.get('package_keywords'):
        #         if Package.package_name == 'Standard' and Package.package_keywords < request.POST.get('package_keywords'):
        #             if Package.package_name == 'Premium' and Package.package_keywords < request.POST.get('package_keywords'):
        try:
            product = Product.objects.filter(pk=id).values()
            product_prices = Price.objects.filter(product_id=product[0]['id']).values()
            data = {"product": product[0], "product_prices": product_prices}
            return Response(
                {
                    'success': True,
                    'detail': 'product with all prices',
                    'data': data
                },
                status=status.HTTP_200_OK
            )


        except Product.DoesNotExist:
            return Response(status.HTTP_400_BAD_REQUEST)


class LaptopsAPIView(APIView):
    def get(self, request):
        products = Product.objects.filter(category=1)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class MobilesAPIView(APIView):
    def get(self, request):
        products = Product.objects.filter(category=2)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductSearchThroughIDAPIView(APIView):
    def get_object(self, product_name):
        try:
            return Product.objects.filter(category_name__icontains=product_name)
        except Product.DoesNotExist:
            return Response(status.HTTP_400_BAD_REQUEST)

    def get(self, request, id, user_id):
        product = Product.objects.get(id=id)
        products = []
        for product in Product.objects.filter(category_name__icontains=product.category_name):
            prices = ""
            for price in Price.objects.filter(product_id=product.id):
                prices = prices + price.product_price + '(' + price.reference_site + '), '
            products.append({
                'product_name': product.product_name,
                'id': product.id,
                'product_image': product.product_image,
                'prices': prices,
                'category_name': product.category_name
            })
        user = User.objects.get(id=user_id)
        subscribed_package, package = False, False
        try:
            subscribed_package = PackageConsumedDetail.objects.get(user_id=user_id, state=True)
        except PackageConsumedDetail.DoesNotExist:
            pass
        if subscribed_package:
            subscribed_package.Keywords_count = subscribed_package.Keywords_count + 1
            subscribed_package.save()
        try:
            package = Package.objects.get(pk=subscribed_package.package.id)
        except:
            pass
        if subscribed_package and package and subscribed_package.Keywords_count >= package.package_keywords:
            user.is_subscribed = False
            subscribed_package.state = False
            subscribed_package.save()
            user.save()

        package_detail = PackageConsumedDetail.objects.filter(user_id=user_id,state=1)
        if len(package_detail):
            package_taken = Package.objects.get(id=package_detail[0].package_id)
            if package_detail[0].Keywords_count > package_taken.package_keywords:
                return Response(status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(status.HTTP_401_UNAUTHORIZED)
        return Response(
            {
                'success': True,
                'detail': 'product with all prices',
                'data': products
            },
            status=status.HTTP_200_OK
    )


class ProductSearchThroughNameAPIView(APIView):
    def get_object(self, product_name):
        try:
            return Product.objects.filter(category_name__icontains=product_name)
        except Product.DoesNotExist:
            return Response(status.HTTP_400_BAD_REQUEST)

    def get(self, request, product_name):
        product = Product.objects.get(product_name=product_name)
        products = []
        for product in Product.objects.filter(category_name__icontains=product.category_name):
            prices = ""
            for price in Price.objects.filter(product_id=product.id):
                prices = prices + price.product_price + '(' + price.reference_site + '), '
            products.append({
                'product_name': product.product_name,
                'id': product.id,
                'product_image': product.product_image,
                'prices': prices,
                'category_name': product.category_name
            })
        return Response(
            {
                'success': True,
                'detail': 'product with all prices',
                'data': products
            },
            status=status.HTTP_200_OK
        )


class ProductReviewAPIView(APIView):
    def get(self, request):
        productreviews = ProductReview.objects.all()
        serializer = ProductReviewSerializer(productreviews, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductReviewSerializer(data=request.data)
        if serializer.is_valid():
            ProductReview.objects.create(
                product_id=request.data['product'],
                product_reviews=request.data['product_reviews']
            )
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class PriceAPIView(APIView):
    def get(self, request):
        ProductPrice = Price.objects.all()
        serializer = PriceSerializer(ProductPrice, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PriceSerializer(data=request.data)

        if serializer.is_valid():
            Price.objects.create(
                product_id=request.data['product'],
                reference_site=request.data['reference_site'],
                product_price=request.data['product_price']

            )
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class LocalSellerDetailAPIView(APIView):
    def get(self, request):
        local_seller_detail = list(
            LocalSellerDetail.objects.filter(local_seller__state=2).values_list('local_seller__first_name', 'shop_name',
                                                                                'shop_address'))
        # serializer = LocalSellerDetailSerializer(local_seller_detail, many=True)
        return Response(local_seller_detail)

    def post(self, request):
        serializer = LocalSellerDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # LocalSellerDetail.objects.create(
            #     local_seller_id=request.data['local_seller'],
            #     shop_name=request.data['shop_name'],
            #     shop_address=request.data['shop_address']
            # )
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class LocalSellerUploadedDataAPIView(APIView):
    def get(self, request):
        uploaded_data = LocalSellerUploadedData.objects.all()
        serializer = LocalSellerUploadedDataSerializer(uploaded_data, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LocalSellerUploadedDataSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.save()
            data.user_id = request.data['user']
            data.save()
            file = settings.MEDIA_ROOT + data.ls_product_file.url[6:]
            user_id = request.data['user']
            LocalSellerFileUpload.delay(user_id,file)
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class ScrapersAPIView(APIView):
    def post(self, request):
        if 'shophive' in request.data['website']:
            ShopHiveScraper.delay(request.data['website'])
            return Response("Data has started to Scrape", status.HTTP_201_CREATED)
        elif 'pakistanistores' in request.data['website'] and 'laptops-and-pc':
            PakistaniStoresLaptopScraper.delay(request.data['website'])
            return Response("Data has started to Scrape", status.HTTP_201_CREATED)
        elif 'pakistanistores' in request.data['website']:
            PakistaniStoresMobileScraper.delay(request.data['website'])
            return Response("Data has started to Scrape", status.HTTP_201_CREATED)
        elif 'mega.pk' in request.data['website']:
            MegaPkScraper.delay(request.data['website'])
            return Response("Data has started to Scrape", status.HTTP_201_CREATED)


stripe.api_key = settings.STRIPE_SECRET_KEY


class PackageAPIView(APIView):
    def get(self, request):
        packages = Package.objects.all()
        serializer = PackageSerializer(packages, many=True)
        return Response(serializer.data)


class PaymentAPIView(APIView):
    def post(self, request):
        try:
            user = stripe.Customer.create(
                name=request.data['name'],
                email=request.data['email'],

            )
        except:
            return Response("Customer not created", status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            exp_date = request.data['exp_date'].replace(' ', '')
            [exp_month, exp_year] = exp_date.split('/')
            paymentMethod = stripe.PaymentMethod.create(
                type="card",
                card={
                    "number": request.data['number'].replace(' ', ''),
                    "exp_month": exp_month,
                    "exp_year": exp_year,
                    "cvc": request.data['cvc'],
                },
            )
        except:
            return Response("Payment method not created", status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            payment_attachment = stripe.PaymentMethod.attach(
                paymentMethod,
                customer=user,
            )
        except:
            return Response("Payment method not attached", status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            stripe.Customer.modify(
                user.id,
                invoice_settings={
                    'default_payment_method': payment_attachment
                }
            )
        except:
            return Response("Customer not modified", status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            stripe.Subscription.create(
                customer=user,
                items=[{"price": request.data['price']}],
            )
        except:
            return Response("Subscription not created", status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            user_id = request.data['user_id']
            User.objects.filter(id=user_id).update(is_subscribed=True)
            PackageConsumedDetail.objects.get_or_create(
                user_id=user_id,
                package_id=Package.objects.get(package_price_id=request.data['price']).id,
                state=True
            )
            message = Mail(
                from_email='helpmesell5@gmail.com',
                to_emails=user.email,
                subject='Welcome to HelpMeSell! Hooray!',
                html_content='Your payment has been successful. Thank you for Subscribing to us.')
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            sg.send(message)
            return Response("Payment Successful", status.HTTP_200_OK)

        except:
            return Response("Payment Not Successful", status.HTTP_500_INTERNAL_SERVER_ERROR)


class PackageConsumedDetailAPIView(APIView):
    def get(self, request):
        package_consumed_detail = PackageConsumedDetail.objects.all()
        serializer = PackageConsumedDetailSerializer(package_consumed_detail, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PackageConsumedDetailSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class ProductReviewStatsAPIView(APIView):
    def get(self, request, product_id):
        try:
            product_review_stats = ProductReviewStats.objects.get(product=product_id)
            return Response([
                {"type": "positive", "value": product_review_stats.positive},
                {"type": "neutral", "value": product_review_stats.neutral},
                {"type": "negative", "value": product_review_stats.negative}
            ])
        except:
            return Response([
                {"type": "positive", "value": 0},
                {"type": "neutral", "value": 0},
                {"type": "negative", "value": 0}
            ])

    def post(self, request):
        serializer = ProductReviewStatsSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class PullReviewsAPIView(APIView):
    def post(self, request):
        pull_reviews.delay()
        return Response("Reviews started to get pull", status.HTTP_200_OK)


class UserStatisticsAPIView(APIView):
    def get(self, request, id):
        package = PackageConsumedDetail.objects.filter(user=id, state=1)[0]
        user = User.objects.get(id=id)
        return Response(
            {
                'package': package.package.package_name,
                'total': package.package.package_keywords,
                'consumed': package.Keywords_count,
                'is_subscribed': package.user.is_subscribed,
                'Designation': user.state
            })


class ReportingStatisticsAPIView(APIView):
    def get(self, request):
        user = User.objects.all()
        total_subscribed = PackageConsumedDetail.objects.all()
        total_mobiles = Product.objects.filter(category_id=2)
        total_laptops = Product.objects.filter(category_id=1)
        total_standard_package = PackageConsumedDetail.objects.filter(package_id=2)
        total_premium_package = PackageConsumedDetail.objects.filter(package_id=3)

        count = 0
        for user_count in user:
            count=count+1
        scount=0
        for subscribed_count in total_subscribed:
            scount=scount+1
        mcount=0
        for mobile_count in total_mobiles:
            mcount=mcount+1
        lcount = 0
        for laptop_count in total_laptops:
            lcount = lcount + 1
        standard_count = 0
        for standardcount in total_standard_package:
            standard_count = standard_count + 1
        premium_count = 0
        for premiumcount in total_premium_package:
            premium_count = premium_count + 1

        if standard_count < premium_count:
            most_bought_package = 'Premium Package'
        else:
            most_bought_package = 'Standard Package'

        return Response(
            {
                'user_count': count,
                'mobile_count': mcount,
                'laptop_count': lcount,
                'Most Bought Package': most_bought_package,
                'Total Subscribed': scount
                # 'Designation': user.state
            })


