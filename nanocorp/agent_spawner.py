"""
NanoCorp Agent Spawning System

Dynamic agent creation and management.
CEO can spawn temporary workers for sub-tasks.
"""
import uuid
import threading
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json


class AgentState(Enum):
    """Agent lifecycle states"""
    SPAWNING = "spawning"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"


@dataclass
class SpawnedAgent:
    """A dynamically spawned agent"""
    id: str
    name: str
    role: str  # specialist role
    task: str
    state: AgentState
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict] = None
    parent_id: Optional[str] = None
    children_ids: List[str] = None


class AgentSpawner:
    """
    Dynamic agent spawning system.
    
    Spawns temporary agents for specific tasks,
    manages their lifecycle, and collects results.
    """
    
    def __init__(self, free_ai=None, workspace: str = None):
        self.free_ai = free_ai
        self.workspace = Path(workspace) if workspace else Path("./workspace")
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        self.agents: Dict[str, SpawnedAgent] = {}
        self.agent_states: Dict[str, AgentState] = {}
        self.results: Dict[str, Any] = {}
        self.subscribers: Dict[str, List[Callable]] = {}
        
        self._lock = threading.Lock()
        self._spawn_thread: Optional[threading.Thread] = None
        self._running = False
    
    def spawn(
        self,
        role: str,
        task: str,
        parent_id: str = None,
        wait_for_result: bool = False,
        timeout: float = 300
    ) -> str:
        """
        Spawn a new agent for a task.
        
        Args:
            role: Agent role (writer, coder, researcher, etc.)
            task: Task description
            parent_id: Parent agent ID (for hierarchical spawning)
            wait_for_result: Block until result is ready
            timeout: Max seconds to wait
        
        Returns:
            Agent ID
        """
        agent_id = str(uuid.uuid4())[:8]
        
        agent = SpawnedAgent(
            id=agent_id,
            name=f"{role.title()}-{agent_id}",
            role=role,
            task=task,
            state=AgentState.SPAWNING,
            created_at=datetime.now().isoformat(),
            parent_id=parent_id,
            children_ids=[]
        )
        
        with self._lock:
            self.agents[agent_id] = agent
            if parent_id and parent_id in self.agents:
                self.agents[parent_id].children_ids.append(agent_id)
        
        # Start execution
        thread = threading.Thread(
            target=self._execute_agent,
            args=(agent_id, timeout)
        )
        thread.start()
        
        if wait_for_result:
            thread.join(timeout=timeout)
        
        return agent_id
    
    def _execute_agent(self, agent_id: str, timeout: float):
        """Execute an agent's task"""
        if agent_id not in self.agents:
            return
        
        agent = self.agents[agent_id]
        agent.state = AgentState.RUNNING
        agent.started_at = datetime.now().isoformat()
        
        self._notify("on_agent_started", agent)
        
        try:
            # Build prompt based on role
            prompt = self._build_role_prompt(agent.role, agent.task)
            
            # Execute with AI
            if self.free_ai:
                result_text = self.free_ai.chat(prompt)
            else:
                result_text = f"[Agent {agent.name}] Task received: {agent.task[:100]}..."
            
            # Parse result
            result = {
                "agent_id": agent_id,
                "role": agent.role,
                "task": agent.task,
                "output": result_text,
                "completed_at": datetime.now().isoformat()
            }
            
            with self._lock:
                agent.state = AgentState.COMPLETED
                agent.completed_at = datetime.now().isoformat()
                agent.result = result
                self.results[agent_id] = result
            
            self._notify("on_agent_completed", agent)
            
        except Exception as e:
            with self._lock:
                agent.state = AgentState.FAILED
                agent.result = {"error": str(e)}
            
            self._notify("on_agent_failed", agent)
    
    def _build_role_prompt(self, role: str, task: str) -> str:
        """Build a prompt based on agent role"""
        role_prompts = {
            "writer": f"""You are an expert content writer.
Task: {task}
Write high-quality content that is engaging, informative, and well-structured.""",
            
            "coder": f"""You are an expert software developer.
Task: {task}
Write clean, well-documented code following best practices.""",
            
            "researcher": f"""You are an expert researcher.
Task: {task}
Provide thorough analysis with data-backed insights.""",
            
            "marketer": f"""You are an expert marketer.
Task: {task}
Create compelling marketing strategies and content.""",
            
            "designer": f"""You are an expert designer.
Task: {task}
Create beautiful, user-centered designs.""",
            
            "analyst": f"""You are an expert analyst.
Task: {task}
Provide deep insights and actionable recommendations.""",
            
            "default": f"""You are a helpful AI assistant.
Task: {task}
Complete this task thoroughly and professionally."""
        }
        
        return role_prompts.get(role.lower(), role_prompts["default"])
    
    def get_agent(self, agent_id: str) -> Optional[SpawnedAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def get_result(self, agent_id: str, timeout: float = 60) -> Optional[Dict]:
        """Get agent result, waiting if necessary"""
        start = datetime.now()
        
        while (datetime.now() - start).total_seconds() < timeout:
            if agent_id in self.results:
                return self.results[agent_id]
            
            agent = self.agents.get(agent_id)
            if agent and agent.state in [AgentState.COMPLETED, AgentState.FAILED]:
                return agent.result
            
            import time
            time.sleep(0.5)
        
        return None
    
    def wait_for_children(self, parent_id: str, timeout: float = 300) -> List[Dict]:
        """Wait for all child agents to complete"""
        start = datetime.now()
        children = []
        
        with self._lock:
            child_ids = list(self.agents.get(parent_id, SpawnedAgent("", "", "", "", AgentState.SPAWNING)).children_ids or [])
        
        for child_id in child_ids:
            result = self.get_result(child_id, timeout - (datetime.now() - start).total_seconds())
            if result:
                children.append(result)
        
        return children
    
    def terminate(self, agent_id: str) -> bool:
        """Terminate an agent"""
        if agent_id in self.agents:
            with self._lock:
                self.agents[agent_id].state = AgentState.TERMINATED
            return True
        return False
    
    def subscribe(self, event: str, callback: Callable):
        """Subscribe to agent events"""
        if event not in self.subscribers:
            self.subscribers[event] = []
        self.subscribers[event].append(callback)
    
    def _notify(self, event: str, agent: SpawnedAgent):
        """Notify subscribers of events"""
        for callback in self.subscribers.get(event, []):
            try:
                callback(agent)
            except:
                pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get spawner status"""
        counts = {s.value: 0 for s in AgentState}
        for agent in self.agents.values():
            counts[agent.state.value] += 1
        
        return {
            "total_agents": len(self.agents),
            "by_state": counts,
            "active": counts.get("running", 0) + counts.get("spawning", 0),
            "completed": counts.get("completed", 0),
            "failed": counts.get("failed", 0)
        }


class HierarchicalCEO:
    """
    A CEO that spawns a team of agents for complex tasks.
    
    Decomposes large goals into sub-tasks and assigns
    specialized agents to handle each one.
    """
    
    def __init__(self, spawner: AgentSpawner, free_ai=None):
        self.spawner = spawner
        self.free_ai = free_ai
        self.team: Dict[str, str] = {}  # role -> agent_id
    
    def assemble_team(self, roles: List[str]) -> Dict[str, str]:
        """Assemble a team of specialists"""
        for role in roles:
            agent_id = self.spawner.spawn(
                role=role,
                task=f"Standby as {role} specialist",
                wait_for_result=False
            )
            self.team[role] = agent_id
        
        return self.team
    
    def assign_task(self, role: str, task: str, wait: bool = True) -> Optional[Dict]:
        """Assign a task to a team member"""
        if role not in self.team:
            # Spawn new agent
            agent_id = self.spawner.spawn(role=role, task=task, wait_for_result=wait)
            self.team[role] = agent_id
        else:
            # Reassign existing agent
            agent_id = self.team[role]
            self.spawner.terminate(agent_id)
            agent_id = self.spawner.spawn(role=role, task=task, wait_for_result=wait)
            self.team[role] = agent_id
        
        if wait:
            return self.spawner.get_result(agent_id)
        return {"agent_id": agent_id, "status": "spawned"}
    
    def parallel_execute(self, tasks: Dict[str, str]) -> Dict[str, Dict]:
        """Execute multiple tasks in parallel with different roles"""
        results = {}
        
        for role, task in tasks.items():
            agent_id = self.spawner.spawn(role=role, task=task, wait_for_result=False)
            results[role] = {"agent_id": agent_id, "task": task}
        
        return results
    
    def get_all_results(self, timeout: float = 300) -> Dict[str, Dict]:
        """Collect results from all team members"""
        results = {}
        
        for role, agent_id in self.team.items():
            result = self.spawner.get_result(agent_id, timeout=timeout)
            results[role] = result
        
        return results
