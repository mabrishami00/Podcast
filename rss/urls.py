from django.contrib import admin
from django.urls import path, include
from . import views

app_name = "rss"

urlpatterns = [
    path("", views.RssView.as_view(), name="rss_reader"),
    path("check/", views.CheckWorkerJobView.as_view(), name="check_worker_job"),
    path(
        "get_all_channels/", views.GetAllChannelsView.as_view(), name="get_all_channels"
    ),
    path("get_podcasts/", views.GetPodcastsView.as_view(), name="get_podcasts"),
    path(
        "recommendation_podcast/",
        views.RecommendationPodcastView.as_view(),
        name="recommendation_podcast",
    ),
]
