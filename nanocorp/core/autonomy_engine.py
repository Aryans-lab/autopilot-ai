"""
NanoCorp v5.0 - Autonomous Execution Engine

The heart of the autonomous startup. This engine coordinates:
- Continuous OODA loop operation
- Goal-driven task execution
- Dynamic worker orchestration
- Self-correction and adaptive replanning
- Real-time monitoring and observability

This is what makes NanoCorp truly autonomous - not just reactive, but proactive.
"""
from __future__ import annotations

import asyncio
import json
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, Type
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import traceback

from ..core.ooda import OODALoop, OODAPhase, Decision, Action, Outcome
from ..core.goals import GoalManager, Goal, Task
from ..agents.base import BaseAgent, AgentType


# ===========================================
# AUTONOMY STATES
# ===========================================

class AutonomyState(str, Enum):
    """System autonomy states"""
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    BLOCKED = "blocked"
    RECOVERING = "recovering"
    SHUTDOWN = "shutdown"


class ExecutionMode(str, Enum):
    """Execution modes for different operational contexts"""
    SINGLE_THREAD = "single_thread"  # One task at a time
    PARALLEL = "parallel"  # Multiple independent tasks
    PRIORITIZED = "prioritized"  # Priority-based scheduling
    ADAPTIVE = "adaptive"  # Dynamic based on workload


@dataclass
class ExecutionContext:
    """Current execution context for decision making"""
    active_goals: List[Goal] = field(default_factory=list)
    pending_tasks: List[Task] = field(default_factory=list)
    in_progress_tasks: List[Task] = field(default_factory=list)
    completed_tasks: List[Task] = field(default_factory=list)
    failed_tasks: List[Task] = field(default_factory=list)
    available_workers: Dict[str, BaseAgent] = field(default_factory=dict)
    busy_workers: Dict[str, str] = field(default_factory=dict)  # worker_id -> task_id
    resources: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ExecutionResult:
    """Result of task execution"""
    task_id: str
    success: bool
    output: Any
    duration: float
    artifacts: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AutonomyMetrics:
    """Comprehensive autonomy metrics"""
    total_goals: int = 0
    completed_goals: int = 0
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    avg_task_duration: float = 0.0
    success_rate: float = 1.0
    ooda_loops_run: int = 0
    decisions_made: int = 0
    actions_executed: int = 0
    recovery_events: int = 0
    parallel_efficiency: float = 0.0
    worker_utilization: Dict[str, float] = field(default_factory=dict)
    goal_velocity: float = 0.0  # goals per hour
    task_throughput: float = 0.0  # tasks per hour


# ===========================================
# AUTONOMOUS EXECUTION ENGINE
# ===========================================

class AutonomyEngine:
    """
    Core autonomous execution engine for NanoCorp.
    
    This engine:
    1. Runs continuous OODA loops for strategic decision-making
    2. Decomposes goals into executable tasks
    3. Orchestrates worker agents dynamically
    4. Monitors execution and handles failures
    5. Adapts strategy based on outcomes
    6. Maintains system health and performance
    
    Think of this as the central nervous system of the autonomous startup.
    """
    
    def __init__(
        self,
        ceo_agent: BaseAgent,
        goal_manager: GoalManager,
        ooda_loop: OODALoop,
        execution_mode: ExecutionMode = ExecutionMode.ADAPTIVE,
        max_parallel_tasks: int = 10,
        config: Optional[Dict[str, Any]] = None
    ):
        self.ceo = ceo_agent
        self.goal_manager = goal_manager
        self.ooda_loop = ooda_loop
        
        # Configuration
        self.execution_mode = execution_mode
        self.max_parallel_tasks = max_parallel_tasks
        self.config = config or {}
        
        # State management
        self.state = AutonomyState.IDLE
        self.is_running = False
        self.context = ExecutionContext()
        
        # Task management
        self.task_queue: deque = deque()
        self.active_tasks: Dict[str, Task] = {}
        self.completed_results: Dict[str, ExecutionResult] = {}
        
        # Worker management
        self.workers: Dict[str, BaseAgent] = {}
        self.worker_tasks: Dict[str, str] = {}  # worker_id -> task_id
        
        # Metrics and monitoring
        self.metrics = AutonomyMetrics()
        self.event_log: deque = deque(maxlen=1000)
        self.start_time: Optional[datetime] = None
        
        # Callbacks
        self._on_goal_start_callbacks: List[Callable] = []
        self._on_goal_complete_callbacks: List[Callable] = []
        self._on_task_start_callbacks: List[Callable] = []
        self._on_task_complete_callbacks: List[Callable] = []
        self._on_error_callbacks: List[Callable] = []
        self._on_state_change_callbacks: List[Callable] = []
        
        # Recovery configuration
        self.max_retries = self.config.get("max_retries", 3)
        self.retry_delay = self.config.get("retry_delay", 5.0)
        self.circuit_breaker_threshold = self.config.get("circuit_breaker_threshold", 5)
        self.failure_window = self.config.get("failure_window", 300)  # seconds
        
        # Circuit breaker state
        self.recent_failures: deque = deque()
        self.circuit_open = False
        self.circuit_open_until: Optional[datetime] = None
    
    # ===========================================
    # LIFECYCLE MANAGEMENT
    # ===========================================
    
    def start(self, initial_goal: Optional[str] = None):
        """Start the autonomous engine."""
        if self.is_running:
            return {"status": "already_running"}
        
        self.is_running = True
        self.state = AutonomyState.PLANNING
        self.start_time = datetime.now()
        
        self._log_event("engine_started", {
            "mode": self.execution_mode.value,
            "max_parallel": self.max_parallel_tasks,
            "initial_goal": initial_goal
        })
        
        # Add initial goal if provided
        if initial_goal:
            goal_id = self.goal_manager.add_goal(
                Goal(
                    id=f"goal_{uuid.uuid4().hex[:8]}",
                    objective=initial_goal,
                    priority="high"
                )
            )
            self._log_event("initial_goal_added", {"goal_id": goal_id, "objective": initial_goal})
        
        return {"status": "started", "state": self.state.value}
    
    def stop(self):
        """Stop the autonomous engine gracefully."""
        self.is_running = False
        self.state = AutonomyState.SHUTDOWN
        
        self._log_event("engine_stopped", {
            "uptime": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            "final_metrics": self.get_metrics()
        })
        
        return {"status": "stopped"}
    
    async def run_async(self, initial_goal: Optional[str] = None):
        """Main async execution loop."""
        self.start(initial_goal)
        
        while self.is_running and self.state != AutonomyState.SHUTDOWN:
            try:
                await self._execution_cycle()
                await asyncio.sleep(0.5)  # Prevent tight loop
            except Exception as e:
                self._handle_critical_error(e)
                await asyncio.sleep(5.0)  # Pause before retry
        
        return self.stop()
    
    def run_blocking(self, initial_goal: Optional[str] = None):
        """Run the engine in blocking mode (for testing)."""
        return asyncio.run(self.run_async(initial_goal))
    
    # ===========================================
    # MAIN EXECUTION CYCLE
    # ===========================================
    
    async def _execution_cycle(self):
        """
        One complete execution cycle:
        1. Observe current state
        2. Run OODA loop for strategic decisions
        3. Schedule and execute tasks
        4. Monitor and handle completions
        5. Update metrics and adapt
        """
        cycle_start = time.time()
        
        # Step 1: Build execution context
        self._update_context()
        
        # Step 2: Check circuit breaker
        if self._is_circuit_open():
            self.state = AutonomyState.BLOCKED
            self._log_event("circuit_breaker_open", {"reason": "too_many_failures"})
            return
        
        # Step 3: Run OODA loop for strategic decisions
        ooda_result = await self._run_ooda_decision_cycle()
        
        # Step 4: Process OODA decisions into actions
        if ooda_result.get("decision"):
            await self._process_decisions(ooda_result["decision"])
        
        # Step 5: Schedule ready tasks
        await self._schedule_ready_tasks()
        
        # Step 6: Execute scheduled tasks (based on mode)
        await self._execute_scheduled_tasks()
        
        # Step 7: Check for completed tasks
        await self._check_task_completions()
        
        # Step 8: Update metrics
        self._update_metrics()
        
        # Step 9: Handle blocked state
        if self._is_blocked():
            self.state = AutonomyState.BLOCKED
            await self._handle_blocked_state()
        
        cycle_duration = time.time() - cycle_start
        self._log_event("cycle_completed", {
            "duration": cycle_duration,
            "state": self.state.value,
            "active_tasks": len(self.active_tasks)
        })
    
    # ===========================================
    # CONTEXT & OBSERVATION
    # ===========================================
    
    def _update_context(self):
        """Update execution context from current system state."""
        # Goals
        self.context.active_goals = [
            g for g in self.goal_manager.goals if g.status == "active"
        ]
        
        # Tasks by status
        all_tasks = list(self.goal_manager.tasks.values()) if hasattr(self.goal_manager, 'tasks') and isinstance(self.goal_manager.tasks, dict) else self.goal_manager.tasks
        self.context.pending_tasks = [t for t in all_tasks if t.status == "pending"]
        self.context.in_progress_tasks = [t for t in all_tasks if t.status == "in_progress"]
        self.context.completed_tasks = [t for t in all_tasks if t.status == "completed"]
        self.context.failed_tasks = [t for t in all_tasks if t.status == "failed"]
        
        # Workers
        self.context.available_workers = {
            w_id: w for w_id, w in self.workers.items()
            if w_id not in self.worker_tasks
        }
        self.context.busy_workers = self.worker_tasks.copy()
        
        self.context.timestamp = datetime.now()
    
    # ===========================================
    # OODA INTEGRATION
    # ===========================================
    
    async def _run_ooda_decision_cycle(self) -> Dict[str, Any]:
        """Run one OODA loop cycle with full context."""
        # Prepare context for OODA
        ooda_context = {
            "task_status": {
                "pending": len(self.context.pending_tasks),
                "in_progress": len(self.context.in_progress_tasks),
                "completed": len(self.context.completed_tasks),
                "failed": len(self.context.failed_tasks)
            },
            "worker_status": {
                "available": len(self.context.available_workers),
                "busy": len(self.context.busy_workers),
                "utilization": len(self.context.busy_workers) / max(1, len(self.workers))
            },
            "goals": {
                "active": len(self.context.active_goals),
                "completed": self.metrics.completed_goals
            },
            "system_health": {
                "success_rate": self.metrics.success_rate,
                "circuit_breaker": self.circuit_open,
                "state": self.state.value
            },
            "recent_outcomes": list(self.completed_results.values())[-10:]
        }
        
        # Run OODA cycle
        try:
            result = self.ooda_loop.run_cycle(ooda_context)
            self.metrics.ooda_loops_run += 1
            
            self._log_event("ooda_cycle", {
                "phase": result.get("phase"),
                "confidence": result.get("confidence"),
                "decision": result.get("decision")
            })
            
            return result
        except Exception as e:
            self._log_event("ooda_error", {"error": str(e)})
            return {"decision": None}
    
    async def _process_decisions(self, decision: Decision):
        """Process OODA decision into concrete actions."""
        self.metrics.decisions_made += 1
        
        action_type = decision.selected_option.get("action", "")
        parameters = decision.selected_option.get("parameters", {})
        
        self._log_event("decision_processed", {
            "action": action_type,
            "rationale": decision.rationale
        })
        
        # Handle different decision types
        if action_type == "mitigate_threats":
            await self._handle_threats(parameters.get("threats", []))
        elif action_type == "seize_opportunity":
            await self._seize_opportunities(parameters.get("opportunities", []))
        elif action_type == "reallocate_resources":
            await self._reallocate_workers(parameters)
        elif action_type == "replan_goal":
            await self._replan_goal(parameters.get("goal_id"))
        # Continue operations is default - no special action needed
    
    async def _handle_threats(self, threats: List[Dict]):
        """Handle identified threats."""
        for threat in threats:
            threat_type = threat.get("type", "")
            if threat_type == "execution_failure":
                # Retry failed tasks or replan
                await self._recover_from_failures()
            elif threat_type == "resource_exhaustion":
                # Scale down or prioritize
                await self._optimize_resource_usage()
            elif threat_type == "blocked_dependency":
                # Find workaround or escalate
                await self._resolve_blocker(threat)
    
    async def _seize_opportunities(self, opportunities: List[Dict]):
        """Capitalize on identified opportunities."""
        for opp in opportunities:
            opp_type = opp.get("type", "")
            if opp_type == "parallel_execution":
                # Increase parallelism
                self.execution_mode = ExecutionMode.PARALLEL
            elif opp_type == "worker_idle":
                # Assign more work
                await self._schedule_ready_tasks()
    
    async def _reallocate_workers(self, parameters: Dict):
        """Reallocate workers based on priorities."""
        # Implementation for dynamic worker reallocation
        pass
    
    async def _replan_goal(self, goal_id: Optional[str]):
        """Replan a goal that's stuck or needs adjustment."""
        if goal_id:
            goal = self.goal_manager.get_goal(goal_id)
            if goal:
                # Trigger CEO to replan
                self._log_event("goal_replan_triggered", {"goal_id": goal_id})
    
    # ===========================================
    # TASK SCHEDULING & EXECUTION
    # ===========================================
    
    async def _schedule_ready_tasks(self):
        """Schedule tasks that are ready to execute (dependencies met)."""
        if self.state == AutonomyState.BLOCKED:
            return
        
        self.state = AutonomyState.PLANNING
        
        # Get pending tasks
        pending = self.context.pending_tasks.copy()
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        pending.sort(key=lambda t: priority_order.get(t.priority, 2))
        
        # Check dependencies and schedule ready tasks
        completed_task_ids = {t.id for t in self.context.completed_tasks}
        completed_task_titles = {t.title for t in self.context.completed_tasks}
        
        for task in pending:
            if len(self.task_queue) >= self.max_parallel_tasks:
                break
            
            # Check if dependencies are met
            deps_met = all(
                dep in completed_task_ids or dep in completed_task_titles
                for dep in task.dependencies
            )
            
            if deps_met:
                # Find appropriate worker
                worker = self._find_best_worker(task)
                if worker:
                    self.task_queue.append((task, worker))
                    task.status = "scheduled"
                    
                    self._log_event("task_scheduled", {
                        "task_id": task.id,
                        "task_title": task.title,
                        "worker": worker.name if worker else None
                    })
    
    def _find_best_worker(self, task: Task) -> Optional[BaseAgent]:
        """Find the best worker for a task."""
        if not self.workers:
            return None
        
        # If task specifies worker type, try to match
        if hasattr(task, 'assigned_worker') and task.assigned_worker:
            for w_id, worker in self.context.available_workers.items():
                if task.assigned_worker.lower() in worker.name.lower() or \
                   task.assigned_worker.lower() in worker.type.value.lower():
                    return worker
        
        # Default: round-robin or least loaded
        if self.context.available_workers:
            return next(iter(self.context.available_workers.values()))
        
        return None
    
    async def _execute_scheduled_tasks(self):
        """Execute scheduled tasks based on execution mode."""
        if self.state == AutonomyState.BLOCKED:
            return
        
        self.state = AutonomyState.EXECUTING
        
        tasks_to_execute = []
        
        if self.execution_mode == ExecutionMode.SINGLE_THREAD:
            # Execute one task at a time
            if self.task_queue and len(self.active_tasks) < 1:
                tasks_to_execute.append(self.task_queue.popleft())
        
        elif self.execution_mode in [ExecutionMode.PARALLEL, ExecutionMode.ADAPTIVE]:
            # Execute up to max_parallel_tasks
            available_slots = self.max_parallel_tasks - len(self.active_tasks)
            for _ in range(min(available_slots, len(self.task_queue))):
                tasks_to_execute.append(self.task_queue.popleft())
        
        elif self.execution_mode == ExecutionMode.PRIORITIZED:
            # Execute highest priority tasks first
            if self.task_queue:
                # Already sorted by priority in _schedule_ready_tasks
                tasks_to_execute.append(self.task_queue.popleft())
        
        # Execute tasks
        for task, worker in tasks_to_execute:
            await self._execute_task(task, worker)
    
    async def _execute_task(self, task: Task, worker: BaseAgent):
        """Execute a single task with a specific worker."""
        task.status = "in_progress"
        task.started_at = datetime.now()
        
        self.active_tasks[task.id] = task
        self.worker_tasks[worker.id] = task.id
        
        self.metrics.total_tasks += 1
        
        self._log_event("task_started", {
            "task_id": task.id,
            "task_title": task.title,
            "worker": worker.name,
            "worker_id": worker.id
        })
        
        # Trigger callbacks
        for callback in self._on_task_start_callbacks:
            try:
                callback(task, worker)
            except:
                pass
        
        # Execute asynchronously
        asyncio.create_task(self._run_task_execution(task, worker))
    
    async def _run_task_execution(self, task: Task, worker: BaseAgent):
        """Run task execution and handle completion."""
        start_time = time.time()
        
        try:
            # Prepare task context
            task_context = {
                "title": task.title,
                "description": task.description,
                "goal_id": task.goal_id,
                "priority": task.priority,
                "context": task.context if hasattr(task, 'context') else {}
            }
            
            # Execute via worker
            # Note: This assumes worker has an execute method
            # Adjust based on actual worker interface
            if hasattr(worker, 'execute_task'):
                result = worker.execute_task(task)
            elif hasattr(worker, 'think'):
                # Use think method for LLM-based workers
                prompt = f"""Execute this task:

Title: {task.title}
Description: {task.description}
Priority: {task.priority}

Provide your solution:"""
                result = await worker.think(prompt)
            else:
                raise NotImplementedError(f"Worker {worker.name} has no executable method")
            
            duration = time.time() - start_time
            
            # Record success
            execution_result = ExecutionResult(
                task_id=task.id,
                success=True,
                output=result,
                duration=duration,
                metadata={"worker": worker.name}
            )
            
            task.status = "completed"
            task.completed_at = datetime.now()
            self.completed_results[task.id] = execution_result
            self.metrics.completed_tasks += 1
            
            self._log_event("task_completed", {
                "task_id": task.id,
                "duration": duration,
                "worker": worker.name
            })
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            
            # Record failure
            execution_result = ExecutionResult(
                task_id=task.id,
                success=False,
                output=None,
                duration=duration,
                errors=[error_msg]
            )
            
            task.status = "failed"
            task.error = error_msg
            self.completed_results[task.id] = execution_result
            self.metrics.failed_tasks += 1
            
            # Track failure for circuit breaker
            self.recent_failures.append(datetime.now())
            
            self._log_event("task_failed", {
                "task_id": task.id,
                "error": str(e),
                "worker": worker.name
            })
            
            # Trigger error callbacks
            for callback in self._on_error_callbacks:
                try:
                    callback(task, e)
                except:
                    pass
        
        finally:
            # Clean up
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]
            if worker.id in self.worker_tasks:
                del self.worker_tasks[worker.id]
            
            # Trigger completion callbacks
            for callback in self._on_task_complete_callbacks:
                try:
                    callback(task, self.completed_results.get(task.id))
                except:
                    pass
    
    async def _check_task_completions(self):
        """Check for and process completed tasks."""
        # Check if any goals are now complete
        for goal in self.context.active_goals:
            goal_tasks = self.goal_manager.get_tasks_for_goal(goal.id) if hasattr(self.goal_manager, 'get_tasks_for_goal') else []
            
            if goal_tasks and all(t.status == "completed" for t in goal_tasks):
                goal.status = "completed"
                goal.completed_at = datetime.now()
                self.metrics.completed_goals += 1
                
                self._log_event("goal_completed", {
                    "goal_id": goal.id,
                    "objective": goal.objective,
                    "task_count": len(goal_tasks)
                })
                
                # Trigger callbacks
                for callback in self._on_goal_complete_callbacks:
                    try:
                        callback(goal)
                    except:
                        pass
    
    # ===========================================
    # BLOCKED STATE HANDLING
    # ===========================================
    
    def _is_blocked(self) -> bool:
        """Check if the system is blocked."""
        # No available workers
        if not self.context.available_workers and self.task_queue:
            return True
        
        # All tasks waiting on dependencies
        if self.context.pending_tasks and not self.task_queue:
            # Check if any can be scheduled
            completed_ids = {t.id for t in self.context.completed_tasks}
            for task in self.context.pending_tasks:
                if all(dep in completed_ids for dep in task.dependencies):
                    return False
            return True
        
        # Circuit breaker open
        if self.circuit_open:
            return True
        
        return False
    
    async def _handle_blocked_state(self):
        """Handle blocked state - attempt recovery."""
        self.state = AutonomyState.RECOVERING
        self.metrics.recovery_events += 1
        
        self._log_event("blocked_state_entered", {
            "reason": self._identify_blocker_reason()
        })
        
        # Try different recovery strategies
        if self.recent_failures:
            # Clear old failures
            cutoff = datetime.now() - timedelta(seconds=self.failure_window)
            while self.recent_failures and self.recent_failures[0] < cutoff:
                self.recent_failures.popleft()
            
            if len(self.recent_failures) < self.circuit_breaker_threshold:
                self.circuit_open = False
        
        # Wait briefly then reassess
        await asyncio.sleep(2.0)
        self.state = AutonomyState.PLANNING
    
    def _identify_blocker_reason(self) -> str:
        """Identify why the system is blocked."""
        if self.circuit_open:
            return "circuit_breaker_open"
        if not self.context.available_workers and self.task_queue:
            return "no_available_workers"
        if self.context.pending_tasks and not self.task_queue:
            return "dependency_deadlock"
        return "unknown"
    
    # ===========================================
    # CIRCUIT BREAKER
    # ===========================================
    
    def _is_circuit_open(self) -> bool:
        """Check if circuit breaker is open."""
        if not self.circuit_open:
            return False
        
        if self.circuit_open_until and datetime.now() > self.circuit_open_until:
            self.circuit_open = False
            self.circuit_open_until = None
            return False
        
        return True
    
    def _trigger_circuit_breaker(self):
        """Open the circuit breaker due to excessive failures."""
        self.circuit_open = True
        self.circuit_open_until = datetime.now() + timedelta(seconds=30)
        
        self._log_event("circuit_breaker_triggered", {
            "failure_count": len(self.recent_failures),
            "reopen_in": 30
        })
    
    # ===========================================
    # METRICS & MONITORING
    # ===========================================
    
    def _update_metrics(self):
        """Update running metrics."""
        # Success rate
        if self.metrics.total_tasks > 0:
            self.metrics.success_rate = self.metrics.completed_tasks / self.metrics.total_tasks
        
        # Average task duration
        recent_durations = [
            r.duration for r in self.completed_results.values()
            if r.success
        ][-20:]  # Last 20 successful tasks
        
        if recent_durations:
            self.metrics.avg_task_duration = sum(recent_durations) / len(recent_durations)
        
        # Goal velocity (goals per hour)
        if self.start_time:
            hours_elapsed = (datetime.now() - self.start_time).total_seconds() / 3600
            if hours_elapsed > 0:
                self.metrics.goal_velocity = self.metrics.completed_goals / hours_elapsed
                self.metrics.task_throughput = self.metrics.completed_tasks / hours_elapsed
        
        # Worker utilization
        for worker_id in self.workers:
            busy_time = sum(
                1 for r in self.completed_results.values()
                if r.metadata.get("worker") == worker_id
            )
            total_time = max(1, self.metrics.completed_tasks)
            self.metrics.worker_utilization[worker_id] = busy_time / total_time
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics as dictionary."""
        return {
            "state": self.state.value,
            "is_running": self.is_running,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            "goals": {
                "total": self.metrics.total_goals,
                "completed": self.metrics.completed_goals,
                "velocity": self.metrics.goal_velocity
            },
            "tasks": {
                "total": self.metrics.total_tasks,
                "completed": self.metrics.completed_tasks,
                "failed": self.metrics.failed_tasks,
                "active": len(self.active_tasks),
                "queued": len(self.task_queue),
                "success_rate": self.metrics.success_rate,
                "avg_duration": self.metrics.avg_task_duration,
                "throughput": self.metrics.task_throughput
            },
            "ooda": {
                "loops_run": self.metrics.ooda_loops_run,
                "decisions_made": self.metrics.decisions_made
            },
            "workers": {
                "total": len(self.workers),
                "available": len(self.context.available_workers),
                "busy": len(self.context.busy_workers),
                "utilization": self.metrics.worker_utilization
            },
            "health": {
                "circuit_breaker_open": self.circuit_open,
                "recent_failures": len(self.recent_failures),
                "recovery_events": self.metrics.recovery_events
            }
        }
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Get dashboard data for UI."""
        metrics = self.get_metrics()
        
        return {
            **metrics,
            "active_goals": [
                {"id": g.id, "objective": g.objective, "priority": g.priority}
                for g in self.context.active_goals
            ],
            "active_tasks": [
                {"id": t.id, "title": t.title, "worker": self.worker_tasks.get(list(self.active_tasks.keys())[0], "unknown")}
                for t in list(self.active_tasks.values())[:5]
            ],
            "recent_completions": [
                {"task_id": r.task_id, "success": r.success, "duration": r.duration}
                for r in list(self.completed_results.values())[-5:]
            ],
            "recent_events": list(self.event_log)[-10:]
        }
    
    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """Log an event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data
        }
        self.event_log.append(event)
    
    def _handle_critical_error(self, error: Exception):
        """Handle critical errors that threaten system stability."""
        self._log_event("critical_error", {
            "error": str(error),
            "traceback": traceback.format_exc()
        })
        
        # Don't shut down - log and continue
        # Autonomous systems should be resilient
    
    # ===========================================
    # WORKER MANAGEMENT
    # ===========================================
    
    def register_worker(self, worker: BaseAgent):
        """Register a worker agent."""
        self.workers[worker.id] = worker
        self._log_event("worker_registered", {
            "worker_id": worker.id,
            "worker_name": worker.name,
            "worker_type": worker.type.value
        })
    
    def unregister_worker(self, worker_id: str):
        """Unregister a worker agent."""
        if worker_id in self.workers:
            del self.workers[worker_id]
            if worker_id in self.worker_tasks:
                del self.worker_tasks[worker_id]
            
            self._log_event("worker_unregistered", {"worker_id": worker_id})
    
    # ===========================================
    # CALLBACKS
    # ===========================================
    
    def on_goal_start(self, callback: Callable):
        """Register callback for goal start."""
        self._on_goal_start_callbacks.append(callback)
    
    def on_goal_complete(self, callback: Callable):
        """Register callback for goal completion."""
        self._on_goal_complete_callbacks.append(callback)
    
    def on_task_start(self, callback: Callable):
        """Register callback for task start."""
        self._on_task_start_callbacks.append(callback)
    
    def on_task_complete(self, callback: Callable):
        """Register callback for task completion."""
        self._on_task_complete_callbacks.append(callback)
    
    def on_error(self, callback: Callable):
        """Register callback for errors."""
        self._on_error_callbacks.append(callback)
    
    def on_state_change(self, callback: Callable):
        """Register callback for state changes."""
        self._on_state_change_callbacks.append(callback)
