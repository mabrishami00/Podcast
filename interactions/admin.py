from django.contrib import admin
from .models import Like, Bookmark, Subscribe, Comment, RecommendationPodcast
# Register your models here.

admin.site.register(Like)
admin.site.register(Bookmark)
admin.site.register(Subscribe)
admin.site.register(Comment)
admin.site.register(RecommendationPodcast)

