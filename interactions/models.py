from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from accounts.models import User
from rss.models import Channel, Category


# Create your models here.
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    @classmethod
    def is_liked(cls, user, content_type, object_id):
        return cls.objects.filter(
            user=user, content_type=content_type, object_id=object_id
        ).exists()

    @classmethod
    def count_like(cls, content_type):
        return cls.objects.filter(content_type=content_type).count()

    @classmethod
    def list_like(cls, user):
        return cls.objects.filter(user=user)

    def __str__(self):
        return f"{self.user}"


class Subscribe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_subscribed = models.BooleanField(default=True)

    @classmethod
    def is_subscribed_method(cls, user, channel):
        try:
            result = cls.objects.get(user=user, channel=channel).is_subscribed
        except Exception as e:
            return False
        else:
            return result

    @classmethod
    def count_subscribe(cls, channel):
        return cls.objects.filter(channel=channel, is_subscribed=True).count()

    @classmethod
    def list_subscribe(cls, user):
        return cls.objects.filter(user=user)

    @classmethod
    def get_all_users_subscribe_channel(cls, channel):
        return [subscribe.user for subscribe in cls.objects.filter(channel=channel)]


    def __str__(self):
        return f"{self.user} | {self.channel}"


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    @classmethod
    def is_bookmarked(cls, user, content_type, object_id):
        return cls.objects.filter(
            user=user, content_type=content_type, object_id=object_id
        ).exists()

    @classmethod
    def count_bookmark(cls, content_type):
        return cls.objects.filter(content_type=content_type).count()

    @classmethod
    def list_bookmark(cls, user):
        return cls.objects.filter(user=user)

    def __str__(self):
        return f"{self.user}"


class RecommendationPodcast(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user} | {self.category} | {self.score}"
