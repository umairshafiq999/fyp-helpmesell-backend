from .views import *
from django.urls import path,include
from rest_framework.authtoken.views import obtain_auth_token
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('users/',UserAPIView.as_view()),
    path('localSellerSignUp/',LocalSellerSignUpAPIView.as_view()),
    path('userslogin/',UserLoginAPIView.as_view()),
    path('api-token-auth/', obtain_auth_token),
    path('api/products/',ProductAPIView.as_view()),
    path('api/product/<int:id>/',ProductDetailAPIView.as_view()),
    path('api/product/<str:product_name>/',ProductSearchThroughNameAPIView.as_view()),
    path('api/reviews/',ProductReviewAPIView.as_view()),
    path('api/price/',PriceAPIView.as_view()),
    path('api/localsellerdetail/',LocalSellerDetailAPIView.as_view()),
    path('api/LSUploadedData/',LocalSellerUploadedDataAPIView.as_view()),
    path('api/Scrapers/',ScrapersAPIView.as_view()),
    path('api/Packages/',PackageAPIView.as_view()),
    path('api/Payment/',PaymentAPIView.as_view()),
    path('api/Payment/',PaymentAPIView.as_view()),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
