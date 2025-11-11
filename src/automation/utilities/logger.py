import logging
import os
from logging.handlers import RotatingFileHandler

from automation.config.settings import settings


def setup_logger():
    # Ensure the directory for the log file exists
    log_dir = os.path.dirname(settings.LOG_FILE_PATH)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create a logger
    logger = logging.getLogger("automation_logger")
    logger.setLevel(logging.DEBUG)

    # Create a rotating file handler
    handler = RotatingFileHandler(
        settings.LOG_FILE_PATH, maxBytes=20 * 1024 * 1024, backupCount=5  # 20 MB per file, 5 backup files
    )

    # Create a formatter and set it for the handler
    formatter = logging.Formatter(
        "%(asctime)s - %(funcName)s:%(lineno)d - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # Add the handler to the logger
    if not logger.handlers:
        logger.addHandler(handler)

    return logger


# Initialize the logger
logger = setup_logger()
