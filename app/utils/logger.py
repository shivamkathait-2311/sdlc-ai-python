# app/utils/logger.py
import logging
import sys
from typing import Optional

def setup_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Configure and return a logger with the given name.
    
    Args:
        name: Name of the logger
        level: Logging level (defaults to INFO if not specified)
    
    Returns:
        Configured logger instance
    """
    if level is None:
        level = logging.INFO
        
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers if logger already exists
    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

# Create loggers for different components
api_logger = setup_logger('api')

# Sample usage:
# redpanda_logger.info("Connected to Redpanda broker")
# data_processor_logger.error("Failed to process message", exc_info=True)