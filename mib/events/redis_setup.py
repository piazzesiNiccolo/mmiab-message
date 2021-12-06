import redis
from fakeredis import FakeStrictRedis
from flask import Flask


def get_redis(app: Flask) -> redis.StrictRedis:  # pragma: no cover
    if app.config.get("TESTING"):
        _redis = FakeStrictRedis()

    else:
        _redis = redis.StrictRedis(
            host=app.config.get("REDIS_HOST", "localhost"),
            port=app.config.get("REDIS_PORT", 6379),
            db=app.config.get("REDIS_DB", 0),
        )
    return _redis
