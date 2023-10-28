from django.shortcuts import render
from .models import Like, Comment, Bookmark
from rss.models import Channel, Podcast, News
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from .serializers import CommentSerializer
from django.shortcuts import get_object_or_404

# Create your views here.
class LikeItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, channel_pk, item_pk):
        user = request.user
        model_type, item, channel = get_model_type_and_item_of_channel(
            channel_pk, item_pk
        )
        return make_model(
            model_type,
            Like.is_liked,
            channel,
            Like,
            user,
            item_pk,
            item,
            "liked",
            update_recommendations,
        )


class UnLikeItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, channel_pk, item_pk):
        user = request.user
        model_type = get_model_type_of_channel(channel_pk, item_pk)
        return delete_object(model_type, Like, user, item_pk, "liked")


class ShowLikeItemView(View):
    authentication_class = []

    def get(self, request, channel_pk, item_pk):
        user = request.user
        channel = get_object_or_404(Channel, id=channel_pk)
        if channel.channel_type == "p":
            item = get_object_or_404(Podcast, id=item_pk)
        elif channel.channel_type == "n":
            item = get_object_or_404(News, id=item_pk)

        if user.is_authenticated():
            liked = Like.is_liked(user, item)
        else:
            liked = False

        likes_count = Like.count_like(item)
        data = {"liked": liked, "likes_count": likes_count}
        return Response(data, status=status.HTTP_200_OK)    
    

class SubscribeItemView(View):
    def post(self, request, channel_pk, item_pk):
        channel = Channel.objects.get(pk=channel_pk)
        if channel.channel_type == "p":
            item = channel.objects.filter(podcast_set__id=item_pk)
        elif channel.channel_type == "n":
            item = channel.objects.filter(news_set__id=item_pk)
        Subscribe.objects.create(user=user, content_object=item)
        return Response("Item has been subscribed", status=status.HTTP_201_CREATED)


class ShowSubscribeItemView(View):
    authentication_class = []

    def get(self, request, channel_pk, item_pk):
        user = request.user
        channel = get_object_or_404(Channel, id=channel_pk)
        if channel.channel_type == "p":
            item = get_object_or_404(Podcast, id=item_pk)
        elif channel.channel_type == "n":
            item = get_object_or_404(News, id=item_pk)

        if user.is_authenticated():
            subscribed = Subscribe.is_subscribed(user, item)
        else:
            subscribed = False

        subscribes_count = Subscribe.count_subscribe(item)
        data = {"subscribed": subscribed, "subscribes_count": subscribes_count}
        return Response(data, status=status.HTTP_200_OK)    
    

class BookmarkItemView(View):
    def post(self, request, channel_pk, item_pk):
        channel = Channel.objects.get(pk=channel_pk)
        if channel.channel_type == "p":
            item = channel.objects.filter(podcast_set__id=item_pk)
        elif channel.channel_type == "n":
            item = channel.objects.filter(news_set__id=item_pk)
        Bookmark.objects.create(user=user, content_object=item)
        return Response("Item has been bookmarked", status=status.HTTP_201_CREATED)


class ShowBookmarkItemView(View):
    def get(self, request, channel_pk, item_pk):
        user = request.user
        channel = get_object_or_404(Channel, id=channel_pk)
        if channel.channel_type == "p":
            item = get_object_or_404(Podcast, id=item_pk)
        elif channel.channel_type == "n":
            item = get_object_or_404(News, id=item_pk)

        if user.is_authenticated():
            bookmarked = Bookmark.is_bookmarked(user, item)
        else:
            bookmarked = False

        bookmarks_count = Bookmark.count_like(item)
        data = {"bookmarked": bookmarked, "bookmarks_count": bookmarks_count}
        return Response(data, status=status.HTTP_200_OK)    

class CommentItemView(View):
    def post(self, request, channel_pk, item_pk):
        sr_data = CommentSerializer(data=request.POST)
        if sr_data.is_valid():
            channel = Channel.objects.get(pk=channel_pk)
            if channel.channel_type == "p":
                item = channel.objects.filter(podcast_set__id=item_pk)
            elif channel.channel_type == "n":
                item = channel.objects.filter(news_set__id=item_pk)
            sr_data.save(user=user, content_object=item)
            return Response("comment has been added", status=status.HTTP_201_CREATED)
        else:
            return Response("comment is not valid!", status=status.HTTP_400_BAD_REQUEST)
        
