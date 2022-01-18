from rest_framework import serializers
from .models import User


# Model Serializer
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id','FirstName', 'LastName', 'Username','Password','CPassword','DateOfBirth','Email','ContactNo']

    def validate(self, data):
        if data['Password'] != data['CPassword']:
            raise serializers.ValidationError({'Password':'Passwords Did Not Match'})
        return data








