from .views import UserAPIView,UserLoginAPIView
from django.urls import path,include
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('users/',UserAPIView.as_view()),
    path('userslogin/<int:id>/',UserLoginAPIView.as_view()),
]