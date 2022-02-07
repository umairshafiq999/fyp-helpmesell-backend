from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import User, Product, Price, ProductReview
from .serializers import UserSerializer, ProductSerializer, PriceSerializer, ProductReviewSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
import xlrd


# Create your views here.
class UserAPIView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

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


class ProductReviewAPIView(APIView):

    def get(self, request):
        productreviews = ProductReview.objects.all()
        serializer = ProductSerializer(productreviews, many=True)
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
        serializer = ProductSerializer(ProductPrice, many=True)
        return Response(serializer.data)

    def post(self, request):
        file = request.FILES.get('product_file')
        fileRead = xlrd.open_workbook(file)

        fileSheet = fileRead.sheet_by_index(0)

        for row in fileSheet.rows:
            try:
                Product.objects.get(product_name=row.value['product_name'])
                Price.objects.create(
                    product_price=row['product_price']
                )
            except Product.objects.get(product_name=row.value['product_name']).DoesNotExist:
                Product.objects.create(
                    product_name=row.value(['product_name'])

                )
                Price.objects.create(
                    product_price=row.value(['product_price'])
                )
        serializer = PriceSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
