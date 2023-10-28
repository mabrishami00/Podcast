mapping_middleware = {
    "mappings": {
        "properties": {
            "user_id": {"type": "integer"},
            "request_time": {"type": "date"},
            "url_path": {"type": "text"},
            "http_method": {"type": "keyword"},
            "ip_address": {"type": "ip"},
            "user_agent": {"type": "text"},
            "status_code": {"type": "integer"},
            "response_time": {"type": "date"},
            "log_level": {"type": "text"},
            "timestamp": {"type": "date"},
        }
    },
}

mapping_rabbitmq = {
    "mappings": {
        "properties": {
            "user_id": {"type": "integer"},
            "activity": {"type": "text"},
            "message_type": {"type": "keyword"},
            "log_level": {"type": "text"},
            "timestamp": {"type": "date"},
        }
    },
}

