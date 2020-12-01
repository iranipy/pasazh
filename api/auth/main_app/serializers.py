from rest_framework import serializers
from .models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):  # Test
    class Meta:
        model = User
        fields = '__all__'
