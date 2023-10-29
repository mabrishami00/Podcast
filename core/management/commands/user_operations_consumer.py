from django.core.management.base import BaseCommand, CommandError
from core.consumers import Consumer, UserOperationCallback
from django.conf import settings


class Command(BaseCommand):
    help = "start the consumer"

    def handle(self, *args, **options):
        consumer = Consumer(settings.RABBITMQ_QUEUES[1])
        consumer.set_callback(UserOperationCallback())
        self.stdout.write(self.style.SUCCESS("Consumer has been started successfully!"))
        consumer.start()

