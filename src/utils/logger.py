"""
Logging configuration for the QiLifeStore Social Media Engagement Bot.
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(log_file: str, log_level: str = "INFO") -> None:
    """
    Configure the application logger.
    
    Args:
        log_file: Path to the log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Get the numeric logging level
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # Clear existing handlers
    logger.handlers = []
    
    # Create formatters
    console_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s"
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Create file handler
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file_with_date = log_file.replace(".log", f"_{timestamp}.log")
    
    file_handler = RotatingFileHandler(
        log_file_with_date, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    logger.info(f"Logger initialized with level {log_level}")


def get_activity_logger(platform: str) -> logging.Logger:
    """
    Get a specialized logger for platform activities.
    
    Args:
        platform: The name of the platform (reddit, quora)
        
    Returns:
        Logger instance for the specified platform
    """
    logger_name = f"activity.{platform}"
    logger = logging.getLogger(logger_name)
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(Path(__file__).parent.parent.parent, "logs", "activity")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create specialized file handler for activity logging
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"{platform}_{timestamp}.log")
    
    # Check if we already set up this logger
    if not any(isinstance(h, RotatingFileHandler) and h.baseFilename == log_file 
              for h in logger.handlers):
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5*1024*1024, backupCount=3
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(message)s"
        ))
        logger.addHandler(file_handler)
    
    return logger 