from rest_framework import serializers
from .models import *
from rest_framework.validators import UniqueTogetherValidator


# Model Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'password', 'dob', 'email', 'contact_no', 'state',
                  'is_subscribed']

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
    product = serializers.StringRelatedField()

    class Meta:
        model = ProductReview
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.category_name')

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'product_description', 'product_image', 'min_price', 'max_price', 'offered_by',
                  'category', 'category_name', 'subcategory']


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = '__all__'


class LocalSellerDetailSerializer(serializers.ModelSerializer):
    local_seller = serializers.StringRelatedField()

    class Meta:
        model = LocalSellerDetail
        fields = ['id', 'local_seller', 'shop_name', 'shop_address']


class LocalSellerUploadedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalSellerUploadedData
        fields = '__all__'


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'


class PackageConsumedDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageConsumedDetail
        fields = '__all__'


class ProductReviewStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReviewStats
        fields = '__all__'
