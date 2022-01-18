from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import authentication
from rest_framework import exceptions
from .models import User
from .serializers import UserSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.serializers import Serializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
# Create your views here.
class UserAPIView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

class UserLoginAPIView(APIView):
    def get_object(self, id):
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            return HttpResponse(status.HTTP_400_BAD_REQUEST)

    def get(self, request, id):
        users = self.get_object(id)
        serializer = UserSerializer(users)
        return Response(serializer.data)