"""
CEO Agent - Strategic Leadership and Task Coordination
The CEO agent creates tasks, sets priorities, and coordinates worker agents
"""
import os
import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from pathlib import Path

from openhands.sdk import LLM, Agent, Conversation, Tool

from .task_manager import TaskManager, Task, TaskStatus, TaskPriority, TaskCategory


# System prompt for the CEO agent
CEO_SYSTEM_PROMPT = """You are the CEO of NanoCorp, an AI-powered autonomous business.
You are a strategic thinker who plans, delegates, and ensures the company succeeds.

Your responsibilities:
1. STRATEGIC PLANNING: Analyze situations, set goals, and create action plans
2. TASK CREATION: Break down goals into actionable tasks with clear priorities
3. DELEGATION: Assign tasks to the right worker agents based on their specialties
4. COORDINATION: Ensure tasks are executed in the right order and dependencies are met
5. QUALITY CONTROL: Review outputs and ensure standards are met

Business functions you can delegate to:
- WebDev: Website creation, landing pages, web applications
- Marketing: Marketing strategies, campaigns, advertising
- Content: Blog posts, articles, copywriting
- SocialMedia: Social media posts, engagement, community management
- Email: Email campaigns, newsletters, outreach
- Document: Business documents, reports, proposals
- Researcher: Market research, competitive analysis, data gathering
- Networker: Partnership outreach, networking, relationship building

When given a goal or objective:
1. Analyze the goal and break it down into specific tasks
2. Determine task priorities and dependencies
3. Assign tasks to appropriate agents
4. Monitor progress and coordinate execution
5. Review results and iterate as needed

Always think strategically about the big picture while ensuring execution excellence.
"""


class CEOSystem:
    """
    CEO Agent System - The main orchestrator for NanoCorp
    Manages strategic planning, task creation, and worker coordination
    """
    
    def __init__(
        self,
        llm: LLM,
        task_manager: TaskManager,
        workspace_path: Path,
        max_concurrent_workers: int = 5
    ):
        self.llm = llm
        self.task_manager = task_manager
        self.workspace_path = workspace_path
        self.max_concurrent_workers = max_concurrent_workers
        
        # Initialize the CEO agent
        self.agent = Agent(
            llm=llm,
            tools=[],  # Will use built-in tools from the server
            system_prompt=CEO_SYSTEM_PROMPT,
            name="CEO",
            include_default_tools=True
        )
        
        self.conversation = Conversation(
            agent=self.agent,
            workspace=str(workspace_path)
        )
        
        # Worker registry
        self.workers: Dict[str, 'WorkerAgent'] = {}
        
        # Execution history
        self.execution_log: List[Dict[str, Any]] = []
        
        # Company state
        self.company_context: Dict[str, Any] = {
            "name": "NanoCorp",
            "mission": "",
            "current_project": None,
            "active_workers": []
        }
    
    def register_worker(self, worker: 'WorkerAgent'):
        """Register a worker agent"""
        self.workers[worker.name] = worker
        self.company_context["active_workers"].append(worker.name)
    
    def set_company_info(self, name: str, mission: str, current_project: str = None):
        """Set company information"""
        self.company_context["name"] = name
        self.company_context["mission"] = mission
        if current_project:
            self.company_context["current_project"] = current_project
    
    def create_strategic_plan(self, objective: str) -> List[Dict[str, Any]]:
        """
        Create a strategic plan for achieving an objective
        Returns a list of task specifications
        """
        prompt = f"""Create a strategic plan for: {objective}

Analyze the objective and break it down into specific, actionable tasks.
For each task provide:
1. Title: Clear, actionable task name
2. Description: What needs to be done
3. Priority: critical, high, medium, or low
4. Category: Which worker should handle it (web_dev, marketing, content, social_media, email, document, research, networking)
5. Dependencies: Which tasks must complete first (by title)

Return your response as a JSON array of task objects.
"""
        
        # Use the LLM to generate the plan
        response = self.llm.generate(prompt, system=CEO_SYSTEM_PROMPT)
        
        # Parse the response and create tasks
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                tasks_spec = json.loads(json_match.group())
            else:
                tasks_spec = []
        except:
            tasks_spec = []
        
        created_tasks = []
        for spec in tasks_spec:
            task = self.task_manager.create_task(
                title=spec.get("title", "Untitled Task"),
                description=spec.get("description", ""),
                priority=TaskPriority(spec.get("priority", "medium")),
                category=TaskCategory(spec.get("category", "custom")),
                created_by="ceo"
            )
            created_tasks.append(task)
        
        return created_tasks
    
    def delegate_task(self, task_id: str, worker_name: str = None) -> bool:
        """
        Delegate a task to a worker agent
        If worker_name is not provided, auto-assign based on task category
        """
        task = self.task_manager.get_task(task_id)
        if not task:
            return False
        
        if worker_name is None:
            # Auto-assign based on category
            category_to_worker = {
                TaskCategory.WEB_DEV: "WebDev",
                TaskCategory.MARKETING: "Marketing",
                TaskCategory.CONTENT: "Content",
                TaskCategory.SOCIAL_MEDIA: "SocialMedia",
                TaskCategory.EMAIL: "Email",
                TaskCategory.DOCUMENTATION: "Document",
                TaskCategory.RESEARCH: "Researcher",
                TaskCategory.NETWORKING: "Networker",
            }
            worker_name = category_to_worker.get(task.category, "General")
        
        self.task_manager.assign_task(task_id, worker_name)
        
        # Log the delegation
        self.log_execution("delegation", {
            "task_id": task_id,
            "task_title": task.title,
            "assigned_to": worker_name
        })
        
        return True
    
    def execute_task(self, task_id: str) -> Dict[str, Any]:
        """Execute a specific task with the assigned worker"""
        task = self.task_manager.get_task(task_id)
        if not task:
            return {"error": "Task not found"}
        
        if task.assigned_to and task.assigned_to in self.workers:
            worker = self.workers[task.assigned_to]
            self.task_manager.start_task(task_id)
            
            try:
                result = worker.execute_task(task)
                self.task_manager.complete_task(task_id, result)
                
                self.log_execution("task_completed", {
                    "task_id": task_id,
                    "task_title": task.title,
                    "worker": worker.name,
                    "result": result
                })
                
                return result
            except Exception as e:
                self.task_manager.fail_task(task_id, str(e))
                self.log_execution("task_failed", {
                    "task_id": task_id,
                    "task_title": task.title,
                    "error": str(e)
                })
                return {"error": str(e)}
        
        return {"error": "No worker assigned or worker not found"}
    
    def execute_ready_tasks(self, max_tasks: int = None) -> List[Dict[str, Any]]:
        """Execute all ready tasks (no blocking dependencies)"""
        ready_tasks = self.task_manager.get_ready_tasks()
        
        if max_tasks:
            ready_tasks = ready_tasks[:max_tasks]
        
        results = []
        for task in ready_tasks:
            # Ensure task is assigned
            if not task.assigned_to:
                self.delegate_task(task.id)
            
            result = self.execute_task(task.id)
            results.append({
                "task_id": task.id,
                "result": result
            })
        
        return results
    
    def run_strategy_session(self, objective: str, execute: bool = True) -> Dict[str, Any]:
        """
        Run a complete strategy session
        1. Create the plan
        2. Delegate tasks
        3. Execute tasks
        """
        self.log_execution("strategy_session_start", {"objective": objective})
        
        # Create the strategic plan
        tasks = self.create_strategic_plan(objective)
        
        # Delegate all tasks
        for task in tasks:
            self.delegate_task(task.id)
        
        # Execute tasks if requested
        if execute:
            self.execute_ready_tasks()
        
        self.log_execution("strategy_session_end", {
            "objective": objective,
            "tasks_created": len(tasks),
            "board": self.task_manager.get_board_view()
        })
        
        return {
            "objective": objective,
            "tasks_created": len(tasks),
            "board": self.task_manager.get_board_view()
        }
    
    def handle_user_request(self, request: str) -> str:
        """Handle a user request - main interface for interaction"""
        prompt = f"""The user has made the following request:

{request}

As the CEO of NanoCorp, analyze this request and determine:
1. What needs to be done
2. How to break it down into tasks
3. Which workers should handle each part

Then create the necessary tasks and begin execution as appropriate.

Current company context:
{json.dumps(self.company_context, indent=2)}

Current task board:
{json.dumps(self.task_manager.get_board_view(), indent=2)}

Provide your analysis, planned actions, and begin executing where appropriate.
"""
        
        response = self.conversation.send_message(prompt)
        return response
    
    def log_execution(self, event_type: str, data: Dict[str, Any]):
        """Log an execution event"""
        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        })
    
    def get_status_report(self) -> Dict[str, Any]:
        """Generate a status report"""
        return {
            "company": self.company_context,
            "statistics": self.task_manager.get_statistics(),
            "board": self.task_manager.get_board_view(),
            "active_workers": list(self.workers.keys()),
            "recent_execution": self.execution_log[-10:] if self.execution_log else []
        }
    
    def save_state(self, path: Path):
        """Save the CEO system state"""
        state = {
            "company_context": self.company_context,
            "execution_log": self.execution_log,
            "tasks": {tid: task.to_dict() for tid, task in self.task_manager.tasks.items()}
        }
        with open(path, 'w') as f:
            json.dump(state, f, indent=2, default=str)
    
    def load_state(self, path: Path):
        """Load the CEO system state"""
        if path.exists():
            with open(path, 'r') as f:
                state = json.load(f)
                self.company_context = state.get("company_context", {})
                self.execution_log = state.get("execution_log", [])
                # Reload tasks into task manager
                for tid, tdata in state.get("tasks", {}).items():
                    self.task_manager.tasks[tid] = Task.from_dict(tdata)


class WorkerAgent:
    """
    Base class for worker agents
    Specialized agents that execute specific types of tasks
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        specialties: List[str],
        llm: LLM,
        workspace_path: Path,
        tools: List[Tool] = None
    ):
        self.name = name
        self.description = description
        self.specialties = specialties
        self.llm = llm
        self.workspace_path = workspace_path
        
        # Build the system prompt
        system_prompt = f"""You are {name}, a specialized worker agent at NanoCorp.

Your role: {description}

Your specialties include:
{chr(10).join(f"- {s}" for s in specialties)}

You execute tasks assigned to you by the CEO with precision and quality.
When given a task:
1. Understand the requirements clearly
2. Execute the work efficiently
3. Report results clearly

Always maintain high standards and professional output.
"""
        
        self.agent = Agent(
            llm=llm,
            tools=tools or [],
            system_prompt=system_prompt,
            name=name,
            include_default_tools=[]
        )
        
        self.conversation = Conversation(
            agent=self.agent,
            workspace=str(workspace_path / name.lower())
        )
        
        self.task_history: List[Dict[str, Any]] = []
    
    def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a task and return results"""
        prompt = f"""Execute the following task:

Title: {task.title}
Description: {task.description}

Context:
{json.dumps(task.context, indent=2)}

Provide a detailed report of:
1. What you did
2. The outputs created
3. Any files generated
4. Recommendations for next steps
"""
        
        start_time = datetime.now()
        
        try:
            response = self.conversation.send_message(prompt)
            
            result = {
                "success": True,
                "response": response,
                "task_id": task.id,
                "worker": self.name,
                "duration": (datetime.now() - start_time).total_seconds()
            }
            
            self.task_history.append({
                "task_id": task.id,
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "response": response
            })
            
            return result
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "task_id": task.id,
                "worker": self.name
            }
            
            self.task_history.append({
                "task_id": task.id,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            })
            
            return error_result
    
    def get_specialty_prompt(self, specialty: str) -> str:
        """Get a specialized prompt for a specific task type"""
        return f"You are executing a {specialty} task as {self.name}."
