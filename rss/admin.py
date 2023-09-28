from django.contrib import admin
from .models import Category, Channel, Podcast, News
# Register your models here.

admin.site.register(Category)
admin.site.register(Channel)
admin.site.register(Podcast)
admin.site.register(News)
