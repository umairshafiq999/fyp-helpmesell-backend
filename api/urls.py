from .views import UserAPIView
from django.urls import path,include
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('users/',UserAPIView.as_view()),
]