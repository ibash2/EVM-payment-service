import os
import logging
import logging.config
import logging.handlers

# import logging_loki
from pydantic import PostgresDsn
from multiprocessing import Queue
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    POSTGRES_NAME: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str

    DATABASE_URL: PostgresDsn

    LOG_LEVEL: str = "INFO"


settings = Config()

# def loki_handler_factory():
#     return logging_loki.LokiQueueHandler(
#         queue=Queue(-1),
#         url=f"{settings.LOKI_URL}/loki/api/v1/push",
#         tags={"application": "my-app"},
#         version="1"
#     )


# class TagsFilter(logging.Filter):
#     def filter(self, record):
#         if not hasattr(record, 'tags'):
#             record.tags = {}
            
#             exclude_attrs = set(vars(logging.LogRecord('', '', '', '', '', '', '', '')))
#             extra_attrs = set(vars(record)) - exclude_attrs
#             for attr in extra_attrs:
#                 if attr != 'tags':
#                     value = getattr(record, attr)
#                     record.tags[attr] = value

#                     if not isinstance(value, str):
#                         record.tags[attr] = str(value)

#                     delattr(record, attr)
#             record.tags["thread"] = f"{record.thread}"
#         return True
    
    
logger_conf = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s : %(levelname)-8s %(filename)s  %(funcName)s:%(lineno)d  %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        }, 
        "file": {
            "class": "logging.FileHandler",
            "formatter": "standard",
            "filename": "logs/all.log",
            "mode": "w"
        },
        "rotation_file": {
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/all_rotation.log',
            'maxBytes': 1024*1024*500, # 500 MB
            'backupCount': 5, # 5 logs files will be kept
            'encoding': 'utf8'
        },
        # "loki": {
        #     "()": loki_handler_factory,
        #     "formatter": "standard",
        #     "filters": ["tags_filter"]
        # }
    },
    # "filters": {
    #     "tags_filter": {
    #         "()": TagsFilter
    #     }
    # },
    'root': {
        'handlers': ["console"],
        'level': settings.LOG_LEVEL,
    },
    "loggers": {
        "daemon": {
            "handlers": ["file", "rotation_file"],
            "level": settings.LOG_LEVEL
        }
    }
}

logging.config.dictConfig(logger_conf)
