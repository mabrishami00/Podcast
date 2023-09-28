from celery import shared_task
from .parser import parser_for_rss_podcast


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=10)
def parallel_parsing(self, url):
    parser_for_rss_podcast(url)

