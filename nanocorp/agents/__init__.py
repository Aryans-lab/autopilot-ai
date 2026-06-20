"""
NanoCorp v3.0 - Agent System

CEO and Worker agents with full tool access.
"""
from .base import BaseAgent, AgentType, AgentState, Message
from .ceo import CEOAgent
from .worker import WorkerAgent, CoderAgent, DesignerAgent, ResearcherAgent, MarketerAgent, WriterAgent, DataAgent, DevOpsAgent
from .manager import AgentManager, WorkforceStats
from .task_manager import TaskManager, Task, TaskStatus, TaskPriority, TaskCategory

__all__ = [
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
    "TaskManager",
    "Task",
    "TaskStatus",
    "TaskPriority",
    "TaskCategory",
]
