from django.contrib import admin
from django.urls import path, include
from . import views

app_name = "rss"

urlpatterns = [
    path("", views.RssView.as_view(), name="rss_reader"),
]
