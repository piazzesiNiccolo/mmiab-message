import os
import logging
import random
import requests
from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from mib.dao.message_manager import MessageManager as MM

_APP = None

# BACKEND = "redis://localhost:6379"
# BROKER = "redis://localhost:6379/0"
BACKEND = "redis://rd01:6379"
BROKER = "redis://rd01:6379/0"  
USERS = None
celery = Celery(__name__, backend=BACKEND, broker=BROKER)

TaskBase = celery.Task


class ContextTask(TaskBase):  # pragma: no cover
    def __call__(self, *args, **kwargs):
        global _APP
        # global USERS
        # lazy init
        if _APP is None:
            from mib import create_app

            app = _APP = create_app()
            # USERS = _APP.config['USERS_MS_URL']
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
    _arrived_messages()

def _arrived_messages():
    message_list = MM.get_new_arrived_messages()

    # TODO: publish notifications for recipient
    #
    # old implementation:
    # for message in message_list:
    #     for recipient in message["recipients"]:
    #         # add notify for the receipent
    #         NotifyModel.add_notify(
    #             id_message=message["id"],
    #             id_user=recipient,
    #             for_recipient=True,
    #         )

    return message_list




