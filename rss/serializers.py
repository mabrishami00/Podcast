from rest_framework import serializers
from .models import Channel, Podcast


class RssSerializer(serializers.Serializer):
    url = serializers.CharField()
    channel_type = serializers.CharField()


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = (
            "url",
            "channel_type",
            "title",
            "subtitle",
            "description",
            "language",
            "owner",
            "email",
            "image_url",
            "categories",
        )


class PodcastSerializer(serializers.ModelSerializer):

    class Meta:
        model = Podcast
        fields = (
            "guid",
            "title",
            "description",
            "author",
            "duration",
            "explicit",
            "pub_date",
            "image_url",
            "audio_url",
            "channel",
        )
