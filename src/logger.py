import logging
import logging.config
import logging.handlers

class Logger():
    @classmethod
    def get_auth_logger(cls):
        return logging.getLogger("daemon")