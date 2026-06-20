"""
Task Management System for NanoCorp
Handles task creation, assignment, tracking, and coordination
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from dataclasses import dataclass, field, asdict
import json
from pathlib import Path


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    WAITING_ON_DEPENDENCY = "waiting_on_dependency"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority levels"""
    CRITICAL = "critical"  # Must be done immediately
    HIGH = "high"          # Important, do soon
    MEDIUM = "medium"      # Normal priority
    LOW = "low"            # Can wait
    BACKLOG = "backlog"    # Future work


class TaskCategory(str, Enum):
    """Task categories for different business functions"""
    STRATEGY = "strategy"
    WEB_DEV = "web_dev"
    MARKETING = "marketing"
    SALES = "sales"
    CONTENT = "content"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    DOCUMENTATION = "documentation"
    RESEARCH = "research"
    NETWORKING = "networking"
    OPERATIONS = "operations"
    CUSTOM = "custom"


@dataclass
class Task:
    """Represents a work task in the system"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    category: TaskCategory = TaskCategory.CUSTOM
    
    # Assignment
    assigned_to: Optional[str] = None  # Agent name
    created_by: str = "system"
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)
    
    # Tracking
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        data['priority'] = self.priority.value
        data['category'] = self.category.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create from dictionary"""
        if isinstance(data.get('status'), str):
            data['status'] = TaskStatus(data['status'])
        if isinstance(data.get('priority'), str):
            data['priority'] = TaskPriority(data['priority'])
        if isinstance(data.get('category'), str):
            data['category'] = TaskCategory(data['category'])
        return cls(**data)


class TaskManager:
    """
    Central task management system
    Tracks all tasks, their status, and coordinates assignment
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.tasks: Dict[str, Task] = {}
        self.storage_path = storage_path
        if storage_path:
            self._load()
    
    def create_task(
        self,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        category: TaskCategory = TaskCategory.CUSTOM,
        assigned_to: Optional[str] = None,
        depends_on: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        created_by: str = "ceo"
    ) -> Task:
        """Create a new task"""
        task = Task(
            title=title,
            description=description,
            priority=priority,
            category=category,
            assigned_to=assigned_to,
            depends_on=depends_on or [],
            context=context or {},
            created_by=created_by
        )
        self.tasks[task.id] = task
        self._save()
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        return self.tasks.get(task_id)
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with a specific status"""
        return [t for t in self.tasks.values() if t.status == status]
    
    def get_tasks_by_agent(self, agent_name: str) -> List[Task]:
        """Get all tasks assigned to an agent"""
        return [t for t in self.tasks.values() if t.assigned_to == agent_name]
    
    def get_tasks_by_category(self, category: TaskCategory) -> List[Task]:
        """Get all tasks in a category"""
        return [t for t in self.tasks.values() if t.category == category]
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks sorted by priority"""
        pending = self.get_tasks_by_status(TaskStatus.PENDING)
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3,
            TaskPriority.BACKLOG: 4
        }
        return sorted(pending, key=lambda t: priority_order.get(t.priority, 5))
    
    def get_ready_tasks(self, agent_name: Optional[str] = None) -> List[Task]:
        """Get tasks that are ready to be worked on (no blocking dependencies)"""
        ready = []
        for task in self.get_pending_tasks():
            if task.depends_on:
                deps_complete = all(
                    self.tasks.get(dep_id) and 
                    self.tasks[dep_id].status == TaskStatus.COMPLETED
                    for dep_id in task.depends_on
                )
                if not deps_complete:
                    task.status = TaskStatus.WAITING_ON_DEPENDENCY
                    continue
            if agent_name and task.assigned_to and task.assigned_to != agent_name:
                continue
            ready.append(task)
        return ready
    
    def assign_task(self, task_id: str, agent_name: str) -> bool:
        """Assign a task to an agent"""
        task = self.tasks.get(task_id)
        if task:
            task.assigned_to = agent_name
            task.updated_at = datetime.now()
            self._save()
            return True
        return False
    
    def start_task(self, task_id: str) -> bool:
        """Mark a task as in progress"""
        task = self.tasks.get(task_id)
        if task:
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now()
            task.updated_at = datetime.now()
            self._save()
            return True
        return False
    
    def complete_task(self, task_id: str, result: Optional[Dict[str, Any]] = None) -> bool:
        """Mark a task as completed"""
        task = self.tasks.get(task_id)
        if task:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.updated_at = datetime.now()
            task.result = result
            self._save()
            return True
        return False
    
    def fail_task(self, task_id: str, error: str) -> bool:
        """Mark a task as failed"""
        task = self.tasks.get(task_id)
        if task:
            task.status = TaskStatus.FAILED
            task.error = error
            task.updated_at = datetime.now()
            self._save()
            return True
        return False
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        task = self.tasks.get(task_id)
        if task:
            task.status = TaskStatus.CANCELLED
            task.updated_at = datetime.now()
            self._save()
            return True
        return False
    
    def get_board_view(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get a Kanban-style board view of tasks"""
        board = {
            "backlog": [],
            "pending": [],
            "in_progress": [],
            "waiting": [],
            "completed": [],
            "failed": []
        }
        
        for task in self.tasks.values():
            task_dict = {
                "id": task.id,
                "title": task.title,
                "priority": task.priority.value,
                "assigned_to": task.assigned_to,
                "category": task.category.value
            }
            
            if task.status == TaskStatus.PENDING:
                board["pending"].append(task_dict)
            elif task.status == TaskStatus.IN_PROGRESS:
                board["in_progress"].append(task_dict)
            elif task.status == TaskStatus.WAITING_ON_DEPENDENCY:
                board["waiting"].append(task_dict)
            elif task.status == TaskStatus.COMPLETED:
                board["completed"].append(task_dict)
            elif task.status == TaskStatus.FAILED:
                board["failed"].append(task_dict)
            else:
                board["backlog"].append(task_dict)
        
        return board
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get task statistics"""
        total = len(self.tasks)
        completed = len(self.get_tasks_by_status(TaskStatus.COMPLETED))
        in_progress = len(self.get_tasks_by_status(TaskStatus.IN_PROGRESS))
        failed = len(self.get_tasks_by_status(TaskStatus.FAILED))
        pending = len(self.get_tasks_by_status(TaskStatus.PENDING))
        
        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "failed": failed,
            "pending": pending,
            "completion_rate": completed / total if total > 0 else 0
        }
    
    def _save(self):
        """Save tasks to disk"""
        if self.storage_path:
            data = {tid: task.to_dict() for tid, task in self.tasks.items()}
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
    
    def _load(self):
        """Load tasks from disk"""
        if self.storage_path and self.storage_path.exists():
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                self.tasks = {tid: Task.from_dict(tdata) for tid, tdata in data.items()}
    
    def __len__(self):
        return len(self.tasks)
    
    def __repr__(self):
        return f"TaskManager({len(self.tasks)} tasks)"
