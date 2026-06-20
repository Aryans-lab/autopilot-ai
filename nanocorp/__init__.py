"""
NanoCorp - Autonomous AI Startup System

A complete AI-powered business automation system with:
- CEO Agent for strategic planning and coordination
- Specialized Worker Agents for different business functions
- Vector Memory with semantic search
- Self-Improvement Engine
- Real Integrations (Email, GitHub, Deploy, Social)
- Agent Spawning System
- FREE MODE - works without API keys!

Example usage:
    from nanocorp import NanoCorpFull, quick_start_full
    
    # Full system with all features!
    nano = quick_start_full("My Company", "Build amazing products")
    nano.create_website("My Product", "landing")
    nano.run()
    
    # Or use FREE mode
    from nanocorp import NanoCorpFree, quick_start
    nano = quick_start("My Company", "Build amazing products")
    nano.run()
"""

# Free version (always available)
from .nanocorp_free import NanoCorpFree, quick_start

# Full system with all features
try:
    from .full_system import NanoCorpFull, quick_start_full
    __all__ = ["NanoCorp", "NanoCorpFree", "NanoCorpFull", "quick_start", "quick_start_full"]
except ImportError:
    NanoCorpFull = None
    quick_start_full = None
    __all__ = ["NanoCorp", "NanoCorpFree", "quick_start"]

# Try to import premium features
try:
    from .nanocorp import NanoCorp
except ImportError:
    NanoCorp = None

# Core systems (optional)
try:
    from .core import OODALoop, AgentMemory, AutonomousGoalEngine, Goal
except ImportError:
    pass

# Advanced systems
from .vector_memory import VectorMemory, LearningEngine
from .integrations import IntegrationManager
from .agent_spawner import AgentSpawner

__version__ = "2.1.0"
__all__ += [
    "OODALoop", "AgentMemory", "AutonomousGoalEngine", "Goal",
    "VectorMemory", "LearningEngine",
    "IntegrationManager", "AgentSpawner"
]
