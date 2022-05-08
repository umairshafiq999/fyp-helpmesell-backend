from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import *
from .serializers import *
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .task import *
from django.conf import settings
import stripe


# Create your views here.
class UserAPIView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = UserSerializer(data=request.data)

        if user.is_valid():
            user.save(password=make_password(request.data["password"]))
            return Response(user.data, status.HTTP_201_CREATED)
        return Response(user.errors, status.HTTP_400_BAD_REQUEST)


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
            'state': user.state
        })


class ProductAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class ProductDetailAPIView(APIView):
    def get(self, request, id):
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


class ProductSearchThroughNameAPIView(APIView):
    def get_object(self, product_name):
        try:
            return Product.objects.filter(category_name__icontains=product_name)
        except Product.DoesNotExist:
            return Response(status.HTTP_400_BAD_REQUEST)

    def get(self, request, id):
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
                        offered_by=3,
                        category_name=row[0][0: 12]

                    )
                    Price.objects.create(
                        product_id=product.id,
                        reference_site="shophive.com",
                        product_price=row[1]

                    )

            # LocalSellerFileUpload.delay(file)
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


stripe.api_key = settings.STRIPE_SECRET_KEY


class PackageAPIView(APIView):
    def get(self, request):
        packages = Package.objects.all()
        serializer = PackageSerializer(packages, many=True)
        return Response(serializer.data)


class PaymentAPIView(APIView):
    def post(self, request):
        try:
            user = stripe.User.create(
                username=request.data['name'],
                payment_method=request.data['payment_method_id'],
                is_subscribed=True,
                invoice_settings={
                    'default_payment_method': request.data['payment_method_id']
                }
            )
            subscription = stripe.Subscription.create(
                user=user,
                items=[
                    {
                        'product': request.data['packageId'],
                        'price': request.data['priceId']

                    }
                ]
            )

            return Response(subscription, status.HTTP_200_OK)

        except:
            return Response("Payment not successful", status.HTTP_500_INTERNAL_SERVER_ERROR)
