import json
from typing import Dict

from flask import current_app

from mib.events.channels import (
    PUBLISH_CHANNEL_WITHDRAW_POINTS,
    PUBLISH_CHANNEL_ADD_MESSAGE_NOTIFICATIONS,
)
from mib.events.redis_setup import get_redis


class EventPublishers:
    @classmethod
    def publish_withdraw_points(cls, msg: Dict):
        if "users" not in msg:
            return None
        else:
            return get_redis(current_app).publish(
                PUBLISH_CHANNEL_WITHDRAW_POINTS, json.dumps(msg)
            )

    @classmethod
    def publish_add_notify(cls, msg: Dict):
        if "notifications" not in msg:
            return None
        else:
            return get_redis(current_app).publish(
                PUBLISH_CHANNEL_ADD_MESSAGE_NOTIFICATIONS, json.dumps(msg)
            )
