from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User, Product, Price, ProductReview, LocalSellerDetail, LocalSellerUploadedData
from .serializers import UserSerializer, ProductSerializer, PriceSerializer, ProductReviewSerializer, \
    LocalSellerUploadedDataSerializer, LocalSellerDetailSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .task import *



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
            user.save(password=make_password(request.data["password"]),
                      confirm_password=make_password(request.data["confirm_password"]))
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
            local_seller = user.save(password=make_password(request.data["password"]),
                                     confirm_password=make_password(request.data["confirm_password"]),state=2)
            LocalSellerDetail.objects.create(
                local_seller=local_seller,
                shop_name= request.data["shop_name"],
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
            'token': token.key,
            'username': user.username,
            'first_name': user.first_name
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
    def get_object(self, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response(status.HTTP_400_BAD_REQUEST)

    def get(self, request, id):
        products = self.get_object(id)
        serializer = ProductSerializer(products)
        return Response(serializer.data)


class ProductSearchThroughNameAPIView(APIView):
    def get_object(self, product_name):
        try:
            return Product.objects.get(product_name=product_name)
        except Product.DoesNotExist:
            return Response(status.HTTP_400_BAD_REQUEST)

    def get(self, request, product_name):
        products = self.get_object(product_name)
        serializer = ProductSerializer(products)
        return Response(serializer.data)


class ProductReviewAPIView(APIView):
    def get(self, request):
        productreviews = ProductReview.objects.all()
        serializer = ProductReviewSerializer(productreviews, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductReviewSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
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
            serializer.save()
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
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class LocalSellerUploadedDataAPIView(APIView):
    def get(self, request):
        uploaded_data = LocalSellerUploadedData.objects.all()
        serializer = LocalSellerUploadedDataSerializer(uploaded_data, many=True)
        return Response(serializer.data)

    def post(self, request):
        LocalSellerFileUpload.delay()
        serializer = LocalSellerUploadedDataSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
