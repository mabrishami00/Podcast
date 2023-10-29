from django.urls import path
from . import views

app_name = "interactions"

urlpatterns = [
    path(
        "like/<int:channel_pk>/<int:item_pk>/",
        views.LikeItemView.as_view(),
        name="like",
    ),
    path(
        "unlike/<int:channel_pk>/<int:item_pk>/",
        views.UnLikeItemView.as_view(),
        name="unlike",
    ),
    path(
        "show_like/<int:channel_pk>/<int:item_pk>/",
        views.ShowLikeItemView.as_view(),
        name="show_like",
    ),
    path(
        "show_liked_items/", views.ShowLikedItemsView.as_view(), name="show_liked_items"
    ),
    path(
        "subscribe/<int:channel_pk>/",
        views.SubscribeItemView.as_view(),
        name="subscribe",
    ),
    path(
        "unsubscribe/<int:channel_pk>/",
        views.UnSubscribeItemView.as_view(),
        name="unsubscribe",
    ),
    path(
        "show_subscribe/<int:channel_pk>/",
        views.ShowSubscribeItemView.as_view(),
        name="show_subscribe",
    ),
    path(
        "show_subscribed_items/",
        views.ShowSubscribedItemsView.as_view(),
        name="show_subscribe_items",
    ),
    path(
        "bookmark/<int:channel_pk>/<int:item_pk>/",
        views.BookmarkItemView.as_view(),
        name="bookmark",
    ),
    path(
        "unbookmark/<int:channel_pk>/<int:item_pk>/",
        views.UnBookmarkItemView.as_view(),
        name="unbookmark",
    ),
    path(
        "show_bookmark/<int:channel_pk>/<int:item_pk>/",
        views.ShowBookmarkItemView.as_view(),
        name="show_bookmark",
    ),
    path(
        "show_bookmarked_items/",
        views.ShowBookmarkedItemsView.as_view(),
        name="show_bookmarked_items",
    ),
    path(
        "comment/<int:channel_pk>/<int:item_pk>/",
        views.CommentItemView.as_view(),
        name="comment",
    ),
    path(
        "comment_item/<int:channel_pk>/<int:item_pk>/",
        views.ShowCommentItemView.as_view(),
        name="comment_item",
    ),
    path(
        "uncomment/<int:comment_pk>/",
        views.UnCommentItemView.as_view(),
        name="uncomment",
    ),
]
