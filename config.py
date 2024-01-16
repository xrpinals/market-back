#!/usr/bin/env python
# encoding: utf-8
import os

from dotenv import load_dotenv


class BaseConfig:
    pass


class DevelopmentConfig(BaseConfig):
    load_dotenv()
    DATABASE_USER = os.environ.get("DEV_DB_USER")
    DATABASE_PASS = os.environ.get("DEV_DB_PASSWORD")
    DATABASE_HOST = os.environ.get("DEV_DB_HOST")
    DATABASE_PORT = int(os.environ.get("DEV_DB_PORT", 3306))
    DATABASE_NAME = os.environ.get("DEV_DB_NAME")
    DATABASE_CHARSET = os.environ.get("DEV_DB_CHARSET")


class ProductionConfig(BaseConfig):
    load_dotenv()
    DATABASE_USER = os.environ.get("PROD_DB_USER")
    DATABASE_PASS = os.environ.get("PROD_DB_PASSWORD")
    DATABASE_HOST = os.environ.get("PROD_DB_HOST")
    DATABASE_PORT = int(os.environ.get("PROD_DB_PORT", 3306))
    DATABASE_NAME = os.environ.get("PROD_DB_NAME")
    DATABASE_CHARSET = os.environ.get("PROD_DB_CHARSET")


configs = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


class Application(object):
    setting = None