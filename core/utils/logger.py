import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(log_level=logging.INFO, log_file='app.log'):
    """
    Set up a custom logger with console and file handlers.
    
    Args:
        log_level (int): The logging level (e.g., logging.DEBUG, logging.INFO)
        log_file (str): The name of the log file
    
    Returns:
        logging.Logger: The configured logger object
    """
    # Create logs directory if it doesn't exist
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create a custom logger
    logger = logging.getLogger('AIAssistant')
    logger.setLevel(log_level)

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = RotatingFileHandler(os.path.join(log_dir, log_file), maxBytes=5*1024*1024, backupCount=3)
    c_handler.setLevel(log_level)
    f_handler.setLevel(log_level)

    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger

def get_logger():
    """
    Get the configured logger.
    
    Returns:
        logging.Logger: The configured logger object
    """
    return logging.getLogger('AIAssistant')