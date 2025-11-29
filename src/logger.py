"""
Professional Logging System for WhatsApp Automation Bot
Provides colored console output and file logging with rotation
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

# ANSI color codes for terminal output
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Log level colors
    DEBUG = '\033[36m'      # Cyan
    INFO = '\033[32m'       # Green
    WARNING = '\033[33m'    # Yellow
    ERROR = '\033[31m'      # Red
    CRITICAL = '\033[35m'   # Magenta
    
    # Component colors
    TIMESTAMP = '\033[90m'  # Gray
    NAME = '\033[34m'       # Blue
    MESSAGE = '\033[0m'     # Default


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for console"""
    
    LEVEL_COLORS = {
        logging.DEBUG: Colors.DEBUG,
        logging.INFO: Colors.INFO,
        logging.WARNING: Colors.WARNING,
        logging.ERROR: Colors.ERROR,
        logging.CRITICAL: Colors.CRITICAL,
    }
    
    def format(self, record):
        # Get the color for this log level
        color = self.LEVEL_COLORS.get(record.levelno, Colors.RESET)
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Build colored message (using ASCII pipe for Windows compatibility)
        formatted = (
            f"{Colors.TIMESTAMP}{timestamp}{Colors.RESET} "
            f"{color}{Colors.BOLD}[{record.levelname:^8}]{Colors.RESET} "
            f"{Colors.NAME}{record.name:>15}{Colors.RESET} | "
            f"{color}{record.getMessage()}{Colors.RESET}"
        )
        
        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{Colors.ERROR}{self.formatException(record.exc_info)}{Colors.RESET}"
        
        return formatted


class FileFormatter(logging.Formatter):
    """Clean formatter for file output (no colors)"""
    
    def format(self, record):
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        formatted = f"{timestamp} [{record.levelname:^8}] {record.name:>15} | {record.getMessage()}"
        
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


class LogManager:
    """Centralized log management for the application"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if LogManager._initialized:
            return
        
        LogManager._initialized = True
        
        # Create logs directory
        self.log_dir = Path(__file__).parent.parent / 'logs'
        self.log_dir.mkdir(exist_ok=True)
        
        # Configure root logger
        self.root_logger = logging.getLogger()
        self.root_logger.setLevel(logging.DEBUG)
        
        # Remove default handlers
        self.root_logger.handlers.clear()
        
        # Setup handlers
        self._setup_console_handler()
        self._setup_file_handler()
        self._setup_error_file_handler()
        
        # Reduce noise from external libraries
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        logging.getLogger('selenium').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('apscheduler').setLevel(logging.WARNING)
    
    def _setup_console_handler(self):
        """Setup colored console output"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ColoredFormatter())
        self.root_logger.addHandler(console_handler)
    
    def _setup_file_handler(self):
        """Setup rotating file handler for all logs"""
        log_file = self.log_dir / 'app.log'
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(FileFormatter())
        self.root_logger.addHandler(file_handler)
    
    def _setup_error_file_handler(self):
        """Setup separate file for errors only"""
        error_file = self.log_dir / 'error.log'
        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(FileFormatter())
        self.root_logger.addHandler(error_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger with the specified name"""
        return logging.getLogger(name)


# Initialize log manager singleton
log_manager = LogManager()


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module/component.
    
    Usage:
        from src.logger import get_logger
        logger = get_logger('whatsapp_bot')
        logger.info("Bot initialized")
        logger.error("Failed to send message", exc_info=True)
    """
    return log_manager.get_logger(name)


# Convenience loggers for common components
app_logger = get_logger('app')
bot_logger = get_logger('whatsapp_bot')
db_logger = get_logger('database')
scheduler_logger = get_logger('scheduler')
