from rest_framework import serializers
from .models import Comment, Like


class CommentSerializer(serializers.Serializer):
    body = serializers.CharField()