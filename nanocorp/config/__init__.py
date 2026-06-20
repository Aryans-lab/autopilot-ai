"""
Configuration module for NanoCorp v3.0
"""
from .settings import (
    Config,
    get_config,
    config,
    NanoCorpConfig,
    AIConfig,
    MCPConfig,
    MemoryConfig,
    IntegrationsConfig,
    SkillsConfig,
    ExecutionConfig,
    APIConfig,
    LoggingConfig,
    StorageConfig,
    ProfilesConfig,
)

# Module reference for convenience
settings = Config

__all__ = [
    "Config",
    "get_config", 
    "config",
    "NanoCorpConfig",
    "AIConfig",
    "MCPConfig",
    "MemoryConfig",
    "IntegrationsConfig",
    "SkillsConfig",
    "ExecutionConfig",
    "APIConfig",
    "LoggingConfig",
    "StorageConfig",
    "ProfilesConfig",
    "settings",
]
