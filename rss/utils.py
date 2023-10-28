import pytz
from datetime import datetime


def body_for_logger_celery(info, activity):
    body_log = {
        "info": info,
        "activity": activity,
    }
    return body_log
