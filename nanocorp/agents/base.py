"""
NanoCorp v3.0 - Base Agent

Foundation for all agents with tool access and memory.
"""
from __future__ import annotations

import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum

from pydantic import BaseModel

from ..tools.base import BaseTool, ToolOutput, success_result, error_result
from ..tools.registry import get_registry
from ..memory.core import AgentMemory


# ===========================================
# AGENT TYPES
# ===========================================

class AgentType(str, Enum):
    """Agent types."""
    CEO = "ceo"
    CODER = "coder"
    DESIGNER = "designer"
    RESEARCHER = "researcher"
    MARKETER = "marketer"
    WRITER = "writer"
    DATA = "data"
    DEVOPS = "devops"
    GENERAL = "general"


# ===========================================
# AGENT STATE
# ===========================================

@dataclass
class AgentState:
    """Current state of an agent."""
    id: str
    name: str
    agent_type: AgentType
    status: str = "idle"  # idle, thinking, working, waiting, done
    current_task: Optional[str] = None
    tools_used: List[str] = field(default_factory=list)
    messages: List[Dict] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_active: str = field(default_factory=lambda: datetime.now().isoformat())


# ===========================================
# MESSAGE
# ===========================================

@dataclass
class Message:
    """Agent message."""
    from_agent: str
    to_agent: Optional[str]  # None = broadcast
    content: str
    type: str = "message"  # message, task, result, error
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ===========================================
# BASE AGENT
# ===========================================

class BaseAgent(ABC):
    """
    Base class for all agents.
    
    Provides:
    - Tool execution
    - Memory access
    - Message handling
    - State management
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        agent_type: AgentType = AgentType.GENERAL,
        tools: Optional[List[str]] = None,
        system_prompt: Optional[str] = None,
        memory: Optional[AgentMemory] = None,
        ai_provider: Optional[Any] = None
    ):
        self.id = agent_id
        self.name = name
        self.type = agent_type
        self.tools = tools or []
        self.system_prompt = system_prompt or self._default_prompt()
        self.memory = memory
        self.ai_provider = ai_provider
        
        self.state = AgentState(
            id=agent_id,
            name=name,
            agent_type=agent_type
        )
        
        self._tool_registry = get_registry()
        self._message_handlers: Dict[str, Callable] = {}
        self._inbox: List[Message] = []
    
    def _default_prompt(self) -> str:
        """Default system prompt."""
        return f"""You are {self.name}, a {self.type.value} agent.
Think step by step and use tools when needed.
Be helpful, concise, and professional."""
    
    # ===========================================
    # TOOL EXECUTION
    # ===========================================
    
    def can_use_tool(self, tool_name: str) -> bool:
        """Check if agent can use a tool."""
        if not self.tools:  # Empty list means all tools
            return True
        return tool_name in self.tools
    
    def list_available_tools(self) -> List[str]:
        """List all tools agent can use."""
        if not self.tools:
            return self._tool_registry.list_all()
        return [t for t in self.tools if self._tool_registry.get(t)]
    
    async def execute_tool(self, tool_name: str, **kwargs) -> ToolOutput:
        """
        Execute a tool.
        
        Args:
            tool_name: Name of tool to execute
            **kwargs: Tool arguments
        
        Returns:
            Tool output
        """
        if not self.can_use_tool(tool_name):
            return error_result(f"Agent cannot use tool: {tool_name}")
        
        tool = self._tool_registry.get(tool_name)
        if not tool:
            return error_result(f"Tool not found: {tool_name}")
        
        self.state.status = "working"
        self.state.tools_used.append(tool_name)
        
        try:
            result = tool.execute(**kwargs)
            return result
        except Exception as e:
            return error_result(f"Tool execution failed: {e}")
        finally:
            self.state.status = "idle"
    
    def execute_tool_sync(self, tool_name: str, **kwargs) -> ToolOutput:
        """Synchronous tool execution."""
        return asyncio.run(self.execute_tool(tool_name, **kwargs))
    
    # ===========================================
    # MEMORY
    # ===========================================
    
    def remember(self, content: str, **kwargs):
        """Store a memory."""
        if self.memory:
            self.memory.remember(content, **kwargs)
    
    def recall(self, query: str, **kwargs):
        """Recall memories."""
        if self.memory:
            return self.memory.recall(query, **kwargs)
        return []
    
    def learn(self, experience: str, outcome: str, **kwargs):
        """Learn from experience."""
        if self.memory:
            self.memory.learn(experience, outcome, **kwargs)
    
    # ===========================================
    # MESSAGING
    # ===========================================
    
    def send_message(self, to: str, content: str, msg_type: str = "message", **metadata):
        """Send a message to another agent."""
        msg = Message(
            from_agent=self.id,
            to_agent=to,
            content=content,
            type=msg_type,
            metadata=metadata
        )
        # This would be handled by the agent manager
        return msg
    
    def broadcast(self, content: str, msg_type: str = "message", **metadata):
        """Broadcast to all agents."""
        return self.send_message(None, content, msg_type, **metadata)
    
    def receive_message(self, message: Message):
        """Receive a message."""
        self._inbox.append(message)
        self.state.last_active = datetime.now().isoformat()
        
        # Call handler if registered
        if message.type in self._message_handlers:
            self._message_handlers[message.type](message)
    
    def on_message(self, msg_type: str, handler: Callable[[Message], None]):
        """Register a message handler."""
        self._message_handlers[msg_type] = handler
    
    def get_messages(self, msg_type: Optional[str] = None) -> List[Message]:
        """Get messages from inbox."""
        if msg_type:
            return [m for m in self._inbox if m.type == msg_type]
        return list(self._inbox)
    
    def clear_messages(self):
        """Clear inbox."""
        self._inbox.clear()
    
    # ===========================================
    # AI INTERACTION
    # ===========================================
    
    async def think(self, prompt: str) -> str:
        """
        Use AI to think about something.
        
        Args:
            prompt: What to think about
        
        Returns:
            AI response
        """
        if self.ai_provider:
            return await self.ai_provider.chat(prompt)
        
        # Fallback: just return the prompt as thought
        return f"[AI not configured] Thinking about: {prompt}"
    
    async def plan(self, goal: str) -> List[str]:
        """
        Create a plan to achieve a goal.
        
        Args:
            goal: The goal to plan for
        
        Returns:
            List of steps
        """
        prompt = f"""Create a plan to achieve this goal: {goal}

Break it down into specific, actionable steps."""
        
        response = await self.think(prompt)
        
        # Parse steps (simple implementation)
        steps = [s.strip() for s in response.split('\n') if s.strip()]
        return steps
    
    # ===========================================
    # ABSTRACT METHODS
    # ===========================================
    
    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task.
        
        Args:
            task: Task definition
        
        Returns:
            Task result
        """
        pass
    
    # ===========================================
    # STATE
    # ===========================================
    
    def get_state(self) -> AgentState:
        """Get agent state."""
        self.state.last_active = datetime.now().isoformat()
        return self.state
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "state": {
                "status": self.state.status,
                "current_task": self.state.current_task,
                "tools_used": self.state.tools_used,
                "created_at": self.state.created_at,
                "last_active": self.state.last_active
            },
            "tools": self.list_available_tools(),
            "unread_messages": len(self._inbox)
        }
