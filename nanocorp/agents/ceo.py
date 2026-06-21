"""
NanoCorp v4.0 - CEO Agent (Autonomous Executive)

Strategic leader with OODA loop decision-making, autonomous execution,
and full workforce coordination. This is the brain of the autonomous startup.
"""
from __future__ import annotations

import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json

from .base import BaseAgent, AgentType, Message
from ..core.ooda import OODALoop, OODAPhase, SituationalAssessment, Decision
from ..core.goals import GoalManager, Goal, Task


# ===========================================
# CEO AUTONOMY MODES
# ===========================================

class AutonomyMode(str, Enum):
    """CEO autonomy operating modes"""
    MANUAL = "manual"  # Wait for explicit commands only
    SEMI_AUTO = "semi_auto"  # Execute assigned goals autonomously
    FULL_AUTO = "full_auto"  # Continuous operation, self-directed
    HYPER_AUTO = "hyper_auto"  # Aggressive optimization, parallel execution


# ===========================================
# CEO SYSTEM PROMPT (ENHANCED)
# ===========================================

CEO_SYSTEM_PROMPT = """You are the CEO of an autonomous AI startup. Your name is {name}.

## YOUR ROLE

You are not just an advisor - you are THE EXECUTIVE. You:
1. **Set Strategy**: Define vision, priorities, and OKRs
2. **Decompose Goals**: Break ambitious goals into executable tasks
3. **Allocate Resources**: Assign work to specialized AI agents
4. **Make Decisions**: Use OODA loop for rapid, evidence-based decisions
5. **Ensure Quality**: Review outputs, enforce standards, iterate
6. **Learn & Adapt**: Continuously improve based on results

## STRATEGIC FRAMEWORKS

### First Principles Thinking
- Challenge every assumption
- Reduce problems to fundamental truths
- Build solutions from the ground up

### 10x Thinking
- Don't optimize - transform
- Ask: "How would we solve this if constraints were 10x different?"
- Seek exponential improvements, not incremental gains

### OODA Loop Decision Making
- **Observe**: Gather data from all sources (tasks, workers, market, users)
- **Orient**: Analyze situation, identify threats and opportunities
- **Decide**: Select best course of action from options
- **Act**: Execute decisively and rapidly
- **Assess**: Learn from outcomes, feed back into loop

### Eisenhower Matrix
- Prioritize by urgency AND importance
- Delegate or delete non-essential work
- Focus on high-leverage activities

## LEADERSHIP PRINCIPLES

1. **Radical Clarity**: Every task has clear success criteria and ownership
2. **Extreme Ownership**: You own all outcomes, good or bad
3. **Bias for Action**: Prefer decisive action over perfect analysis
4. **Data-Driven**: Base decisions on evidence, not opinions
5. **Relentless Iteration**: Ship fast, learn fast, improve faster
6. **Transparent Communication**: Share context, reasoning, status openly
7. **Empowerment**: Give agents autonomy on HOW, clarity on WHAT

## OPERATING CADENCE

### Continuous OODA Loops
- Run decision cycles every 30 seconds in hyper mode
- Adjust frequency based on situation criticality
- Parallelize independent decision streams

### Daily Rhythm (Simulated)
- **Morning**: Review overnight progress, set daily priorities
- **Midday**: Check blockers, reallocate resources
- **Evening**: Review day's results, plan tomorrow

### Weekly Rhythm (Simulated)
- **Monday**: Set weekly OKRs, align team
- **Wednesday**: Mid-week check-in, course correct
- **Friday**: Review week, celebrate wins, learn from losses

## COMMUNICATION STYLE

- **Direct & Decisive**: No hedging, no ambiguity
- **Context-Rich**: Explain the WHY behind decisions
- **Action-Oriented**: Every conversation ends with clear next steps
- **Intellectually Honest**: Acknowledge uncertainty and mistakes
- **Inspiring**: Motivate the team with vision and progress

## RESPONSE PROTOCOL

When receiving input (user message, task completion, market signal):

1. **SITUATIONAL AWARENESS**
   - What just happened?
   - What's the broader context?
   - What goals does this relate to?

2. **OODA ANALYSIS**
   - What do my sensors tell me?
   - What are the threats and opportunities?
   - What's my confidence level?

3. **DECISION**
   - What are my options?
   - Which option maximizes goal achievement?
   - What's the risk/reward?

4. **ACTION**
   - Execute immediately if low-risk
   - Delegate to appropriate worker
   - Create follow-up tasks if needed
   - Log decision rationale

5. **FOLLOW-THROUGH**
   - Monitor execution
   - Unblock if stuck
   - Review results
   - Extract learnings

## PRIORITIZATION HEURISTICS

Always prioritize actions that:
✓ Move toward North Star goals fastest
✓ Remove critical blockers
✓ Generate validated learning
✓ Reduce existential risk
✓ Create compounding value
✓ Leverage existing momentum

Avoid:
✗ Perfectionism over progress
✗ Low-leverage busywork
✗ Premature optimization
✗ Solving imaginary problems
✗ Context switching without purpose

## SUCCESS METRICS

You are measured by:
- Goal completion rate
- Speed of execution (idea → result)
- Quality of outputs (user satisfaction)
- Resource efficiency (output per token)
- Learning velocity (improvement rate)
- Team utilization (worker productivity)

Remember: You are building a company that can operate autonomously at the level of a 100-person team with Elon Musk as CEO. Think bigger. Move faster. Execute better."""


# ===========================================
# CEO AGENT (v4.0 - AUTONOMOUS)
# ===========================================

class CEOAgent(BaseAgent):
    """
    Autonomous CEO Agent - Strategic executive of the AI workforce.
    
    Capabilities:
    - OODA loop decision making
    - Autonomous goal pursuit
    - Dynamic task decomposition
    - Workforce orchestration
    - Continuous operation
    - Self-improvement
    
    This is not a chatbot. This is an autonomous executive.
    """
    
    def __init__(
        self,
        name: str = "CEO",
        tools: Optional[List[str]] = None,
        memory: Optional[Any] = None,
        ai_provider: Optional[Any] = None,
        company_name: str = "My Company",
        mission: str = "",
        autonomy_mode: AutonomyMode = AutonomyMode.SEMI_AUTO,
        ooda_config: Optional[Dict] = None
    ):
        super().__init__(
            agent_id="ceo",
            name=name,
            agent_type=AgentType.CEO,
            tools=tools,  # CEO has access to ALL tools
            system_prompt=CEO_SYSTEM_PROMPT.format(name=name),
            memory=memory,
            ai_provider=ai_provider
        )
        
        self.company_name = company_name
        self.mission = mission
        
        # Core systems
        self.goal_manager = GoalManager()
        self.ooda_loop = OODALoop(llm=ai_provider, memory=memory, config=ooda_config or {})
        
        # State
        self.autonomy_mode = autonomy_mode
        self.is_running = False
        self.current_goal: Optional[Goal] = None
        self.active_tasks: Dict[str, Task] = {}
        self.workers: Dict[str, BaseAgent] = {}
        self.decisions_log: List[Decision] = []
        
        # Metrics
        self.metrics = {
            "goals_completed": 0,
            "tasks_completed": 0,
            "decisions_made": 0,
            "loops_run": 0,
            "avg_task_duration": 0.0,
            "success_rate": 1.0
        }
        
        # Callbacks
        self._on_decision_callbacks: List[Callable] = []
        self._on_task_complete_callbacks: List[Callable] = []
        self._on_goal_complete_callbacks: List[Callable] = []
    
    # ===========================================
    # COMPANY MANAGEMENT
    # ===========================================
    
    def set_company(self, name: str, mission: str, vision: str = ""):
        """Set company identity and strategic direction."""
        self.company_name = name
        self.mission = mission
        
        # Store in memory
        self.remember(
            content=f"Company: {name} | Mission: {mission} | Vision: {vision}",
            memory_type="semantic",
            tags=["company", "strategy"]
        )
    
    def get_company_context(self) -> Dict[str, Any]:
        """Get comprehensive company context for decision-making."""
        return {
            "name": self.company_name,
            "mission": self.mission,
            "active_goals": len([g for g in self.goal_manager.goals if g.status == "active"]),
            "pending_tasks": len([t for t in self.active_tasks.values() if t.status == "pending"]),
            "workers_available": len(self.workers),
            "mode": self.autonomy_mode.value,
            "metrics": self.metrics.copy()
        }
    
    # ===========================================
    # GOAL MANAGEMENT (ENHANCED)
    # ===========================================
    
    def add_goal(
        self,
        goal: str,
        priority: str = "medium",
        deadline: Optional[str] = None,
        success_criteria: Optional[str] = None,
        key_results: Optional[List[str]] = None
    ) -> str:
        """
        Add a strategic goal with full OKR structure.
        
        Args:
            goal: Goal description (the Objective)
            priority: high, medium, low
            deadline: Optional deadline (ISO format)
            success_criteria: Definition of done
            key_results: Measurable key results
        
        Returns:
            Goal ID
        """
        goal_obj = Goal(
            id=f"goal_{uuid.uuid4().hex[:8]}",
            objective=goal,
            priority=priority,
            deadline=deadline,
            success_criteria=success_criteria,
            key_results=key_results or []
        )
        
        self.goal_manager.add_goal(goal_obj)
        
        # Remember strategically
        self.remember(
            content=f"New strategic goal: {goal} (priority: {priority})",
            memory_type="semantic",
            tags=["goal", "objective", priority]
        )
        
        # Auto-decompose if in auto mode
        if self.autonomy_mode in [AutonomyMode.FULL_AUTO, AutonomyMode.HYPER_AUTO]:
            asyncio.create_task(self.decompose_and_execute_goal(goal_obj.id))
        
        return goal_obj.id
    
    async def decompose_and_execute_goal(self, goal_id: str):
        """
        Decompose a goal into tasks and begin autonomous execution.
        
        This is where strategy becomes action.
        """
        goal = self.goal_manager.get_goal(goal_id)
        if not goal:
            return {"error": f"Goal {goal_id} not found"}
        
        self.current_goal = goal
        
        # Use AI to decompose goal into tasks
        decomposition_prompt = f"""
Decompose this strategic goal into specific, actionable tasks:

GOAL: {goal.objective}
PRIORITY: {goal.priority}
SUCCESS CRITERIA: {goal.success_criteria or "Not specified"}
KEY RESULTS: {goal.key_results or "Not specified"}

Create a task list that:
1. Covers all aspects of achieving this goal
2. Has clear dependencies between tasks
3. Identifies which worker type should handle each task
4. Orders tasks for maximum parallelization
5. Includes validation/testing tasks

Return as JSON array of tasks with fields:
- title: Task name
- type: Task type (research, coding, design, marketing, etc.)
- worker_type: Best worker for this task
- dependencies: List of task titles this depends on
- estimated_complexity: low/medium/high
"""
        
        try:
            decomposition_response = await self.think(decomposition_prompt)
            
            # Parse response (robust parsing)
            tasks = self._parse_task_decomposition(decomposition_response)
            
            # Create tasks in dependency order
            for task_data in tasks:
                task = Task(
                    id=f"task_{uuid.uuid4().hex[:8]}",
                    title=task_data.get("title", "Unnamed Task"),
                    task_type=task_data.get("type", "general"),
                    description=task_data.get("description", ""),
                    priority=goal.priority,
                    assigned_worker=task_data.get("worker_type"),
                    dependencies=task_data.get("dependencies", []),
                    goal_id=goal_id
                )
                self.goal_manager.add_task(task)
                self.active_tasks[task.id] = task
            
            # Begin execution
            await self.execute_goal(goal_id)
            
        except Exception as e:
            # Fallback: create basic tasks
            fallback_tasks = [
                Task(id=f"task_{i}", title=f"Research: {goal.objective}", task_type="research", priority=goal.priority, goal_id=goal_id),
                Task(id=f"task_{i+1}", title=f"Plan: {goal.objective}", task_type="planning", priority=goal.priority, goal_id=goal_id),
                Task(id=f"task_{i+2}", title=f"Execute: {goal.objective}", task_type="execution", priority=goal.priority, goal_id=goal_id),
                Task(id=f"task_{i+3}", title=f"Review: {goal.objective}", task_type="review", priority=goal.priority, goal_id=goal_id),
            ]
            for task in fallback_tasks:
                self.goal_manager.add_task(task)
                self.active_tasks[task.id] = task
    
    def _parse_task_decomposition(self, response: str) -> List[Dict]:
        """Parse AI response into structured tasks."""
        # Try JSON parsing first
        import re
        json_match = re.search(r'\[[\s\S]*\]', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        
        # Fallback: line-by-line parsing
        tasks = []
        for line in response.split('\n'):
            line = line.strip()
            if line and ('-' in line or '•' in line or line[0].isdigit()):
                tasks.append({
                    "title": line.lstrip('-•').strip(),
                    "type": "general",
                    "worker_type": "general"
                })
        
        return tasks if tasks else [{"title": "Execute goal", "type": "execution", "worker_type": "general"}]
    
    async def execute_goal(self, goal_id: str):
        """Execute all tasks for a goal with dependency management."""
        goal = self.goal_manager.get_goal(goal_id)
        if not goal:
            return
        
        completed_tasks = set()
        max_iterations = 100  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            # Get ready tasks (dependencies met)
            ready_tasks = []
            for task in self.goal_manager.get_tasks_for_goal(goal_id):
                if task.id in completed_tasks:
                    continue
                if task.status == "completed":
                    completed_tasks.add(task.id)
                    continue
                
                # Check dependencies
                deps_met = all(
                    any(t.title in completed_tasks or t.id in completed_tasks 
                        for t in self.goal_manager.tasks if t.title == dep or t.id == dep)
                    for dep in task.dependencies
                )
                
                if deps_met and task.status == "pending":
                    ready_tasks.append(task)
            
            if not ready_tasks:
                # Check if all done
                all_done = all(t.status == "completed" for t in self.goal_manager.get_tasks_for_goal(goal_id))
                if all_done:
                    goal.status = "completed"
                    self.metrics["goals_completed"] += 1
                    self._trigger_goal_complete(goal)
                    return
                break
            
            # Execute ready tasks in parallel (if hyper mode)
            if self.autonomy_mode == AutonomyMode.HYPER_AUTO:
                results = await asyncio.gather(*[self.execute_task(task) for task in ready_tasks])
            else:
                results = [await self.execute_task(task) for task in ready_tasks]
            
            # Update task statuses
            for task, result in zip(ready_tasks, results):
                task.status = "completed"
                task.result = result
                completed_tasks.add(task.id)
                self.metrics["tasks_completed"] += 1
                self._trigger_task_complete(task, result)
            
            iteration += 1
        
        # Mark goal as partially complete if we exited early
        if goal.status != "completed":
            goal.status = "in_progress"
    
    # ===========================================
    # TASK EXECUTION
    # ===========================================
    
    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a single task."""
        task.status = "in_progress"
        start_time = datetime.now()
        
        # Determine executor
        worker_type = task.assigned_worker or task.task_type
        worker = self._get_best_worker_for_task(task)
        
        if worker:
            # Delegate to worker
            result = await worker.execute_task({
                "id": task.id,
                "title": task.title,
                "type": task.task_type,
                "description": task.description,
                "goal_id": task.goal_id
            })
        else:
            # Execute directly
            result = await self._execute_task_direct(task)
        
        # Record metrics
        duration = (datetime.now() - start_time).total_seconds()
        self._update_task_metrics(duration, result.get("success", True))
        
        return result
    
    async def _execute_task_direct(self, task: Task) -> Dict[str, Any]:
        """Execute task directly using AI."""
        prompt = f"""Execute this task:

TASK: {task.title}
TYPE: {task.task_type}
DESCRIPTION: {task.description or "No additional details"}

Provide a complete, actionable result. Be specific and thorough."""
        
        try:
            result_content = await self.think(prompt)
            return {
                "success": True,
                "task_id": task.id,
                "result": result_content,
                "executed_by": "ceo"
            }
        except Exception as e:
            return {
                "success": False,
                "task_id": task.id,
                "error": str(e)
            }
    
    def _get_best_worker_for_task(self, task: Task) -> Optional[BaseAgent]:
        """Find the best worker for a task."""
        if not self.workers:
            return None
        
        # Simple matching (can be enhanced with skill vectors)
        type_to_worker = {
            "coding": ["coder", "webdev", "backend", "frontend"],
            "design": ["designer", "ui", "ux"],
            "research": ["researcher", "analyst"],
            "marketing": ["marketer", "growth"],
            "writing": ["writer", "content"],
            "email": ["email_marketer"],
            "social": ["social_media"],
            "devops": ["devops", "infrastructure"],
            "sales": ["sales"],
            "finance": ["finance"],
        }
        
        target_types = type_to_worker.get(task.task_type, [])
        target_types.append(task.assigned_worker) if task.assigned_worker else None
        
        for worker_id, worker in self.workers.items():
            if worker.type.value in target_types or worker.name.lower() in [t.lower() for t in target_types]:
                return worker
        
        # Return first available worker as fallback
        return list(self.workers.values())[0] if self.workers else None
    
    # ===========================================
    # OODA LOOP INTEGRATION
    # ===========================================
    
    async def run_ooda_cycle(self, context_override: Optional[Dict] = None):
        """Run a single OODA decision cycle."""
        # Gather context
        context = context_override or self._gather_ooda_context()
        
        # Run OODA loop
        cycle_result = self.ooda_loop.run_cycle(context, executor=self._execute_ooda_action)
        
        # Log decision
        if self.ooda_loop.decisions:
            latest_decision = self.ooda_loop.decisions[-1]
            self.decisions_log.append(latest_decision)
            self.metrics["decisions_made"] += 1
            self._trigger_decision(latest_decision)
        
        self.metrics["loops_run"] += 1
        
        return cycle_result
    
    def _gather_ooda_context(self) -> Dict[str, Any]:
        """Gather comprehensive context for OODA loop."""
        return {
            "task_status": {
                "pending": len([t for t in self.active_tasks.values() if t.status == "pending"]),
                "in_progress": len([t for t in self.active_tasks.values() if t.status == "in_progress"]),
                "completed": len([t for t in self.active_tasks.values() if t.status == "completed"]),
                "failed": len([t for t in self.active_tasks.values() if t.status == "failed"])
            },
            "worker_status": {
                worker_id: worker.get_state().status 
                for worker_id, worker in self.workers.items()
            },
            "goal_progress": {
                goal.id: goal.status 
                for goal in self.goal_manager.goals
            },
            "resources": {
                "memory_usage": "N/A",  # Can be enhanced
                "token_usage": "N/A",
                "api_calls_remaining": "N/A"
            },
            "external_signals": {}  # Market data, user feedback, etc.
        }
    
    def _execute_ooda_action(self, action) -> Dict[str, Any]:
        """Execute an action from OODA loop decision."""
        action_type = action.action_type
        
        if action_type == "create_task":
            # Create and queue new task
            pass
        elif action_type == "reallocate_worker":
            # Reassign worker to different task
            pass
        elif action_type == "pivot_strategy":
            # Adjust goal priorities
            pass
        
        return {"status": "executed", "action": action_type}
    
    # ===========================================
    # AUTONOMOUS OPERATION
    # ===========================================
    
    async def start_autonomous_operation(self, initial_goal: Optional[str] = None):
        """
        Start continuous autonomous operation.
        
        The CEO will continuously:
        - Run OODA loops
        - Execute tasks
        - Adapt to changing conditions
        - Pursue goals relentlessly
        """
        if self.is_running:
            return {"status": "already_running"}
        
        self.is_running = True
        
        # Set initial goal if provided
        if initial_goal:
            self.add_goal(initial_goal, priority="high")
        
        # Main autonomy loop
        while self.is_running:
            try:
                # Run OODA cycle
                await self.run_ooda_cycle()
                
                # Process pending tasks
                pending_goals = [g for g in self.goal_manager.goals if g.status == "active"]
                if pending_goals:
                    # Execute highest priority goal
                    priority_order = {"high": 0, "medium": 1, "low": 2}
                    pending_goals.sort(key=lambda g: priority_order.get(g.priority, 1))
                    
                    if not any(t.status == "in_progress" for t in self.active_tasks.values()):
                        await self.execute_goal(pending_goals[0].id)
                
                # Sleep between cycles (adjust based on mode)
                sleep_times = {
                    AutonomyMode.MANUAL: 3600,
                    AutonomyMode.SEMI_AUTO: 60,
                    AutonomyMode.FULL_AUTO: 10,
                    AutonomyMode.HYPER_AUTO: 1
                }
                await asyncio.sleep(sleep_times.get(self.autonomy_mode, 10))
                
            except Exception as e:
                # Log error but keep running
                self.remember(
                    content=f"Autonomy loop error: {str(e)}",
                    memory_type="episodic",
                    tags=["error", "autonomy"]
                )
                await asyncio.sleep(5)  # Brief pause before retry
        
        return {"status": "stopped"}
    
    def stop_autonomous_operation(self):
        """Stop autonomous operation."""
        self.is_running = False
    
    # ===========================================
    # WORKER MANAGEMENT
    # ===========================================
    
    def register_worker(self, worker: BaseAgent):
        """Register a worker agent."""
        self.workers[worker.id] = worker
        
        self.remember(
            content=f"Worker registered: {worker.name} ({worker.type.value})",
            memory_type="semantic",
            tags=["worker", "team"]
        )
    
    def get_worker(self, worker_id: str) -> Optional[BaseAgent]:
        """Get a worker by ID."""
        return self.workers.get(worker_id)
    
    def list_workers(self) -> List[Dict]:
        """List all workers with status."""
        return [
            {
                "id": w.id,
                "name": w.name,
                "type": w.type.value,
                "status": w.get_state().status
            }
            for w in self.workers.values()
        ]
    
    # ===========================================
    # CALLBACKS & EVENTS
    # ===========================================
    
    def on_decision(self, callback: Callable):
        """Register callback for decisions."""
        self._on_decision_callbacks.append(callback)
    
    def on_task_complete(self, callback: Callable):
        """Register callback for task completion."""
        self._on_task_complete_callbacks.append(callback)
    
    def on_goal_complete(self, callback: Callable):
        """Register callback for goal completion."""
        self._on_goal_complete_callbacks.append(callback)
    
    def _trigger_decision(self, decision: Decision):
        """Trigger decision callbacks."""
        for callback in self._on_decision_callbacks:
            try:
                callback(decision)
            except:
                pass
    
    def _trigger_task_complete(self, task: Task, result: Dict):
        """Trigger task completion callbacks."""
        for callback in self._on_task_complete_callbacks:
            try:
                callback(task, result)
            except:
                pass
    
    def _trigger_goal_complete(self, goal):
        """Trigger goal completion callbacks."""
        for callback in self._on_goal_complete_callbacks:
            try:
                callback(goal)
            except:
                pass
    
    # ===========================================
    # METRICS & REPORTING
    # ===========================================
    
    def _update_task_metrics(self, duration: float, success: bool):
        """Update running metrics."""
        # Update average duration
        total_tasks = self.metrics["tasks_completed"]
        old_avg = self.metrics["avg_task_duration"]
        self.metrics["avg_task_duration"] = ((old_avg * (total_tasks - 1)) + duration) / total_tasks
        
        # Update success rate
        old_success_count = self.metrics["success_rate"] * (total_tasks - 1)
        new_success_count = old_success_count + (1 if success else 0)
        self.metrics["success_rate"] = new_success_count / total_tasks if total_tasks > 0 else 1.0
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        return {
            **self.metrics,
            "active_goals": len([g for g in self.goal_manager.goals if g.status == "active"]),
            "total_tasks": len(self.active_tasks),
            "workers": len(self.workers),
            "decisions_logged": len(self.decisions_log),
            "autonomy_mode": self.autonomy_mode.value
        }
    
    def generate_report(self) -> str:
        """Generate executive summary report."""
        metrics = self.get_metrics()
        
        report = f"""
# {self.company_name} - Executive Report
Generated: {datetime.now().isoformat()}

## MISSION
{self.mission or "Not specified"}

## PERFORMANCE METRICS
- Goals Completed: {metrics['goals_completed']}
- Tasks Completed: {metrics['tasks_completed']}
- Decisions Made: {metrics['decisions_made']}
- OODA Loops Run: {metrics['loops_run']}
- Average Task Duration: {metrics['avg_task_duration']:.2f}s
- Success Rate: {metrics['success_rate']*100:.1f}%

## TEAM STATUS
- Active Workers: {metrics['workers']}
- Operating Mode: {metrics['autonomy_mode']}

## CURRENT FOCUS
{f"Goal: {self.current_goal.objective}" if self.current_goal else "No active goal"}

---
*Report generated by autonomous CEO agent*
"""
        return report=
    
    def get_dashboard(self) -> Dict:
        """Get CEO dashboard."""
        status_counts = {}
        for t in self.tasks:
            status = t["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "company": self.company_name,
            "mission": self.mission,
            "goals": {
                "total": len(self.goals),
                "active": len([g for g in self.goals if g["status"] == "active"])
            },
            "tasks": {
                "total": len(self.tasks),
                **status_counts
            },
            "workers": {
                "total": len(self.workers),
                "by_type": {
                    w.type.value: 1 for w in self.workers.values()
                }
            },
            "completion_rate": (
                status_counts.get("completed", 0) / max(1, len(self.tasks)) * 100
            )
        }
