from django.core.management.base import BaseCommand, CommandError
from core.consumers import Consumer, UpdateConsumerCallback
from django.conf import settings
import time


class Command(BaseCommand):
    help = "start the consumer"

    def handle(self, *args, **options):
        consumer = Consumer(settings.RABBITMQ_QUEUES[0])
        consumer.set_callback(UpdateConsumerCallback())
        self.stdout.write(self.style.SUCCESS("Consumer has been started successfully!"))
        consumer.start()
