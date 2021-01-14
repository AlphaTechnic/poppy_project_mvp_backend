from rest_framework import serializers
from .models import Post, Pet


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post, Pet
        fields = ('__all__')