from django.shortcuts import render
from django.db.models import Count

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .serializers import RssSerializer, ChannelSerializer, PodcastSerializer
from .parser import parser_for_rss_podcast
from .models import Channel, Podcast, News
from .tasks import parallel_parsing

from celery.result import AsyncResult


class RssView(APIView):
    authentication_classes = []

    def get(self, request):
        url = request.query_params.get("url")
        channel = Channel.objects.get(url=url)
        results = (
            Podcast.objects.filter(channel=channel)
            if channel.channel_type == "p"
            else News.objects.filter(channel=channel)
        )

        sr_podcasts = PodcastSerializer(instance=podcasts, many=True)
        return Response(sr_podcasts.data)

    def post(self, request):
        sr_data = RssSerializer(data=request.POST)
        if sr_data.is_valid():
            print(sr_data.data)
            vd = sr_data.validated_data
            url = vd["url"]
            result = parallel_parsing.delay(url)
            task_id = result.task_id
            return Response(task_id, status=status.HTTP_200_OK)
        else:
            url = request.POST.get("url")
            if not url:
                channels = Channel.objects.all()
                (parallel_parsing.delay(channel.url) for channel in channels)
                return Response(
                    "All links are going to be updated!",
                    status=status.HTTP_202_ACCEPTED,
                )
            return Response(
                "This is not a valid url!", status=status.HTTP_400_BAD_REQUEST
            )
