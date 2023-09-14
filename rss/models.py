from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=100)


class Channel(models.Model):
    CHANNEL_TYPES = [
        ("p", "Podcast"),
        ("n", "News"),
    ]
    url = models.URLField(max_length=500, unique=True)
    channel_type = models.CharField(max_length=1, choices=CHANNEL_TYPES)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField()
    language = models.CharField(max_length=25, null=True, blank=True)
    owner = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    categories = models.ManyToManyField(Category, blank=True)

class Podcast(models.Model):
    guid = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    author = models.CharField(max_length=100, null=True, blank=True)
    duration = models.CharField(max_length=25, null=True, blank=True)
    explicit = models.BooleanField(default=False)
    pub_date = models.DateTimeField()
    image_url = models.URLField(max_length=500, null=True, blank=True)
    audio_url = models.URLField(max_length=500)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
