"""
NanoCorp v3.0 - Agent System

CEO and Worker agents with full tool access.
"""
# v3.0 Agents
from .base import BaseAgent, AgentType, AgentState, Message
from .ceo import CEOAgent
from .worker import WorkerAgent, CoderAgent, DesignerAgent, ResearcherAgent, MarketerAgent, WriterAgent, DataAgent, DevOpsAgent
from .manager import AgentManager, WorkforceStats

# Legacy imports for backward compatibility
from .ceo_agent import CEOSystem, WorkerAgent as LegacyWorkerAgent, CEO_SYSTEM_PROMPT
from .task_manager import TaskManager, Task, TaskStatus, TaskPriority, TaskCategory

__all__ = [
    # v3.0 Agents
    "BaseAgent",
    "AgentType",
    "AgentState",
    "Message",
    "CEOAgent",
    "WorkerAgent",
    "CoderAgent",
    "DesignerAgent",
    "ResearcherAgent",
    "MarketerAgent",
    "WriterAgent",
    "DataAgent",
    "DevOpsAgent",
    "AgentManager",
    "WorkforceStats",
    # Legacy
    "CEOSystem",
    "LegacyWorkerAgent",
    "CEO_SYSTEM_PROMPT",
    "TaskManager",
    "Task",
    "TaskStatus",
    "TaskPriority",
    "TaskCategory",
]
