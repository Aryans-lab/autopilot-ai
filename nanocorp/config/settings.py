"""
NanoCorp Configuration
Central configuration for the autonomous AI startup system
"""
import os
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class LLMConfig(BaseModel):
    """LLM Provider Configuration"""
    provider: str = Field(default_factory=lambda: os.getenv("LLM_PROVIDER", "openai"))
    model: str = Field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4o"))
    api_key: str = Field(default_factory=lambda: os.getenv("LLM_API_KEY", ""))
    base_url: Optional[str] = Field(default_factory=lambda: os.getenv("LLM_BASE_URL", None))
    temperature: float = 0.7
    max_tokens: int = 4096


class WorkspaceConfig(BaseModel):
    """Workspace Configuration"""
    root: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "workspace")
    projects_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "workspace" / "projects")
    output_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "workspace" / "output")
    
    def __init__(self, **data):
        super().__init__(**data)
        self.root.mkdir(parents=True, exist_ok=True)
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)


class EmailConfig(BaseModel):
    """Email Configuration"""
    smtp_host: str = Field(default_factory=lambda: os.getenv("SMTP_HOST", "smtp.gmail.com"))
    smtp_port: int = Field(default_factory=lambda: int(os.getenv("SMTP_PORT", "587")))
    smtp_user: str = Field(default_factory=lambda: os.getenv("SMTP_USER", ""))
    smtp_password: str = Field(default_factory=lambda: os.getenv("SMTP_PASSWORD", ""))
    from_name: str = Field(default_factory=lambda: os.getenv("EMAIL_FROM_NAME", "NanoCorp AI"))
    use_tls: bool = True


class SocialMediaConfig(BaseModel):
    """Social Media Configuration"""
    twitter_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("TWITTER_API_KEY", None))
    twitter_api_secret: Optional[str] = Field(default_factory=lambda: os.getenv("TWITTER_API_SECRET", None))
    linkedin_api_token: Optional[str] = Field(default_factory=lambda: os.getenv("LINKEDIN_API_TOKEN", None))


class BusinessConfig(BaseModel):
    """Business Configuration - Customize for your startup"""
    company_name: str = Field(default_factory=lambda: os.getenv("COMPANY_NAME", "NanoCorp"))
    company_description: str = "AI-powered autonomous business operating system"
    industry: str = Field(default_factory=lambda: os.getenv("INDUSTRY", "Technology"))
    target_market: str = Field(default_factory=lambda: os.getenv("TARGET_MARKET", "B2B SaaS"))
    email_domain: str = Field(default_factory=lambda: os.getenv("EMAIL_DOMAIN", "nanocorp.io"))
    
    # Brand Guidelines
    brand_name: str = "NanoCorp"
    brand_voice: str = "Professional, innovative, approachable"
    primary_color: str = "#2563EB"
    secondary_color: str = "#10B981"


class NanoCorpConfig(BaseModel):
    """Main NanoCorp Configuration"""
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Sub-configurations
    llm: LLMConfig = Field(default_factory=LLMConfig)
    workspace: WorkspaceConfig = Field(default_factory=WorkspaceConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)
    social_media: SocialMediaConfig = Field(default_factory=SocialMediaConfig)
    business: BusinessConfig = Field(default_factory=BusinessConfig)
    
    # Agent Settings
    max_concurrent_workers: int = 5
    task_timeout_seconds: int = 300
    enable_browser: bool = True
    debug_mode: bool = Field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    
    class Config:
        env_prefix = "NANOCORP_"


# Global config instance
config = NanoCorpConfig()


def get_config() -> NanoCorpConfig:
    """Get the global configuration instance"""
    return config


def update_business_info(
    company_name: str = None,
    company_description: str = None,
    industry: str = None,
    target_market: str = None
):
    """Update business configuration"""
    if company_name:
        config.business.company_name = company_name
    if company_description:
        config.business.company_description = company_description
    if industry:
        config.business.industry = industry
    if target_market:
        config.business.target_market = target_market
