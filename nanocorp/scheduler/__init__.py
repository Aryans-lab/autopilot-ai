"""
NanoCorp v3.0 - Scheduler

Cron-based task scheduling and execution.
"""
from __future__ import annotations

import asyncio
import re
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from croniter import croniter


class ScheduleType(Enum):
    """Schedule types."""
    ONCE = "once"
    CRON = "cron"
    INTERVAL = "interval"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class ScheduledTask:
    """A scheduled task."""
    id: str
    name: str
    func: Callable
    schedule_type: ScheduleType
    schedule: str  # cron expr, interval, or datetime
    
    enabled: bool = True
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    run_count: int = 0
    error_count: int = 0
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_next_run(self) -> Optional[datetime]:
        """Calculate next run time."""
        try:
            if self.schedule_type == ScheduleType.CRON:
                iter = croniter(self.schedule, datetime.now())
                return iter.get_next(datetime)
            elif self.schedule_type == ScheduleType.INTERVAL:
                minutes = int(self.schedule)
                return datetime.now() + timedelta(minutes=minutes)
            elif self.schedule_type == ScheduleType.DAILY:
                # Parse time (HH:MM)
                hour, minute = map(int, self.schedule.split(":"))
                next_run = datetime.now().replace(hour=hour, minute=minute, second=0)
                if next_run <= datetime.now():
                    next_run += timedelta(days=1)
                return next_run
            elif self.schedule_type == ScheduleType.ONCE:
                return datetime.fromisoformat(self.schedule)
        except:
            pass
        return None


class TaskScheduler:
    """
    Task scheduler with cron support.
    
    Features:
    - Cron expressions
    - Intervals
    - One-time tasks
    - Daily/weekly schedules
    """
    
    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self._running = False
        self._loop_task: Optional[asyncio.Task] = None
    
    def add_task(
        self,
        name: str,
        func: Callable,
        schedule_type: ScheduleType,
        schedule: str,
        task_id: Optional[str] = None,
        **metadata
    ) -> str:
        """
        Add a scheduled task.
        
        Args:
            name: Task name
            func: Function to execute
            schedule_type: Type of schedule
            schedule: Schedule expression
            task_id: Optional task ID
        
        Returns:
            Task ID
        """
        tid = task_id or f"task_{len(self.tasks) + 1}"
        
        task = ScheduledTask(
            id=tid,
            name=name,
            func=func,
            schedule_type=schedule_type,
            schedule=schedule,
            metadata=metadata
        )
        
        task.next_run = task.get_next_run()
        self.tasks[tid] = task
        
        return tid
    
    def add_cron(
        self,
        name: str,
        func: Callable,
        cron_expr: str,
        **metadata
    ) -> str:
        """Add a cron task."""
        return self.add_task(name, func, ScheduleType.CRON, cron_expr, **metadata)
    
    def add_interval(
        self,
        name: str,
        func: Callable,
        minutes: int,
        **metadata
    ) -> str:
        """Add an interval task."""
        return self.add_task(name, func, ScheduleType.INTERVAL, str(minutes), **metadata)
    
    def add_daily(
        self,
        name: str,
        func: Callable,
        time: str = "09:00",
        **metadata
    ) -> str:
        """Add a daily task."""
        return self.add_task(name, func, ScheduleType.DAILY, time, **metadata)
    
    def add_once(
        self,
        name: str,
        func: Callable,
        datetime_str: str,
        **metadata
    ) -> str:
        """Add a one-time task."""
        return self.add_task(name, func, ScheduleType.ONCE, datetime_str, **metadata)
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a scheduled task."""
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False
    
    def enable_task(self, task_id: str) -> bool:
        """Enable a task."""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = True
            return True
        return False
    
    def disable_task(self, task_id: str) -> bool:
        """Disable a task."""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = False
            return True
        return False
    
    async def execute_task(self, task: ScheduledTask) -> Dict:
        """Execute a scheduled task."""
        try:
            result = task.func()
            
            # Handle async functions
            if asyncio.iscoroutinefunction(task.func):
                result = await result
            
            task.last_run = datetime.now().isoformat()
            task.run_count += 1
            task.next_run = task.get_next_run()
            
            return {"success": True, "result": result}
            
        except Exception as e:
            task.error_count += 1
            return {"success": False, "error": str(e)}
    
    async def start(self):
        """Start the scheduler."""
        self._running = True
        self._loop_task = asyncio.create_task(self._run_loop())
    
    async def stop(self):
        """Stop the scheduler."""
        self._running = False
        if self._loop_task:
            self._loop_task.cancel()
    
    async def _run_loop(self):
        """Main scheduler loop."""
        while self._running:
            now = datetime.now()
            
            # Check each task
            for task in self.tasks.values():
                if not task.enabled:
                    continue
                
                if task.next_run and now >= task.next_run:
                    # Execute task
                    result = await self.execute_task(task)
                    
                    # Remove one-time tasks that have run
                    if task.schedule_type == ScheduleType.ONCE:
                        self.remove_task(task.id)
            
            # Sleep for a second
            await asyncio.sleep(1)
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status."""
        return {
            "running": self._running,
            "total_tasks": len(self.tasks),
            "enabled_tasks": len([t for t in self.tasks.values() if t.enabled]),
            "tasks": [
                {
                    "id": t.id,
                    "name": t.name,
                    "schedule_type": t.schedule_type.value,
                    "schedule": t.schedule,
                    "enabled": t.enabled,
                    "next_run": t.next_run.isoformat() if t.next_run else None,
                    "last_run": t.last_run,
                    "run_count": t.run_count
                }
                for t in self.tasks.values()
            ]
        }


# Global scheduler
_scheduler: Optional[TaskScheduler] = None

def get_scheduler() -> TaskScheduler:
    """Get global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = TaskScheduler()
    return _scheduler
