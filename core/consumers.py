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


class UpdateConsumerCallback(Callback):
    def callback(self, ch, method, properties, body):
        body_dict = json.loads(body)
        message_type = body_dict.get("message_type")
        channel_id = body_dict.get("activity").split(" ")[0]
        body_dict["activity"] = f"{message_type} Task is going to be consumed!"
        logger.info(json.dumps(body_dict))
        channel = Channel.objects.get(id=channel_id)
        email_operation = {
            "update_podcast": f"{channel.title} has new episode. Check it now!",
            "update_news": f"{channel.title} has been updated recently. Check it now!!",
        }
        users = Subscribe.get_all_users_subscribe_channel(channel)
        for user in users:
            recipient = user.email
            subject = message_type
            message = email_operation.get(message_type)
            sender_email = settings.EMAIL_HOST_USER

            send_mail(
                subject,
                message,
                sender_email,
                [recipient],
                fail_silently=False,
            )

        body_dict["activity"] = f"{message_type} Task consumed successfully!"
        logger.info(json.dumps(body_dict))

        ch.basic_ack(delivery_tag=method.delivery_tag)


class UserOperationCallback(Callback):
    def callback(self, ch, method, properties, body):
        body_dict = json.loads(body)

        message_type = body_dict.get("message_type")
        user_id = body_dict.get("user_id")

        body_dict["activity"] = f"{message_type} Task is going to be consumed!"
        logger.info(json.dumps(body_dict))
        user = User.objects.get(id=user_id)
        Notification.objects.create(user=user, message=message_type)
        obj, created = UserLastActivity.objects.update_or_create(
            user=user,
            defaults={"activity": message_type},
        )
        email_operation = {
            "register": "Your account has been registered successfully!",
            "change_password": "Your password has been changed successfully!",
        }
        if message_type in email_operation.keys():
            recipient = user.email
            subject = message_type
            message = email_operation.get(message_type)
            sender_email = settings.EMAIL_HOST_USER

            send_mail(
                subject,
                message,
                sender_email,
                [recipient],
                fail_silently=False,
            )
        body_dict["activity"] = f"{message_type} Task consumed successfully!"
        logger.info(json.dumps(body_dict))
        ch.basic_ack(delivery_tag=method.delivery_tag)
