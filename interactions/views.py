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


class ShowLikeItemView(APIView):
    authentication_class = []

    def get(self, request, channel_pk, item_pk):
        user = request.user
        model_type = get_model_type_of_channel(channel_pk, item_pk)
        data = get_modeled_and_count_model(
            model_type, user, Like.is_liked, Like.count_like, item_pk, "like"
        )
        return Response(data, status=status.HTTP_200_OK)


class ShowLikedItemsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        data = get_list_model(Like.list_like, user, "like")
        return Response(data, status=status.HTTP_200_OK)


class SubscribeItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, channel_pk):
        user = request.user
        channel = Channel.objects.get(pk=channel_pk)
        if not Subscribe.is_subscribed_method(user, channel):
            subscribe_list = Subscribe.objects.filter(user=user, channel=channel)
            if subscribe_list.exists():
                subscribe = subscribe_list.last()
                subscribe.is_subscribed = True
                subscribe.save()
            else:
                Subscribe.objects.create(user=user, channel=channel)
        else:
            return Response(
                "You've subscribed this item before!",
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(_("Item has been subscribed"), status=status.HTTP_201_CREATED)


class UnSubscribeItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, channel_pk):
        user = request.user
        channel = Channel.objects.get(pk=channel_pk)
        if Subscribe.is_subscribed_method(user, channel):
            subscribe = Subscribe.objects.get(user=user, channel=channel)
            subscribe.is_subscribed = False
            subscribe.save()
        else:
            return Response(
                "You've not subscribed this item before!",
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(_("Item has been unsubscribed"), status=status.HTTP_200_OK)


class ShowSubscribedItemsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        data = get_list_model(Subscribe.list_subscribe, user, "subscribe")
        return Response(data, status=status.HTTP_200_OK)


class ShowSubscribeItemView(APIView):
    authentication_class = []

    def get(self, request, channel_pk):
        user = request.user
        channel = get_object_or_404(Channel, id=channel_pk)

        if user.is_authenticated:
            subscribed = Subscribe.is_subscribed_method(user, channel)
        else:
            subscribed = False

        subscribes_count = Subscribe.count_subscribe(channel=channel)
        data = {"subscribed": subscribed, "subscribes_count": subscribes_count}
        return Response(data, status=status.HTTP_200_OK)


class BookmarkItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, channel_pk, item_pk):
        user = request.user
        model_type, item, channel = get_model_type_and_item_of_channel(
            channel_pk, item_pk
        )

        return make_model(
            model_type,
            Bookmark.is_bookmarked,
            channel,
            Bookmark,
            user,
            item_pk,
            item,
            "bookmarked",
        )


class UnBookmarkItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, channel_pk, item_pk):
        user = request.user
        model_type = get_model_type_of_channel(channel_pk, item_pk)
        return delete_object(model_type, Like, user, item_pk, "bookmark")


class ShowBookmarkItemView(APIView):
    authentication_class = []

    def get(self, request, channel_pk, item_pk):
        user = request.user
        model_type = get_model_type_of_channel(channel_pk, item_pk)
        data = get_modeled_and_count_model(
            model_type,
            user,
            Bookmark.is_bookmarked,
            Bookmark.count_bookmark,
            item_pk,
            "bookmark",
        )
        return Response(data, status=status.HTTP_200_OK)


class ShowBookmarkedItemsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        data = get_list_model(Bookmark.list_bookmark, user, "bookmark")
        return Response(data, status=status.HTTP_200_OK)


class CommentItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, channel_pk, item_pk):
        sr_data = CommentSerializer(data=request.data)
        if sr_data.is_valid():
            user = request.user
            model_type, item, _ = get_model_type_and_item_of_channel(
                channel_pk, item_pk
            )

            content_type = ContentType.objects.get(model=model_type)
            Comment.objects.create(
                user=user, body=sr_data.validated_data["body"], content_object=item
            )
            return Response(
                "Your comment has been registered successfully!",
                status=status.HTTP_201_CREATED,
            )

        else:
            return Response(_("comment is not valid!"), status=status.HTTP_400_BAD_REQUEST)


class ShowCommentItemView(APIView):
    authentication_classes = []

    def get(self, request, channel_pk, item_pk):
        user = request.user
        model_type = get_model_type_of_channel(channel_pk, item_pk)
        content_type = ContentType.objects.get(model=model_type)
        comments = Comment.objects.filter(content_type=content_type, object_id=item_pk)
        sr_data = CommentSerializer(instance=comments, many=True)
        return Response(sr_data.data, status=status.HTTP_200_OK)

