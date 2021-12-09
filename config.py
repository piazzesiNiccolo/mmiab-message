import os


class Config(object):
    DEBUG = False
    TESTING = False

    UPLOAD_FOLDER = os.path.join("/static", "assets")
    UNSAFE_WORDS_FOLDER = os.path.join("/static", "txt")
    REQUESTS_TIMEOUT_SECONDS = float(os.getenv("REQUESTS_TIMEOUT_SECONDS", 5))
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", 6379)
    REDIS_DB = os.getenv("REDIS_DB", 0)

    # users microservice
    USERS_MS_PROTO = os.getenv("USERS_MS_PROTO", "http")
    USERS_MS_HOST = os.getenv("USERS_MS_HOST", "localhost")
    USERS_MS_PORT = os.getenv("USERS_MS_PORT", 5000)
    USERS_MS_URL = "%s://%s:%s" % (USERS_MS_PROTO, USERS_MS_HOST, USERS_MS_PORT)


class DebugConfig(Config):
    """
    This is the main configuration object for application.
    """

    DEBUG = True
    TESTING = False

    SECRET_KEY = b"isreallynotsecretatall"

    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///../db.sqlite"
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class DevConfig(DebugConfig):
    """
    This is the main configuration object for application.
    """

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    """
    This is the main configuration object for application.
    """

    TESTING = True

    import os

    SECRET_KEY = os.urandom(24)
    WTF_CSRF_ENABLED = False

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(DevConfig):
    """
    This is the main configuration object for application.
    """

    TESTING = False
    DEBUG = False

    import os

    SECRET_KEY = os.getenv("APP_SECRET_KEY", os.urandom(24))

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTGRES_USER = os.getenv("POSTGRES_USER", None)
    POSTGRES_PASS = os.getenv("POSTGRES_PASSWORD", None)
    POSTGRES_DB = os.getenv("POSTGRES_DB", None)
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", None)
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    SQLALCHEMY_DATABASE_URI = "postgres://%s:%s@%s:%s/%s" % (
        POSTGRES_USER,
        POSTGRES_PASS,
        POSTGRES_HOST,
        POSTGRES_PORT,
        POSTGRES_DB,
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
