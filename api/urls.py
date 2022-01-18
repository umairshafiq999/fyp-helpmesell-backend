from .views import UserAPIView,UserDetailAPIView
from django.urls import path,include
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('users/',UserAPIView.as_view()),
    path('users/<int:id>',UserDetailAPIView.as_view()),
]