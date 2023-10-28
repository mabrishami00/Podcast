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
    def get(self, request):
        try:
            url = request.query_params.get("url")
            channel = Channel.objects.get(url=url)
        except:
            channel = Channel.objects.last()
        results = (
            Podcast.objects.filter(channel=channel)
            if channel.channel_type == "p"
            else News.objects.filter(channel=channel)
        )

        sr_podcasts = PodcastSerializer(instance=results, many=True)
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


class CheckWorkerJobView(APIView):
    authentication_classes = []

    def get(self, request):
        task_id = request.query_params.get("task_id")
        result = AsyncResult(task_id)
        result_state = result.state
        if result.ready():
            if result_state == "FAILURE":
                return Response(result_state, status=status.HTTP_400_BAD_REQUEST)
            elif result.state == "SUCCESS":
                return Response(result_state, status=status.HTTP_201_CREATED)
        else:
            return Response(result_state, status=status.HTTP_102_PROCESSING)


class GetAllChannelsView(APIView):
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        searched = request.GET.get("searched")
        if searched:
            channels = Channel.objects.filter(
                Q(title__icontains=searched) | Q(description__icontains=searched)
            )
        else:
            channels = Channel.objects.all()
        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(channels, request)
        serializer = ChannelSerializer(instance=paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)


class GetPodcastsView(APIView):
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        searched = request.GET.get("searched")
        if searched:
            podcasts = Podcast.objects.filter(
                Q(title__icontains=searched) | Q(description__icontains=searched)
            )
            paginator = CustomPagination()
            paginated_queryset = paginator.paginate_queryset(podcasts, request)
            serializer = PodcastSerializer(instance=paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)
        else:
            return Response(
                _("You didn't search for anything!"), status=status.HTTP_400_BAD_REQUEST
            )


class RecommendationPodcastView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        categories = [
            rp.category
            for rp in RecommendationPodcast.objects.filter(user=user).order_by(
                "-score"
            )[:3]
        ]
        channels = Channel.objects.filter(categories__in=categories)[:5]
        sr_data = ChannelSerializer(instance=channels, many=True)
        return Response(sr_data.data, status=status.HTTP_200_OK)
