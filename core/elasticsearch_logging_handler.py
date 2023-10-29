import logging
from elasticsearch import Elasticsearch
from datetime import datetime
import pytz
import json
from django.conf import settings


class ElasticsearchHandler(logging.Handler):
    def __init__(self, prefix="default", mapping=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = prefix
        self.mapping = mapping
        self.es = Elasticsearch(hosts=settings.ELASTICSEARCH_CONNECTION["hosts"])

    @property
    def get_index_name(self):
        current_date = datetime.now(tz=pytz.timezone("Asia/Tehran")).strftime(
            "%Y-%m-%d"
        )
        return f"{self.prefix}-{current_date}"

    def emit(self, record):
        print("start log")
        log_entry = json.loads(self.format(record))
        now = datetime.now(tz=pytz.timezone("Asia/Tehran"))
        timestamp = now.strftime("%Y-%m-%dT%H:%M:%S")
        log_entry.update({"log_level": record.levelname, "timestamp": timestamp})
        try:
            self.es.indices.create(index=self.get_index_name, body=self.mapping)
        except Exception as e:
            print(e)
            pass
        self.es.index(index=self.get_index_name, document=log_entry)
        print("end log")
