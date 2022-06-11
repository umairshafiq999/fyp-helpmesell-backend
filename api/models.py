from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from .constants import *


# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, username, first_name, last_name, dob, email, contact_no, state,
                    password=None):
        if not username:
            raise ValueError('User must have an username')
        if not first_name:
            raise ValueError('User must have an First Name')
        if not last_name:
            raise ValueError('User must have an Last Name')
        if not dob:
            raise ValueError('User must have an Date Of Birth')
        if not email:
            raise ValueError('User must have an Email')
        if not contact_no:
            raise ValueError('User must have an Contact No')
        if not state:
            raise ValueError('User must have an state')

        user = self.model(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            email=self.normalize_email(email),
            contact_no=contact_no,
            state=state
        )

        user.save(using=self._db)
        return user

    def create_superuser(self, username, first_name, last_name, dob, email, contact_no, password=None):
        user = self.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            email=self.normalize_email(email),
            contact_no=contact_no,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(verbose_name="First Name", max_length=50)
    last_name = models.CharField(verbose_name="Last Name", max_length=50)
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=20)
    dob = models.DateField(verbose_name="Date Of Birth")
    email = models.CharField(max_length=50)
    contact_no = models.IntegerField(verbose_name="Contact No")
    state = models.SmallIntegerField(verbose_name='User State', choices=USER_STATE_CHOICES, default=1)
    date_joined = models.DateTimeField(verbose_name="Date Registered", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="Last Login", auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_subscribed = models.BooleanField(default=False)
    reset_password_token = models.CharField(max_length=200, default='')
    reset_password_token_valid = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password', 'first_name', 'last_name', 'dob', 'email', 'contact_no', 'state']

    objects = UserManager()

    def __str__(self):
        return self.first_name

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    @property
    def token(self):
        return ''


class Category(models.Model):
    category_name = models.CharField(verbose_name="Category Name", max_length=100)

    def __str__(self):
        return self.category_name


class SubCategory(models.Model):
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory_name = models.CharField(verbose_name="SubCategory Name", max_length=100)

    def __str__(self):
        return self.subcategory_name


class Product(models.Model):
    product_name = models.CharField(verbose_name="Product Name", max_length=100)
    product_description = models.CharField(verbose_name="Product Description", max_length=1000)
    product_image = models.CharField(verbose_name="Product Image", max_length=1500)
    min_price = models.IntegerField(verbose_name="Minimum Price", default=0)
    max_price = models.IntegerField(verbose_name="Maximum Price", default=0)
    offered_by = models.IntegerField(verbose_name="Offered By", default=0)
    category = models.ForeignKey(Category, verbose_name="Category", on_delete=models.CASCADE, default=1)
    category_name = models.CharField(verbose_name="Category Name", max_length=200, default="")
    subcategory = models.ForeignKey(SubCategory, verbose_name="Sub Category", on_delete=models.CASCADE, default=1)
    walmart_id = models.CharField(verbose_name="Walmart Id", max_length=200, default="")

    def __str__(self):
        return self.product_name


class Price(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    reference_site = models.CharField(verbose_name="Reference Site", max_length=1000)
    product_price = models.CharField(verbose_name="Product Price", max_length=6)

    def __str__(self):
        return str(self.product)


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_reviews = models.CharField(verbose_name="Product Reviews", max_length=1000)
    review_type = models.SmallIntegerField(verbose_name='Review Type', choices=REVIEW_TYPE_CHOICES, default=1)

    def __str__(self):
        template = '{0.product} {0.product_reviews}'
        return template.format(self)


class ProductReviewStats(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    positive = models.IntegerField(verbose_name="Positive Reviews Count", default=0)
    neutral = models.IntegerField(verbose_name="Neutral Reviews Count", default=0)
    negative = models.IntegerField(verbose_name="Negative Reviews Count", default=0)

    def __str__(self):
        return str(self.product)


class LocalSellerDetail(models.Model):
    id = models.AutoField(primary_key=True)
    local_seller = models.ForeignKey(User, on_delete=models.CASCADE)
    shop_name = models.CharField(verbose_name="Shop Name", max_length=100)
    shop_address = models.CharField(verbose_name="Shop Address", max_length=1000)

    def __str__(self):
        return self.shop_name


class LocalSellerUploadedData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    file_state = models.SmallIntegerField(verbose_name='File State', choices=FILE_STATE_CHOICES, default=1)
    ls_product_file = models.FileField(verbose_name="Upload CSV File", default=False,
                                       upload_to='media/LocalSellerData/')
    created = models.DateTimeField(verbose_name='Creation date', auto_now_add=True, editable=False)

    def __str__(self):
        template = '{0.user} {0.file_state}'
        return template.format(self)


class Package(models.Model):
    package_name = models.CharField(verbose_name="Package Name", max_length=10)
    package_price = models.IntegerField(verbose_name="Package Price")
    package_duration = models.CharField(verbose_name="Package Duration", max_length=25)
    package_description = models.CharField(verbose_name="Package Description", max_length=1000)
    package_keywords = models.IntegerField(verbose_name="Package Keywords", default=0)
    package_price_id = models.CharField(verbose_name="Package Price ID", max_length=150, default="")

    def __str__(self):
        return self.package_name


class PackageConsumedDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, null=True, blank=True)
    Keywords_count = models.IntegerField(verbose_name="Keywords Count", default=0)
    state = models.BooleanField(verbose_name='state', default=True)

    def __str__(self):
        template = '{0.user} {0.package}'
        return template.format(self)


class TrainingData(models.Model):
    review_text = models.CharField(verbose_name="Review Text", max_length=1000)
    review_type = models.SmallIntegerField(verbose_name="Review Type", choices=REVIEW_TYPE_CHOICES, default=1)