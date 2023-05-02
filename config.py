import os
import logging
from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG = False
    LOG_LEVEL = logging.INFO


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = logging.DEBUG


class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = logging.WARNING


def config():
    if os.getenv("FLASK_DEBUG", "1") != "1":
        return ProductionConfig
    return DevelopmentConfig


def configure_logging(cfg):
    logging.basicConfig(level=cfg.LOG_LEVEL)
