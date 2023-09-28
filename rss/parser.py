import xml.etree.ElementTree as ET
import requests
from rss.models import Channel, Podcast, Category, News
from datetime import datetime
from django.db import transaction
from .exceptions import NotValidXML

def parser_for_rss_podcast(feed):
    namespaces = {
        "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
        "media": "http://search.yahoo.com/mrss/",
    }
    response = requests.get(feed)
    if "xml" not in response.headers.get("Content-Type"):
        raise notValidXML()
    root = ET.fromstring(response.text)
    channel = root.find("channel")
    channel_type = "p" if "enclosure" in response.text else "n"
    channel_info, channel_category = parse_channel(channel, namespaces)
    channel_info["url"] = feed
    channel_info["channel_type"] = channel_type
    items_info = (
        parse_news(channel, namespaces)
        if channel_type == "n"
        else parse_podcasts(channel, namespaces)
    )
    create_channel_and_podcasts(channel_category, channel_info, items_info)


def create_channel_and_podcasts(channel_category, channel_info, items_info):
    categories = []
    existed_categories = []

    for category in channel_category:
        if not Category.objects.filter(title=category).exists():
            categories.append(Category(title=category))
        else:
            existed_categories.append(Category.objects.get(title=category))

    categories = Category.objects.bulk_create(categories)
    categories += existed_categories
    channel, created = Channel.objects.get_or_create(
        url=channel_info.get("url"), defaults=channel_info
    )
    channel.categories.set(categories)
    channel.save()
    try:
        condition = channel.pub_date < channel_info["pub_date"]
    except:
        condition = False

    if created or condition:
        if channel_info["channel_type"] == "p":
            print("if podcast")
            podcasts = [
                Podcast(**item, channel=channel)
                for item in items_info
                if not Podcast.objects.filter(guid=item.get("guid")).exists()
            ]
            Podcast.objects.bulk_create(podcasts)

        elif channel_info["channel_type"] == "n":
            print("if news")
            news = [
                News(**item, channel=channel)
                for item in items_info
                if not News.objects.filter(guid=item.get("guid")).exists()
            ]
            News.objects.bulk_create(news)


def parse_channel(channel, namespaces):
    channel_title = channel.find("title")
    channel_subtitle = channel.find("itunes:subtitle", namespaces=namespaces)
    channel_description = channel.find("description")
    channel_pub_date = channel.find("pubDate")
    channel_language = channel.find("language")
    channel_owner_name = channel.find("itunes:owner/itunes:name", namespaces=namespaces)
    channel_owner_email = channel.find(
        "itunes:owner/itunes:email", namespaces=namespaces
    )
    channel_image_url = channel.find("itunes:image", namespaces=namespaces)
    channel_categories = [
        return_attrib_or_none(item, "text")
        for item in channel.findall("itunes:category", namespaces=namespaces)
        if return_attrib_or_none(item, "text") is not None
    ]

    channel_info = {
        "title": return_text_or_none(channel_title),
        "subtitle": return_text_or_none(channel_subtitle),
        "description": return_text_or_none(channel_description),
        "pub_date": convert_str_to_datetime(return_text_or_none(channel_pub_date)),
        "language": return_text_or_none(channel_language),
        "owner": return_text_or_none(channel_owner_name),
        "email": return_text_or_none(channel_owner_email),
        "image_url": return_attrib_or_none(channel_image_url, "href"),
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


def parse_news(channel, namespaces):
    channel_items = channel.findall("item")
    items_info = []

    for item in channel_items:
        item_guid = item.find("guid")
        item_title = item.find("title")
        item_description = item.find("description")
        item_source = item.find("source", namespaces=namespaces)
        item_source_link = item.find("source", namespaces=namespaces)
        item_pub_date = item.find("pubDate")
        item_image_url = item.find("media:content", namespaces=namespaces)

        if return_text_or_none(item_guid) and return_text_or_none(item_title):
            items_info.append(
                {
                    "guid": return_text_or_none(item_guid),
                    "title": return_text_or_none(item_title),
                    "description": return_text_or_none(item_description),
                    "source": return_text_or_none(item_source),
                    "source_link": return_attrib_or_none(item_source_link, "url"),
                    "pub_date": convert_str_to_datetime(
                        return_text_or_none(item_pub_date)
                    ),
                    "image_url": return_attrib_or_none(item_image_url, "href"),
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
