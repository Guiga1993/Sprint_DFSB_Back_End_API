import logging
import os
from logging.config import dictConfig

# Directory where all log files are stored.
log_path = "logs/h2_system/"

# Ensure the log directory exists before handlers are initialized.
if not os.path.exists(log_path):
    os.makedirs(log_path, exist_ok=True)

# Centralized logging configuration for console + one rotating file.
dictConfig(
    {
        # Logging schema version required by dictConfig.
        "version": 1,
        # Keep third-party loggers active (e.g., Werkzeug request logs).
        "disable_existing_loggers": False,
        "formatters": {
            # Standard formatter for console output.
            "console_standard": {
                "format": "[%(asctime)s] %(levelname)-7s %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            # Detailed formatter for persisted file logs (adds source file and line).
            "file_detailed": {
                "format": (
                    "[%(asctime)s] %(levelname)-7s "
                    "[%(filename)s:%(lineno)d] - %(message)s"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            # Console handler for real-time local development visibility.
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console_standard",
                "stream": "ext://sys.stdout",
            },
            # Single rotating file handler for all application log levels.
            "application_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "file_detailed",
                "filename": os.path.join(log_path, "activity.log"),
                "maxBytes": 2097152,  # 2MB limit
                "backupCount": 5,
                "encoding": "utf-8",
            },
        },
        # Root logger routes all logs to console + the single file.
        "root": {
            "handlers": ["console", "application_file"],
            "level": "INFO",  # Capture INFO, WARNING, ERROR, and CRITICAL
        },
    }
)

# Application-level named logger used across API endpoints.
logger = logging.getLogger("H2_Generator_API")