from rest_framework import serializers
from .models import Comment

class CommentSerializer(serializers.Serializer):
    class Meta:
        model = Comment
        fields = ["body"]

    def save(self, user, content_object):
        comment = super().save(*args, **kwargs)
        comment.user = user
        comment.content_object = content_object
        comment.save()
        return comment

