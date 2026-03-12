from logging.config import dictConfig
import logging
import os

# Define the directory where your H2 system logs will be stored
log_path = "logs/h2_system/"

# Ensure the log directory exists to avoid "FileNotFound" errors
if not os.path.exists(log_path):
    os.makedirs(log_path)

dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        # Standard format for general monitoring
        "h2_standard": {
            "format": "[%(asctime)s] %(levelname)-7s %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        # Detailed format for debugging hardware/API failures
        "h2_debug": {
            "format": "[%(asctime)s] %(levelname)-7s [%(filename)s:%(lineno)d] - %(message)s"
        }
    },
    "handlers": {
        # Prints logs to your terminal while the API is running
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "h2_standard",
            "stream": "ext://sys.stdout",
        },
        # Dedicated file for critical safety/hardware errors
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "h2_debug",
            "filename": os.path.join(log_path, "system_errors.log"),
            "maxBytes": 1048576,  # 1MB limit per file
            "backupCount": 5,      # Keeps 5 old versions
        },
        # General file to track system activity (registrations, startups)
        "activity_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "h2_standard",
            "filename": os.path.join(log_path, "activity.log"),
            "maxBytes": 2097152,  # 2MB limit
            "backupCount": 3,
        }
    },
    "root": {
        "handlers": ["console", "activity_file", "error_file"],
        "level": "INFO", # Capture INFO, WARNING, ERROR, and CRITICAL
    }
})

# Create the logger instance to be used throughout the project
logger = logging.getLogger("H2_Generator_API")