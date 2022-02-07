from rest_framework import serializers
from .models import User, Product, Price, ProductReview
from rest_framework.validators import UniqueTogetherValidator


# Model Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'password', 'dob', 'email', 'contact_no','state','confirm_password']

        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username']
            )


        ]


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = '__all__'
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','product_name','product_description','product_image']

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = '__all__'
