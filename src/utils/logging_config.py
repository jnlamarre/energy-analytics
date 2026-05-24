import logging
import os
from typing import Optional


def setup_basic_logging(logger_name: str, log_file: str) -> logging.Logger:
    """
    Setup basic logging configuration with INFO level and simple format.
    
    Args:
        logger_name: Name of the logger
        log_file: Path to the log file
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(logger_name)
    
    # Prevent duplicate handlers if logger already exists
    if logger.handlers:
        return logger
        
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logger


def setup_advanced_logging(logger_name: str, log_file: str) -> logging.Logger:
    """
    Setup advanced logging configuration with multiple handlers and levels.
    
    Features:
    - DEBUG level logging to file
    - WARNING+ level logging to console
    - Detailed formatter with logger name
    - UTF-8 encoding for French characters
    
    Args:
        logger_name: Name of the logger
        log_file: Path to the log file
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(logger_name)
    
    # Prevent duplicate handlers if logger already exists
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.DEBUG)

    # Create detailed formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console handler: WARNING+ level only
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler: DEBUG+ level (all messages)
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_pipeline_logger(pipeline_name: str, log_file: str | None = None) -> logging.Logger:
    """
    Get a logger configured for pipeline operations.
    
    Args:
        pipeline_name: Name of the pipeline (e.g., 'consumption', 'stations')
        log_file: Optional custom log file path
        
    Returns:
        Configured logger instance for the pipeline
    """
    if log_file is None:
        # Default log file in logs directory
        log_file = f"../logs/{pipeline_name}.log"
    
    logger_name = f"{pipeline_name}_pipeline"
    return setup_advanced_logging(logger_name, log_file)


def get_main_logger(log_file: str = "../logs/main.log") -> logging.Logger:
    """
    Get the main application logger for coordinating all pipelines.
    
    Args:
        log_file: Path to the main log file
        
    Returns:
        Configured main logger instance
    """
    return setup_advanced_logging("main_pipeline", log_file)


if __name__ == '__main__':
    # Test the logging configuration
    test_logger = setup_advanced_logging("test", "../logs/test.log")
    test_logger.debug("Debug message test")
    test_logger.info("Info message test")
    test_logger.warning("Warning message test")
    test_logger.error("Error message test")