import os
import logging
import random
import requests
import config # Needed for create_app
from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from mib.dao.message_manager import MessageManager as MM
from mib.events.publishers import EventPublishers
_APP = None

# BACKEND = "redis://localhost:6379"
# BROKER = "redis://localhost:6379/0"
CELERY_REDIS_HOST = os.getenv("CELERY_REDIS_HOST", "localhost")
CELERY_REDIS_PORT = os.getenv("CELERY_REDIS_PORT", 6379)
CELERY_REDIS_DB = os.getenv("CELERY_REDIS_DB", 0)

BACKEND = f"redis://{CELERY_REDIS_HOST}:{CELERY_REDIS_PORT}"
BROKER = f"redis://{CELERY_REDIS_HOST}:{CELERY_REDIS_PORT}/{CELERY_REDIS_DB}"
celery = Celery(__name__, backend=BACKEND, broker=BROKER)

TaskBase = celery.Task


class ContextTask(TaskBase):  # pragma: no cover
    def __call__(self, *args, **kwargs):
        global _APP
        # lazy init
        if _APP is None:
            from mib import create_app

            app = _APP = create_app()
        else:
            app = _APP
        with app.app_context():
            return TaskBase.__call__(self, *args, **kwargs)


celery.Task = ContextTask

celery.conf.beat_schedule = {
    "arrived_messages": {"task": __name__ + ".arrived_messages", "schedule": 5.0},
}

@celery.task
def arrived_messages():  # pragma: nocover
    return _arrived_messages()

def _arrived_messages():
    message_list = MM.get_new_arrived_messages()
    payload = {
        "notifications":[]
    }
    for message in message_list:
        for recipient in message["recipients"]:
            payload["notifications"].append({
                "id_message":message["id"],
                "id_user":recipient,
                "for_recipient":True,
                "for_sender":False,
                "for_lottery":False,
                "from_recipient":None
            })
    EventPublishers.publish_add_notify(payload)
    
    return payload




