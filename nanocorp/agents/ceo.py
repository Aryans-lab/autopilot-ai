"""
NanoCorp v3.0 - CEO Agent

Strategic leader with full tool access and goal decomposition.
"""
from __future__ import annotations

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

from .base import BaseAgent, AgentType, Message


# ===========================================
# CEO SYSTEM PROMPT
# ===========================================

CEO_SYSTEM_PROMPT = """You are the CEO of a startup being built with AI agents. Your name is {name}.

Your role is to:
1. **Strategic Vision**: Define company direction and priorities
2. **Goal Decomposition**: Break down big goals into actionable tasks
3. **Resource Allocation**: Assign tasks to the right agents
4. **Quality Control**: Ensure outputs meet standards
5. **Learning & Adaptation**: Improve based on results

## Strategic Frameworks

### First Principles Thinking
- Challenge assumptions
- Break problems to fundamentals
- Build up from there

### 10x Thinking  
- Don't optimize, transform
- How would you solve this if constraints were 10x different?

### First-Team Priority
- Treat the agent team as your first team
- Ensure they have what they need to succeed

## Leadership Principles

1. **Clear Direction**: Every task should have clear success criteria
2. **Autonomy with Accountability**: Give agents room to decide how, but expect results
3. **Rapid Iteration**: Ship fast, learn fast, improve fast
4. **Evidence Over Opinion**: Base decisions on data and results
5. **Radical Transparency**: Share context, reasoning, and status openly

## Communication Style

- Be direct and decisive
- Explain the "why" behind decisions
- Acknowledge uncertainty when it exists
- Celebrate wins and learn from failures

## Response Format

When given a request, respond with:
1. **Understanding**: Confirm what you're being asked to do
2. **Analysis**: Quick assessment of approach
3. **Decision**: What you're going to do
4. **Plan**: How you'll execute (if complex)
5. **Action**: Execute or delegate

Always prioritize actions that:
- Move toward goals fastest
- Reduce risk early
- Generate learning
"""


# ===========================================
# CEO AGENT
# ===========================================

class CEOAgent(BaseAgent):
    """
    CEO Agent - Strategic leader of the AI workforce.
    
    Responsibilities:
    - Strategic planning
    - Task decomposition
    - Agent coordination
    - Quality assurance
    - Goal tracking
    """
    
    def __init__(
        self,
        name: str = "CEO",
        tools: Optional[List[str]] = None,
        memory: Optional[Any] = None,
        ai_provider: Optional[Any] = None,
        company_name: str = "My Company",
        mission: str = ""
    ):
        super().__init__(
            agent_id="ceo",
            name=name,
            agent_type=AgentType.CEO,
            tools=tools,  # CEO has access to all tools
            system_prompt=CEO_SYSTEM_PROMPT.format(name=name),
            memory=memory,
            ai_provider=ai_provider
        )
        
        self.company_name = company_name
        self.mission = mission
        self.goals: List[Dict] = []
        self.tasks: List[Dict] = []
        self.workers: Dict[str, BaseAgent] = {}
        self.delegations: Dict[str, str] = {}  # task_id -> worker_id
    
    # ===========================================
    # COMPANY MANAGEMENT
    # ===========================================
    
    def set_company(self, name: str, mission: str):
        """Set company information."""
        self.company_name = name
        self.mission = mission
        
        # Update system prompt
        self.system_prompt = CEO_SYSTEM_PROMPT.format(name=self.name)
        
        self.remember(
            content=f"Company set: {name} - {mission}",
            memory_type="semantic",
            tags=["company", "mission"]
        )
    
    def get_company_info(self) -> Dict:
        """Get company information."""
        return {
            "name": self.company_name,
            "mission": self.mission,
            "goals": self.goals,
            "active_tasks": len([t for t in self.tasks if t.get("status") == "active"])
        }
    
    # ===========================================
    # GOAL MANAGEMENT
    # ===========================================
    
    def add_goal(
        self,
        goal: str,
        priority: str = "medium",
        deadline: Optional[str] = None,
        success_criteria: Optional[str] = None
    ) -> str:
        """
        Add a strategic goal.
        
        Args:
            goal: Goal description
            priority: high, medium, low
            deadline: Optional deadline
            success_criteria: What success looks like
        
        Returns:
            Goal ID
        """
        goal_id = f"goal_{len(self.goals) + 1}"
        
        goal_data = {
            "id": goal_id,
            "goal": goal,
            "priority": priority,
            "deadline": deadline,
            "success_criteria": success_criteria,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "tasks": []
        }
        
        self.goals.append(goal_data)
        
        self.remember(
            content=f"New goal: {goal} (priority: {priority})",
            memory_type="semantic",
            tags=["goal", priority]
        )
        
        return goal_id
    
    def decompose_goal(self, goal_id: str) -> List[Dict]:
        """
        Decompose a goal into tasks.
        
        Args:
            goal_id: Goal to decompose
        
        Returns:
            List of tasks
        """
        goal = self.get_goal(goal_id)
        if not goal:
            return []
        
        # Use AI to decompose
        # For now, return simple tasks
        tasks = [
            {"title": f"Research for: {goal['goal']}", "type": "research"},
            {"title": f"Plan: {goal['goal']}", "type": "planning"},
            {"title": f"Execute: {goal['goal']}", "type": "execution"},
            {"title": f"Review: {goal['goal']}", "type": "review"}
        ]
        
        # Update goal with tasks
        goal["tasks"] = [t["title"] for t in tasks]
        
        return tasks
    
    def get_goal(self, goal_id: str) -> Optional[Dict]:
        """Get a goal by ID."""
        for g in self.goals:
            if g["id"] == goal_id:
                return g
        return None
    
    # ===========================================
    # TASK MANAGEMENT
    # ===========================================
    
    def create_task(
        self,
        title: str,
        task_type: str,
        description: str = "",
        priority: str = "medium",
        assigned_to: Optional[str] = None,
        goal_id: Optional[str] = None,
        dependencies: Optional[List[str]] = None
    ) -> str:
        """
        Create a task.
        
        Args:
            title: Task title
            task_type: Type of task (coding, writing, research, etc.)
            description: Detailed description
            priority: high, medium, low
            assigned_to: Worker ID to assign to
            goal_id: Goal this task supports
            dependencies: Task IDs this depends on
        
        Returns:
            Task ID
        """
        task_id = f"task_{len(self.tasks) + 1}"
        
        task = {
            "id": task_id,
            "title": title,
            "type": task_type,
            "description": description,
            "priority": priority,
            "status": "pending",
            "assigned_to": assigned_to,
            "goal_id": goal_id,
            "dependencies": dependencies or [],
            "result": None,
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None
        }
        
        self.tasks.append(task)
        
        # Delegate if assigned
        if assigned_to and assigned_to in self.workers:
            self.delegate_task(task_id, assigned_to)
        
        return task_id
    
    def delegate_task(self, task_id: str, worker_id: str):
        """
        Delegate a task to a worker.
        
        Args:
            task_id: Task to delegate
            worker_id: Worker to delegate to
        """
        task = self.get_task(task_id)
        if not task:
            return
        
        task["assigned_to"] = worker_id
        self.delegations[task_id] = worker_id
        
        worker = self.workers.get(worker_id)
        if worker:
            # Send task to worker
            message = Message(
                from_agent=self.id,
                to_agent=worker_id,
                content=f"New task: {task['title']}",
                type="task",
                metadata={"task": task}
            )
            worker.receive_message(message)
        
        self.remember(
            content=f"Delegated: {task['title']} to {worker_id}",
            memory_type="episodic",
            tags=["delegation", task["type"]]
        )
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get a task by ID."""
        for t in self.tasks:
            if t["id"] == task_id:
                return t
        return None
    
    def update_task_status(self, task_id: str, status: str, result: Any = None):
        """Update task status and result."""
        task = self.get_task(task_id)
        if not task:
            return
        
        task["status"] = status
        
        if status == "in_progress":
            task["started_at"] = datetime.now().isoformat()
        elif status == "completed":
            task["completed_at"] = datetime.now().isoformat()
            if result:
                task["result"] = result
            
            # Learn from result
            self.learn(
                f"Task completed: {task['title']}",
                outcome="success" if result else "failure"
            )
    
    def get_pending_tasks(self, task_type: Optional[str] = None) -> List[Dict]:
        """Get pending tasks, optionally filtered by type."""
        pending = [t for t in self.tasks if t["status"] == "pending"]
        
        if task_type:
            pending = [t for t in pending if t["type"] == task_type]
        
        return pending
    
    # ===========================================
    # WORKER MANAGEMENT
    # ===========================================
    
    def register_worker(self, worker: BaseAgent):
        """Register a worker agent."""
        self.workers[worker.id] = worker
        self.remember(
            content=f"Worker joined: {worker.name} ({worker.type.value})",
            memory_type="semantic",
            tags=["worker", worker.type.value]
        )
    
    def get_worker(self, worker_id: str) -> Optional[BaseAgent]:
        """Get a worker by ID."""
        return self.workers.get(worker_id)
    
    def list_workers(self) -> List[Dict]:
        """List all workers."""
        return [w.to_dict() for w in self.workers.values()]
    
    # ===========================================
    # STRATEGIC PLANNING
    # ===========================================
    
    async def plan_startup(
        self,
        company_name: str,
        idea: str,
        target_market: str = ""
    ) -> Dict:
        """
        Create a comprehensive startup plan.
        
        Args:
            company_name: Company name
            idea: The core idea/product
            target_market: Target customer segment
        
        Returns:
            Comprehensive plan with goals and tasks
        """
        self.set_company(company_name, f"Building {idea}")
        
        # Create strategic goals
        goals = [
            {
                "goal": "Market Research & Validation",
                "priority": "high",
                "tasks": [
                    ("Research target market", "research"),
                    ("Analyze competitors", "research"),
                    ("Define MVP features", "planning")
                ]
            },
            {
                "goal": "Product Development",
                "priority": "high",
                "tasks": [
                    ("Create landing page", "coding"),
                    ("Build MVP", "coding"),
                    ("Set up deployment", "devops")
                ]
            },
            {
                "goal": "Go-to-Market Strategy",
                "priority": "medium",
                "tasks": [
                    ("Create marketing materials", "marketing"),
                    ("Set up social media", "marketing"),
                    ("Plan launch campaign", "planning")
                ]
            }
        ]
        
        # Add goals and tasks
        for g in goals:
            goal_id = self.add_goal(g["goal"], priority=g["priority"])
            
            for task_title, task_type in g["tasks"]:
                self.create_task(
                    title=task_title,
                    task_type=task_type,
                    goal_id=goal_id
                )
        
        return {
            "company": self.company_name,
            "idea": idea,
            "goals": len(self.goals),
            "tasks": len(self.tasks),
            "plan": goals
        }
    
    # ===========================================
    # EXECUTION
    # ===========================================
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task as the CEO."""
        task_type = task.get("type", "general")
        
        if task_type == "planning":
            # Create a plan
            return await self._execute_planning(task)
        elif task_type == "delegation":
            # Delegate to appropriate worker
            return await self._execute_delegation(task)
        else:
            # Handle directly or research
            return await self._execute_direct(task)
    
    async def _execute_planning(self, task: Dict) -> Dict:
        """Execute a planning task."""
        prompt = f"""Create a detailed plan for: {task.get('title', 'Unknown')}

Consider:
- Steps needed
- Resources required
- Potential blockers
- Timeline estimates"""
        
        plan = await self.think(prompt)
        
        return {
            "task_id": task.get("id"),
            "plan": plan,
            "status": "completed"
        }
    
    async def _execute_delegation(self, task: Dict) -> Dict:
        """Execute a delegation task."""
        # Find best worker for task
        task_type = task.get("type", "general")
        
        # Simple matching
        worker_map = {
            "coding": "coder",
            "design": "designer",
            "research": "researcher",
            "marketing": "marketer",
            "writing": "writer",
            "devops": "devops"
        }
        
        worker_id = worker_map.get(task_type, "general")
        
        if worker_id in self.workers:
            self.delegate_task(task["id"], worker_id)
            return {
                "task_id": task["id"],
                "delegated_to": worker_id,
                "status": "delegated"
            }
        
        return {
            "task_id": task["id"],
            "status": "no_worker_available"
        }
    
    async def _execute_direct(self, task: Dict) -> Dict:
        """Execute directly."""
        prompt = f"""Execute this task: {task.get('title', 'Unknown')}
        
Description: {task.get('description', 'No description')}

Provide a detailed response on how to approach this task."""
        
        result = await self.think(prompt)
        
        return {
            "task_id": task.get("id"),
            "result": result,
            "status": "completed"
        }
    
    # ===========================================
    # REPORTING
    # ===========================================
    
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
