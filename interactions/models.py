from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from accounts.models import User
from rss.models import Channel


# Create your models here.
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    @staticmethod
    def is_liked(user, content_object):
        return Like.objects.filter(user=user, content_object=content_object)

    @staticmethod
    def count_like(content_object):
        return Like.objects.filter(content_object=content_object).count()

    def __str__(self):
        return self.user


class Subscribe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_subscribed = models.BooleanField(default=True)

    @staticmethod
    def is_subscribed(user, content_object):
        return Subscribe.objects.filter(user=user, content_object=content_object)

    @staticmethod
    def count_subscribed(content_object):
        return Subscribe.objects.filter(content_object=content_object).count()

    def __str__(self):
        return f"{self.user} | {self.channel}"


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    @staticmethod
    def is_bookmarked(user, content_object):
        return Bookmark.objects.filter(user=user, content_object=content_object)

    @staticmethod
    def count_bookmarked(content_object):
        return Bookmark.objects.filter(content_object=content_object).count()

    def __str__(self):
        return self.user
