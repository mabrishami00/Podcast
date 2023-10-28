from django.conf import settings
from django.core.mail import send_mail

from accounts.models import User, Notification, UserLastActivity
from rss.models import Channel
from interactions.models import Subscribe

from abc import ABC, abstractmethod
import pika
import json
import logging
import datetime
import pytz
from core.elasticsearch_logging_handler import ElasticsearchHandler
from core.mappings import mapping_rabbitmq


logger = logging.getLogger("elasticsearch_rabbitmq")
handler = ElasticsearchHandler("rabbitmq", mapping_rabbitmq)
logger.addHandler(handler)


class Callback(ABC):
    @abstractmethod
    def callback(self, ch, method, properties, body):
        pass


class Consumer(ABC):
    def __init__(self, queue_name):
        self.callback = None
        credentials = pika.PlainCredentials(
            settings.RABBITMQ_USERNAME, settings.RABBITMQ_PASSWORD
        )

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=settings.RABBITMQ_HOSTNAME,
                port=settings.RABBITMQ_PORT,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300,
            )
        )
        self.queue_name = queue_name
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue_name)
        self.channel.basic_qos(prefetch_count=5)

    def set_callback(self, callback: Callback):
        self.callback = callback

    def start(self):
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=self.callback.callback
        )
        self.channel.start_consuming()
