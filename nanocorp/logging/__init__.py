"""
NanoCorp v3.0 - Structured Logging System

Context-aware logging with agent, task, and operation tracking.
"""
from __future__ import annotations

import logging
import json
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime
from contextvars import ContextVar
from logging.handlers import RotatingFileHandler

# Context variables for structured logging
agent_id: ContextVar[Optional[str]] = ContextVar("agent_id", default=None)
task_id: ContextVar[Optional[str]] = ContextVar("task_id", default=None)
operation: ContextVar[Optional[str]] = ContextVar("operation", default=None)


class StructuredFormatter(logging.Formatter):
    """JSON-structured log formatter."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add context
        if agent_id.get():
            log_data["agent_id"] = agent_id.get()
        if task_id.get():
            log_data["task_id"] = task_id.get()
        if operation.get():
            log_data["operation"] = operation.get()
        
        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        # Add exception info
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored console formatter for development."""
    
    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[35m", # Magenta
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        """Format with colors."""
        color = self.COLORS.get(record.levelname, "")
        reset = self.RESET
        
        # Add color codes
        record.levelname = f"{color}{record.levelname}{reset}"
        
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    format_type: str = "text",
    log_file: Optional[Path] = None,
    max_size: str = "100MB",
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up structured logging for NanoCorp.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Format type ("text" or "json")
        log_file: Optional file path for logging
        max_size: Max log file size
        backup_count: Number of backup files
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger("nanocorp")
    logger.setLevel(getattr(logging, level.upper()))
    logger.handlers.clear()
    
    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(getattr(logging, level.upper()))
    
    if format_type == "json":
        console.setFormatter(StructuredFormatter())
    else:
        console.setFormatter(ColoredFormatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%H:%M:%S"
        ))
    
    logger.addHandler(console)
    
    # File handler
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Parse size
        size = int(max_size.rstrip("MB")) * 1024 * 1024 if "MB" in max_size else 10 * 1024 * 1024
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=size,
            backupCount=backup_count
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(StructuredFormatter())
        logger.addHandler(file_handler)
    
    return logger


# Global logger instance
logger = logging.getLogger("nanocorp")


# ===========================================
# CONTEXT MANAGERS
# ===========================================

class LogContext:
    """Context manager for structured logging."""
    
    def __init__(
        self,
        agent: Optional[str] = None,
        task: Optional[str] = None,
        operation: Optional[str] = None,
        **extra
    ):
        self.agent = agent
        self.task = task
        self.operation = operation
        self.extra = extra
        self.tokens = []
    
    def __enter__(self):
        if self.agent:
            self.tokens.append(agent_id.set(self.agent))
        if self.task:
            self.tokens.append(task_id.set(self.task))
        if self.operation:
            self.tokens.append(operation.set(self.operation))
        return self
    
    def __exit__(self, *args):
        for token in self.tokens:
            token.reset()


# ===========================================
# HELPER FUNCTIONS
# ===========================================

def log_task_start(task_id: str, task_name: str, agent: Optional[str] = None):
    """Log task start."""
    with LogContext(task=task_id, agent=agent):
        logger.info(f"Task started: {task_name}")


def log_task_complete(task_id: str, task_name: str, duration: float, result: Any = None):
    """Log task completion."""
    with LogContext(task=task_id):
        logger.info(f"Task completed: {task_name} ({duration:.2f}s)")


def log_agent_action(agent_id: str, action: str, target: Optional[str] = None):
    """Log agent action."""
    with LogContext(agent=agent_id, operation=action):
        msg = f"Agent action: {action}"
        if target:
            msg += f" -> {target}"
        logger.info(msg)


def log_error(error: Exception, context: Optional[Dict] = None):
    """Log error with context."""
    extra = context or {}
    extra["error_type"] = type(error).__name__
    extra["error_message"] = str(error)
    
    logger.error(f"Error: {error}", extra=extra)


# ===========================================
# DECORATORS
# ===========================================

def log_calls(func):
    """Decorator to log function calls."""
    def wrapper(*args, **kwargs):
        logger.debug(f"Calling {func.__name__}({args}, {kwargs})")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            log_error(e, {"function": func.__name__})
            raise
    return wrapper
