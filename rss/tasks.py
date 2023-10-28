from django.conf import settings

from .parser import parser_for_rss_podcast
from .models import Channel
from core.elasticsearch_logging_handler import ElasticsearchHandler

import logging
import pytz
import json
from celery import signals, group, shared_task, signature, Task
from elasticsearch import Elasticsearch
from datetime import datetime
from core.mappings import mapping_celery
from .utils import body_for_logger_celery

logger = logging.getLogger("elasticsearch_celery")
handler = ElasticsearchHandler("celery", mapping_celery)
logger.addHandler(handler)


class BaseTaskWithRetry(Task):
    autoretry_for = (Exception,)
    max_retries = 5
    retry_backoff = 2
    retry_backoff_max = 100
    retry_jitter = False


@shared_task(bind=True, base=BaseTaskWithRetry)
def parallel_parsing(self, url, user_id):
    parser_for_rss_podcast(url, user_id)


def update_all_channels(user_id):
    channels = Channel.objects.all()
    tasks_to_run = [
        signature(parallel_parsing, args=(channel.url, user_id)) for channel in channels
    ]
    result = group(tasks_to_run)()


@signals.before_task_publish.connect
def task_before_publish_handler(
    sender=None, headers=None, body=None, exchange=None, routing_key=None, **kwargs
):
    print("start before publish")
    body_log = body_for_logger_celery(body[0][0], "Task is going to be published!")
    logger.info(json.dumps(body_log))
    print("end before publish")


@signals.after_task_publish.connect
def task_after_publish_handler(sender=None, headers=None, body=None, **kwargs):
    print("start after publish")
    body_log = body_for_logger_celery(body[0][0], "Task is published successfully!")
    logger.info(json.dumps(body_log))
    print("end after publish")


