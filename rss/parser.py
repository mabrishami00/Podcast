import xml.etree.ElementTree as ET
import requests
from rss.models import Channel, Podcast, Category
from datetime import datetime
from django.db import transaction

def parser_for_rss_podcast(feed, channel_type):
    namespaces = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"}
    response = requests.get(feed)
    root = ET.fromstring(response.text)
    channel = root.find("channel")
    channel_info, channel_category = parse_channel(channel, namespaces)
    channel_info["url"] = feed
    channel_info["channel_type"] = channel_type[0]
    items_info = parse_podcasts(channel, namespaces)
    create_channel_and_podcasts(channel_category, channel_info, items_info)

@transaction.atomic
def create_channel_and_podcasts(channel_category, channel_info, items_info):
    categories = [
        Category(title=category)
        for category in channel_category
        if not Category.objects.filter(title=category).exists()
    ]
    categories = Category.objects.bulk_create(categories)
    channel, created = Channel.objects.get_or_create(url=channel_info.get("url"), defaults=channel_info)
    channel.categories.set(categories)
    channel.save()
    podcasts = [
        Podcast(**item, channel=channel)
        for item in items_info
        if not Podcast.objects.filter(guid=item.get("guid")).exists()
    ]
    Podcast.objects.bulk_create(podcasts)


def parse_channel(channel, namespaces):
    channel_title = channel.find("title")
    channel_subtitle = channel.find("itunes:subtitle", namespaces=namespaces)
    channel_description = channel.find("description")
    channel_language = channel.find("language")
    channel_owner_name = channel.find("itunes:owner/itunes:name", namespaces=namespaces)
    channel_owner_email = channel.find(
        "itunes:owner/itunes:email", namespaces=namespaces
    )
    channel_image_url = channel.find("itunes:image", namespaces=namespaces).attrib.get(
        "href"
    )
    channel_categories = [
        item.attrib.get("text")
        for item in channel.findall("itunes:category", namespaces=namespaces)
    ]

    channel_info = {
        "title": return_text_or_none(channel_title),
        "subtitle": return_text_or_none(channel_subtitle),
        "description": return_text_or_none(channel_description),
        "language": return_text_or_none(channel_language),
        "owner": return_text_or_none(channel_owner_name),
        "email": return_text_or_none(channel_owner_email),
        "image_url": channel_image_url,
    }

    return channel_info, channel_categories


def parse_podcasts(channel, namespaces):
    channel_items = channel.findall("item")
    items_info = []

    for item in channel_items:
        item_guid = item.find("guid")
        item_title = item.find("title")
        item_description = item.find("description")
        item_author = item.find("itunes:author", namespaces=namespaces)
        item_duration = item.find("itunes:duration", namespaces=namespaces)
        item_explicit = item.find("itunes:explicit", namespaces=namespaces)
        item_pub_date = item.find("pubDate")
        item_image_url = item.find("itunes:image", namespaces=namespaces)
        item_audio_url = item.find("enclosure")

        if (
            return_text_or_none(item_guid)
            and return_text_or_none(item_title)
            and return_attrib_or_none(item_audio_url, "url")
        ):
            items_info.append(
                {
                    "guid": return_text_or_none(item_guid),
                    "title": return_text_or_none(item_title),
                    "description": return_text_or_none(item_description),
                    "author": return_text_or_none(item_author),
                    "duration": return_text_or_none(item_duration),
                    "explicit": explicit_converter(return_text_or_none(item_explicit)),
                    "pub_date": convert_str_to_datetime(
                        return_text_or_none(item_pub_date)
                    ),
                    "image_url": return_attrib_or_none(item_image_url, "href"),
                    "audio_url": return_attrib_or_none(item_audio_url, "url"),
                }
            )

    return items_info


def return_text_or_none(value):
    try:
        return value.text
    except:
        return None


def return_attrib_or_none(value, attr):
    try:
        return value.attrib.get(attr)
    except:
        return None


def convert_str_to_datetime(date_string):
    date_format = "%a, %d %b %Y %H:%M:%S %z"
    try:
        return datetime.strptime(date_string, date_format)
    except:
        return None


def explicit_converter(value):
    if value is None:
        return False
    elif value.lower() in ("false", "no"):
        return False
    elif value.lower() in ("true", "yes"):
        return True
    return False
