from rest_framework import serializers
from .models import User
from rest_framework.validators import UniqueTogetherValidator

# Model Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['Username']
            )
        ]

    def validate(self, data):
        if data['Password'] != data['CPassword']:
            raise serializers.ValidationError({'Password':'Passwords Did Not Match'})
        return data










