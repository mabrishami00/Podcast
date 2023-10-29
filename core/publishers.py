import json
import pika
from django.conf import settings
import pytz
import logging
from datetime import datetime
from core.elasticsearch_logging_handler import ElasticsearchHandler
from core.mappings import mapping_rabbitmq
from django.conf import settings


logger = logging.getLogger("elasticsearch_rabbitmq")
handler = ElasticsearchHandler("rabbitmq", mapping_rabbitmq)
logger.addHandler(handler)


class NotificationPublisher:
    def __init__(self, exchange_name, queue_name):
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
        self.exchange_name = exchange_name
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=exchange_name, exchange_type="direct")
        self.channel.queue_declare(queue=queue_name)
        self.channel.queue_bind(
            exchange=exchange_name, queue=queue_name, routing_key=queue_name
        )

    def publish(self, body):
        body = json.dumps(body)
        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=self.queue_name,
            body=body,
            # properties=properties,
        )
        logger.info(body)
        self.connection.close()



