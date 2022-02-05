from django.contrib import admin
from .models import User, Product,Price,ProductReview


# Register your models here.

admin.site.register(User)
admin.site.register(Product)
admin.site.register(Price)
admin.site.register(ProductReview)


