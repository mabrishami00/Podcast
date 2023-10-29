from datetime import datetime
import pytz
import json
from .publishers import NotificationPublisher
from django.conf import settings

def publish_update_message(user_id, activity, message_type):
    body = {
        "user_id": user_id,
        "activity": activity,
        "message_type": message_type,
    }
    np = NotificationPublisher(
        settings.RABBITMQ_EXCHANGES[0], settings.RABBITMQ_QUEUES[0]
    )

    np.publish(body=body)


def publish_uo_message(user_id, activity, message_type):
    body = {
        "user_id": user_id,
        "activity": activity,
        "message_type": message_type,
    }
    np = NotificationPublisher(
        settings.RABBITMQ_EXCHANGES[1], settings.RABBITMQ_QUEUES[1]
    )
    np.publish(body=body)
