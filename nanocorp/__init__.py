"""
NanoCorp v3.0 - The Ultimate Autonomous AI Agent System

Build and run your entire business with AI agents.

Example usage:
    from nanocorp import NanoCorp, quick_start
    
    # Quick start (recommended!)
    nano = quick_start("My Startup", "Build amazing products")
    nano.create_website("My Product", "landing")
    nano.autopilot(duration_seconds=60)

Architecture:
- CEO Agent: Strategic planning and coordination
- Workers: WebDev, Marketing, Email, Social, etc.
- Tools: Filesystem, Code, Web, etc.
- Memory: Vector embeddings with semantic search
- Skills: Tavily, GitHub, Slack, Linear integrations
- MCP: Model Context Protocol support
"""

__version__ = "3.0.0"

# Core system (free, no API key needed)
from .nanocorp_free import NanoCorpFree, quick_start

# Full system with all features
try:
    from .full_system import NanoCorpFull, quick_start_full
except (ImportError, Exception):
    NanoCorpFull = None
    quick_start_full = None

# Legacy compatibility
try:
    from .nanocorp import NanoCorp
except (ImportError, Exception):
    NanoCorp = None

# v3.0 Modules (lazy imports to avoid circular dependencies)
def _lazy_imports():
    global setup_logging, logger, LogContext
    global MCPClient, MCPRegistry, get_mcp_registry
    global BaseTool, ToolRegistry, get_tool_registry, get_tool_schemas, register_all_tools
    global AgentMemory
    global get_skill_registry, SkillRegistry
    
    from .logging import setup_logging, logger, LogContext
    from .mcp import MCPClient, MCPRegistry, get_registry as get_mcp_registry
    from .tools import (
        BaseTool, ToolRegistry, 
        get_registry as get_tool_registry,
        get_tool_schemas, register_all_tools,
    )
    from .memory import AgentMemory
    from .skills import get_skill_registry, SkillRegistry

__all__ = [
    "__version__",
    "NanoCorpFree",
    "NanoCorp",
    "NanoCorpFull",
    "quick_start",
    "quick_start_full",
]
