from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from rss.models import Channel, Podcast, News
from .models import Like, Subscribe, Comment, Bookmark, RecommendationPodcast

from rest_framework.response import Response
from rest_framework import status


def get_model_type_and_item_of_channel(channel_pk, item_pk):
    channel = get_object_or_404(Channel, pk=channel_pk)
    if channel.channel_type == "p":
        item = get_object_or_404(Podcast, id=item_pk)
        model_type = "podcast"
    elif channel.channel_type == "n":
        item = get_object_or_404(News, id=item_pk)
        model_type = "news"
    return model_type, item, channel


def get_model_type_of_channel(channel_pk, item_pk):
    channel = get_object_or_404(Channel, pk=channel_pk)
    if channel.channel_type == "p":
        # item = get_object_or_404(Podcast, id=item_pk)
        model_type = "podcast"
    elif channel.channel_type == "n":
        # item = get_object_or_404(News, id=item_pk)
        model_type = "news"
    return model_type


def delete_object(model_type, model, user, item_pk, word):
    content_type = get_object_or_404(ContentType, model=model_type)
    try:
        model.objects.get(
            user=user, content_type=content_type, object_id=item_pk
        ).delete()
    except Exception as e:
        return Response(
            f"You have not {word} this before!", status=status.HTTP_400_BAD_REQUEST
        )
    return Response(f"Item has been un{word}", status=status.HTTP_200_OK)


def get_modeled_and_count_model(
    model_type, user, model_method, model_method_count, item_pk, word
):
    content_type = ContentType.objects.get(model=model_type)
    if user.is_authenticated:
        modeled = model_method(user, content_type, item_pk)
    else:
        modeled = False
    model_count = model_method_count(content_type=content_type)
    data = {f"{word}": modeled, f"{word}_count": model_count}
    return data


def get_list_model(model_method, user, word):
    list_model = model_method(user)
    list_model_sr = list_model.values()
    data = {f"list_{word}_sr": list_model_sr}
    return data


def make_model(
    model_type, model_method, channel, model, user, item_pk, item, word, func=None
):
    content_type = ContentType.objects.get(model=model_type)
    if not model_method(user, content_type, item_pk):
        model.objects.create(user=user, content_object=item)
        try:
            fun(channel)
        except Exception:
            pass
    else:
        return Response(
            f"You've {word} this item before!", status=status.HTTP_400_BAD_REQUEST
        )
    return Response(f"Item has been {word}", status=status.HTTP_201_CREATED)


def update_recommendations(channel):
    rec_podcasts = []
    for category in channel.categories.all():
        recommendation = RecommendationPodcast.objects.filter(
            user=user, category=category
        )
        if not recommendation.exists():
            rec_podcasts.append(
                RecommendationPodcast(user=user, category=category, score=1)
            )
        else:
            recommendation_object = recommendation.last()
            recommendation_object.score += 1
            recommendation_object.save()
    RecommendationPodcast.objects.bulk_create(rec_podcasts)
