"""
NanoCorp v3.0 - Unified Configuration System

Single source of truth for all configuration using Pydantic.
Supports environment variables and .env files.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Literal
from functools import lru_cache

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# ===========================================
# PATH CONFIGURATION
# ===========================================

def get_project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parent.parent.parent

def get_workspace_dir() -> Path:
    """Get workspace directory."""
    return Path(os.getenv("WORKSPACE_DIR", get_project_root() / "workspace"))

def get_data_dir() -> Path:
    """Get data directory."""
    return Path(os.getenv("DATA_DIR", get_project_root() / "data"))

def get_cache_dir() -> Path:
    """Get cache directory."""
    return Path(os.getenv("CACHE_DIR", get_project_root() / ".cache"))


# ===========================================
# AI CONFIGURATION
# ===========================================

class AIConfig(BaseModel):
    """AI provider configuration."""
    
    provider: Literal["auto", "claude", "openai", "ollama"] = "auto"
    model: str = "sonnet"
    
    # API Keys (optional for free mode)
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Free mode (CLI-based)
    free_mode: bool = True
    
    # Provider priorities
    provider_priority: List[str] = ["claude", "ollama", "openai"]


# ===========================================
# MCP CONFIGURATION  
# ===========================================

class MCPConfig(BaseModel):
    """MCP (Model Context Protocol) configuration."""
    
    enabled: bool = False
    servers: Dict[str, str] = Field(default_factory=dict)
    stdio_timeout: int = 30


# ===========================================
# MEMORY CONFIGURATION
# ===========================================

class MemoryConfig(BaseModel):
    """Memory and embedding configuration."""
    
    embedding_provider: Literal["sentence-transformers", "openai"] = "sentence-transformers"
    embedding_model: str = "all-MiniLM-L6-v2"
    openai_embedding_model: str = "text-embedding-3-small"
    
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_persist_dir: Path = Field(default_factory=lambda: get_cache_dir() / "chromadb")
    
    max_entries: int = 10000
    similarity_threshold: float = 0.3
    cache_embeddings: bool = True


# ===========================================
# INTEGRATIONS CONFIGURATION
# ===========================================

class IntegrationsConfig(BaseModel):
    """Third-party integrations configuration."""
    
    github_token: Optional[str] = None
    
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    email_from: str = "autopilot@nanocorp.ai"
    
    twitter_bearer_token: Optional[str] = None
    discord_webhook: Optional[str] = None
    slack_bot_token: Optional[str] = None
    slack_channel: str = "#general"
    
    vercel_token: Optional[str] = None
    netlify_token: Optional[str] = None


# ===========================================
# SKILLS CONFIGURATION
# ===========================================

class SkillsConfig(BaseModel):
    """Skills configuration."""
    
    enabled: bool = True
    tavily_api_key: Optional[str] = None
    linear_api_key: Optional[str] = None
    notion_token: Optional[str] = None
    notion_database_id: Optional[str] = None
    datadog_api_key: Optional[str] = None
    datadog_app_key: Optional[str] = None


# ===========================================
# EXECUTION CONFIGURATION
# ===========================================

class ExecutionConfig(BaseModel):
    """Execution sandbox and worker configuration."""
    
    sandbox_enabled: bool = True
    sandbox_timeout: int = 60
    sandbox_memory_limit: str = "512mb"
    sandbox_cpu_limit: int = 1
    
    max_workers: int = 10
    worker_timeout: int = 300
    
    task_retry_count: int = 3
    task_retry_delay: int = 5
    
    allowed_operations: List[str] = ["read", "write", "execute", "git", "http"]


# ===========================================
# API CONFIGURATION
# ===========================================

class APIConfig(BaseModel):
    """REST API server configuration."""
    
    enabled: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    api_key: Optional[str] = None
    
    ws_enabled: bool = False
    ws_port: int = 8001
    
    cors_origins: List[str] = ["*"]
    rate_limit: str = "100/minute"


# ===========================================
# LOGGING CONFIGURATION
# ===========================================

class LoggingConfig(BaseModel):
    """Logging configuration."""
    
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    format: Literal["json", "text"] = "text"
    
    file: Optional[Path] = None
    max_size: str = "100MB"
    backup_count: int = 5
    
    tracing_enabled: bool = False
    tracing_endpoint: Optional[str] = None
    metrics_enabled: bool = False


# ===========================================
# STORAGE CONFIGURATION
# ===========================================

class StorageConfig(BaseModel):
    """Storage paths configuration."""
    
    workspace_dir: Path = Field(default_factory=get_workspace_dir)
    data_dir: Path = Field(default_factory=get_data_dir)
    cache_dir: Path = Field(default_factory=get_cache_dir)


# ===========================================
# PROFILES
# ===========================================

class ProfilesConfig(BaseModel):
    """Feature profiles."""
    
    environment: Literal["development", "testing", "production"] = "development"
    
    profile_memory: bool = True
    profile_mcp: bool = True
    profile_skills: bool = True
    profile_api: bool = False
    
    debug: bool = False
    verbose: bool = False
    reload: bool = False


# ===========================================
# MAIN CONFIGURATION
# ===========================================

class Config(BaseSettings):
    """
    Main NanoCorp v3.0 configuration.
    
    Loads from environment variables with .env file support.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore"
    )
    
    ai: AIConfig = Field(default_factory=AIConfig)
    mcp: MCPConfig = Field(default_factory=MCPConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    integrations: IntegrationsConfig = Field(default_factory=IntegrationsConfig)
    skills: SkillsConfig = Field(default_factory=SkillsConfig)
    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    profiles: ProfilesConfig = Field(default_factory=ProfilesConfig)
    
    version: str = "3.0.0"


@lru_cache()
def _get_config_instance() -> Config:
    """Get cached config instance."""
    return Config()


def get_config() -> Config:
    """Get the global configuration instance."""
    return _get_config_instance()


# Convenience alias
config = _get_config_instance()


# Legacy compatibility
NanoCorpConfig = Config
