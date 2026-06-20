"""
NanoCorp v3.0 - Agent Manager

Coordinates all agents, handles messaging, and manages the workforce.
"""
from __future__ import annotations

import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path

from .base import BaseAgent, AgentType, Message
from .ceo import CEOAgent
from .worker import WorkerAgent


@dataclass
class WorkforceStats:
    """Statistics about the workforce."""
    total_agents: int = 0
    active_agents: int = 0
    tasks_completed: int = 0
    tasks_pending: int = 0
    tasks_failed: int = 0
    uptime: str = ""


class AgentManager:
    """
    Manages all agents and their interactions.
    
    Handles:
    - Agent registration
    - Message routing
    - Task delegation
    - Resource allocation
    """
    
    def __init__(
        self,
        memory: Optional[Any] = None,
        ai_provider: Optional[Any] = None
    ):
        self.agents: Dict[str, BaseAgent] = {}
        self.memory = memory
        self.ai_provider = ai_provider
        
        self._started_at = datetime.now()
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._running = False
        self._message_queue: asyncio.Queue = asyncio.Queue()
    
    # ===========================================
    # AGENT MANAGEMENT
    # ===========================================
    
    def register_agent(self, agent: BaseAgent):
        """
        Register an agent.
        
        Args:
            agent: Agent to register
        """
        self.agents[agent.id] = agent
        self._emit("agent_registered", {"agent_id": agent.id, "agent": agent})
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            del self.agents[agent_id]
            self._emit("agent_unregistered", {"agent_id": agent_id})
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID."""
        return self.agents.get(agent_id)
    
    def list_agents(self, agent_type: Optional[AgentType] = None) -> List[BaseAgent]:
        """List all agents, optionally filtered by type."""
        agents = list(self.agents.values())
        
        if agent_type:
            agents = [a for a in agents if a.type == agent_type]
        
        return agents
    
    # ===========================================
    # WORKFORCE CREATION
    # ===========================================
    
    def create_workforce(
        self,
        company_name: str = "My Company",
        mission: str = "",
        worker_types: Optional[List[AgentType]] = None
    ):
        """
        Create a complete workforce.
        
        Args:
            company_name: Company name
            mission: Company mission
            worker_types: Types of workers to create
        
        Returns:
            CEO agent
        """
        # Create CEO
        ceo = CEOAgent(
            name="CEO",
            memory=self.memory,
            ai_provider=self.ai_provider,
            company_name=company_name,
            mission=mission
        )
        self.register_agent(ceo)
        
        # Create workers
        if worker_types is None:
            worker_types = [
                AgentType.CODER,
                AgentType.DESIGNER,
                AgentType.RESEARCHER,
                AgentType.MARKETER,
                AgentType.WRITER
            ]
        
        for worker_type in worker_types:
            worker = WorkerAgent(
                name=worker_type.value.title(),
                agent_type=worker_type,
                memory=self.memory,
                ai_provider=self.ai_provider
            )
            self.register_agent(worker)
            ceo.register_worker(worker)
        
        self._emit("workforce_created", {
            "ceo": ceo.id,
            "workers": [w.id for w in self.agents.values() if w.id != ceo.id]
        })
        
        return ceo
    
    # ===========================================
    # MESSAGING
    # ===========================================
    
    async def send_message(
        self,
        from_agent: str,
        to_agent: str,
        content: str,
        msg_type: str = "message"
    ):
        """
        Send a message between agents.
        
        Args:
            from_agent: Sender ID
            to_agent: Receiver ID
            content: Message content
            msg_type: Message type
        """
        sender = self.agents.get(from_agent)
        receiver = self.agents.get(to_agent)
        
        if not sender or not receiver:
            return False
        
        message = Message(
            from_agent=from_agent,
            to_agent=to_agent,
            content=content,
            type=msg_type
        )
        
        receiver.receive_message(message)
        self._emit("message_sent", {
            "from": from_agent,
            "to": to_agent,
            "type": msg_type
        })
        
        return True
    
    async def broadcast(
        self,
        from_agent: str,
        content: str,
        msg_type: str = "message"
    ):
        """
        Broadcast a message to all agents.
        
        Args:
            from_agent: Sender ID
            content: Message content
            msg_type: Message type
        """
        for agent in self.agents.values():
            if agent.id != from_agent:
                await self.send_message(from_agent, agent.id, content, msg_type)
    
    # ===========================================
    # TASK EXECUTION
    # ===========================================
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task.
        
        Finds the best agent and delegates.
        """
        # Find best agent for task
        task_type = task.get("type", "general")
        
        # Map task types to agent types
        type_map = {
            "coding": AgentType.CODER,
            "design": AgentType.DESIGNER,
            "research": AgentType.RESEARCHER,
            "marketing": AgentType.MARKETER,
            "writing": AgentType.WRITER,
            "data": AgentType.DATA,
            "devops": AgentType.DEVOPS
        }
        
        best_type = type_map.get(task_type, AgentType.GENERAL)
        best_agent = self._find_best_agent(best_type)
        
        if not best_agent:
            return {
                "success": False,
                "error": f"No agent available for {task_type}"
            }
        
        # Execute
        self._emit("task_started", {"task": task, "agent": best_agent.id})
        
        result = await best_agent.execute_task(task)
        
        self._emit("task_completed", {
            "task": task,
            "agent": best_agent.id,
            "result": result
        })
        
        return result
    
    def _find_best_agent(self, preferred_type: AgentType) -> Optional[BaseAgent]:
        """
        Find the best available agent.
        
        Prioritizes agents that are idle.
        """
        # Find idle agents of preferred type
        idle_of_type = [
            a for a in self.agents.values()
            if a.type == preferred_type and a.state.status == "idle"
        ]
        
        if idle_of_type:
            return idle_of_type[0]
        
        # Find any idle agent
        idle = [
            a for a in self.agents.values()
            if a.type != AgentType.CEO and a.state.status == "idle"
        ]
        
        if idle:
            return idle[0]
        
        # Any agent
        agents = [
            a for a in self.agents.values()
            if a.type != AgentType.CEO
        ]
        
        return agents[0] if agents else None
    
    async def execute_parallel(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute multiple tasks in parallel.
        
        Args:
            tasks: List of tasks
        
        Returns:
            List of results
        """
        results = await asyncio.gather(
            *[self.execute_task(task) for task in tasks],
            return_exceptions=True
        )
        
        # Convert exceptions to error dicts
        processed = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed.append({
                    "success": False,
                    "error": str(result),
                    "task_id": tasks[i].get("id")
                })
            else:
                processed.append(result)
        
        return processed
    
    # ===========================================
    # EVENTS
    # ===========================================
    
    def on_event(self, event: str, handler: Callable):
        """Register an event handler."""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
    
    def _emit(self, event: str, data: Dict):
        """Emit an event."""
        for handler in self._event_handlers.get(event, []):
            try:
                handler(data)
            except Exception as e:
                print(f"Event handler error: {e}")
    
    # ===========================================
    # STATUS & METRICS
    # ===========================================
    
    def get_stats(self) -> WorkforceStats:
        """Get workforce statistics."""
        active = len([a for a in self.agents.values() if a.state.status != "idle"])
        
        # Count tasks
        completed = 0
        pending = 0
        failed = 0
        
        for agent in self.agents.values():
            if hasattr(agent, "task_history"):
                for task in agent.task_history:
                    if task.get("success"):
                        completed += 1
                    else:
                        failed += 1
            if agent.state.status == "idle":
                pending += 1
        
        uptime = datetime.now() - self._started_at
        
        return WorkforceStats(
            total_agents=len(self.agents),
            active_agents=active,
            tasks_completed=completed,
            tasks_pending=pending,
            tasks_failed=failed,
            uptime=str(uptime).split(".")[0]
        )
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Get full workforce dashboard."""
        return {
            "stats": self.get_stats().__dict__,
            "agents": {
                agent_id: agent.to_dict()
                for agent_id, agent in self.agents.items()
            },
            "ceo": self.agents.get("ceo").to_dict() if "ceo" in self.agents else None
        }
    
    # ===========================================
    # LIFECYCLE
    # ===========================================
    
    async def start(self):
        """Start the agent manager."""
        self._running = True
        self._emit("manager_started", {})
        
        # Start message processing loop
        while self._running:
            try:
                await asyncio.sleep(1)
            except Exception as e:
                print(f"Manager error: {e}")
    
    def stop(self):
        """Stop the agent manager."""
        self._running = False
        self._emit("manager_stopped", {})
