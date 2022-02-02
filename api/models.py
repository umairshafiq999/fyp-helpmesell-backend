from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, username, first_name, last_name, dob, email, contact_no, password=None):
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

        user = self.model(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            email=self.normalize_email(email),
            contact_no=contact_no,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username,first_name, last_name, dob, email, contact_no,password=None):
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


class User(AbstractBaseUser):
    first_name = models.CharField(verbose_name="First Name", max_length=50)
    last_name = models.CharField(verbose_name="Last Name", max_length=50)
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=20)
    dob = models.DateField(verbose_name="Date Of Birth")
    email = models.CharField(max_length=50)
    contact_no = models.IntegerField(verbose_name="Contact No")
    date_joined = models.DateTimeField(verbose_name="Date Registered", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="Last Login", auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password','first_name', 'last_name', 'dob', 'email', 'contact_no']

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

class Product(models.Model):
    product_name = models.CharField(verbose_name="Product Name",max_length=100)
    product_price = models.IntegerField(verbose_name="Product Price")
    product_description = models.CharField(verbose_name="Product Description",max_length=1000)
    product_reviews = models.CharField(verbose_name="Product Reviews",max_length= 1000)
    product_image = models.CharField(verbose_name="Product Image",max_length=1500)

    def __str__(self):
        return self.product_name