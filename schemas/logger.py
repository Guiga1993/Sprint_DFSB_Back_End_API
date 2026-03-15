import logging
import os
from logging.config import dictConfig

log_path = "logs/h2_system/"

if not os.path.exists(log_path):
    os.makedirs(log_path, exist_ok=True)

dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "h2_standard": {
                "format": "[%(asctime)s] %(levelname)-7s %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "h2_debug": {
                "format": (
                    "[%(asctime)s] %(levelname)-7s "
                    "[%(filename)s:%(lineno)d] - %(message)s"
                )
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "h2_standard",
                "stream": "ext://sys.stdout",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "h2_debug",
                "filename": os.path.join(log_path, "system_errors.log"),
                "maxBytes": 1048576,  # 1MB limit per file
                "backupCount": 5,  # Keeps 5 old versions
            },
            "activity_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "h2_standard",
                "filename": os.path.join(log_path, "activity.log"),
                "maxBytes": 2097152,  # 2MB limit
                "backupCount": 3,
            },
        },
        "root": {
            "handlers": ["console", "activity_file", "error_file"],
            "level": "INFO",  # Capture INFO, WARNING, ERROR, and CRITICAL
        },
    }
)

logger = logging.getLogger("H2_Generator_API")