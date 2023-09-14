from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RssSerializer, ChannelSerializer, PodcastSerializer
from .parser import parser_for_rss_podcast
from .models import Channel, Podcast

# Create your views here.


class RssView(APIView):
    authentication_classes = []

    def get(self, request):
        url = request.query_params.get("url")
        channel = Channel.objects.get(url=url)
        podcasts = Podcast.objects.filter(channel=channel)
        sr_podcasts = PodcastSerializer(instance=podcasts, many=True)
        return Response(sr_podcasts.data)

    def post(self, request):
        sr_data = RssSerializer(data=request.POST)
        if sr_data.is_valid():
            vd = sr_data.validated_data
            url = vd["url"]
            channel_type = vd["channel_type"]
            if channel_type == "podcast":
                parser_for_rss_podcast(url, channel_type)
                return Response("ok")
