# -*- coding: utf-8 -*-
import os


def _to_boolean(val):
    if val is not None and val.lower() in ["true", "t", "on", "y", "yes"]:
        return True
    return False


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    APP_ROOT = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_ROOT, os.pardir))
    SECRET_KEY = os.getenv("SECRET_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
    AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
    SAFE_URLS = set(os.getenv("SAFE_URLS", "").split(","))
    AUTHENTICATION_ON = _to_boolean(os.getenv("AUTHENTICATION_ON", None))
    MAX_DEVELOPMENT_PLANS = int(os.getenv("MAX_DEVELOPMENT_PLANS", 10))
    PLANNING_DATA_API_URL = os.getenv(
        "PLANNING_DATA_API_URL", "https://www.planning.data.gov.uk"
    )
    WTF_CSRF_ENABLED = True
    MAX_CONTENT_LENGTH = 1024 * 1024
    ALLOWED_EXTENSIONS = ["zip"]


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = "development"
    WTF_CSRF_ENABLED = False
    AUTHENTICATION_ON = True


class TestConfig(Config):
    ENV = "test"
    DEBUG = True
    TESTING = True
