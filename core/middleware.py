from elasticsearch import Elasticsearch
from datetime import datetime
from django.conf import settings
import logging
from .elasticsearch_logging_handler import ElasticsearchHandler
import json
import pytz
from core.mappings import mapping_middleware


logger = logging.getLogger("elasticsearch_middleware")
handler = ElasticsearchHandler("middleware", mapping_middleware)
logger.addHandler(handler)


class TrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        before view being executed.
        """
        user_id = request.user.id or None
        now = datetime.now(tz=pytz.timezone("Asia/Tehran"))
        request_time = now.strftime("%Y-%m-%dT%H:%M:%S")
        url_path = request.path
        http_method = request.method
        ip_address = request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT")

        response = self.get_response(request)

        """ 
        after view being executed.
        """

        # user_id = request.user.id if request.user.is_authenticated else None
        status_code = response.status_code
        response_time = now.strftime("%Y-%m-%dT%H:%M:%S")

        body = {
            "user_id": user_id,
            "request_time": request_time,
            "url_path": url_path,
            "http_method": http_method,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "status_code": status_code,
            "response_time": response_time,
        }

        logger.info(json.dumps(body))

        return response
