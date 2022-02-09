from .views import UserAPIView,UserLoginAPIView,ProductAPIView,PriceAPIView,ProductReviewAPIView
from .views import ProductDetailAPIView,LocalSellerDetailAPIView,ProductSearchThroughNameAPIView,LocalSellerUploadedDataAPIView
from django.urls import path,include
from rest_framework.authtoken.views import obtain_auth_token
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('users/',UserAPIView.as_view()),
    path('userslogin/',UserLoginAPIView.as_view()),
    path('api-token-auth/', obtain_auth_token),
    path('product/',ProductAPIView.as_view()),
    path('product/<int:id>/',ProductDetailAPIView.as_view()),
    path('product/<str:product_name>/',ProductSearchThroughNameAPIView.as_view()),
    path('reviews/',ProductReviewAPIView.as_view()),
    path('price/',PriceAPIView.as_view()),
    path('localsellerdetail/',LocalSellerDetailAPIView.as_view()),
    path('LSUploadedData/',LocalSellerUploadedDataAPIView.as_view()),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
