"""
NanoCorp v3.0 - Worker Agents

Specialized agents with tool access for different domains.
"""
from __future__ import annotations

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from .base import BaseAgent, AgentType, Message


# ===========================================
# WORKER SYSTEM PROMPTS
# ===========================================

WORKER_PROMPTS = {
    AgentType.GENERAL: """You are a versatile AI assistant.

Your responsibilities:
- Help with any task asked of you
- Use available tools effectively
- Learn from interactions
- Be helpful and thorough

You have access to various tools depending on the task.""",

    AgentType.CODER: """You are an expert software engineer.

Your responsibilities:
- Write clean, maintainable code
- Follow best practices (SOLID, DRY, KISS)
- Write tests for your code
- Document complex logic
- Consider performance and scalability

Tools available:
- file_read, file_write, file_edit, file_glob, file_search
- bash, git, python_exec, linter, run_tests

Code quality standards:
- Use type hints
- Add docstrings to functions
- Handle errors gracefully
- Write self-documenting code""",

    AgentType.DESIGNER: """You are an expert UI/UX designer and frontend developer.

Your responsibilities:
- Create beautiful, functional interfaces
- Follow design best practices
- Ensure accessibility (WCAG)
- Make designs responsive
- Use modern CSS and component libraries

Tools available:
- file_read, file_write, file_edit, file_glob
- bash (for running dev servers)

Design standards:
- Use Tailwind CSS or modern CSS
- Follow responsive design principles
- Ensure color contrast accessibility
- Mobile-first approach""",

    AgentType.RESEARCHER: """You are an expert researcher.

Your responsibilities:
- Find accurate, relevant information
- Cite sources for claims
- Synthesize findings clearly
- Present data objectively
- Update knowledge as new info emerges

Tools available:
- web_search, web_scrape, http_request
- file_write (for reports)

Research standards:
- Verify information from multiple sources
- Note confidence levels
- Include contrary evidence
- Make conclusions actionable""",

    AgentType.MARKETER: """You are an expert marketer.

Your responsibilities:
- Create compelling campaigns
- Know your audience deeply
- Test and iterate
- Track metrics rigorously
- Build brand consistency

Tools available:
- web_search (for competitive research)
- file_write (for content)
- social media tools

Marketing standards:
- Data-driven decisions
- Clear CTAs
- Consistent messaging
- Multi-channel approach""",

    AgentType.WRITER: """You are an expert content writer.

Your responsibilities:
- Write clear, engaging content
- Match brand voice
- SEO optimize where appropriate
- Edit ruthlessly
- Meet deadlines

Tools available:
- file_read, file_write, file_edit
- web_search (for research)

Writing standards:
- Active voice
- Short paragraphs
- Strong headlines
- Include examples""",

    AgentType.DATA: """You are an expert data analyst.

Your responsibilities:
- Clean and prepare data
- Generate insights
- Create visualizations
- Present findings clearly
- Build data pipelines

Tools available:
- file_read, file_write, python_exec
- bash (for data processing)

Analysis standards:
- Reproducible methods
- Clear data lineage
- Statistical rigor
- Actionable insights""",

    AgentType.DEVOPS: """You are an expert DevOps engineer.

Your responsibilities:
- Automate everything
- Ensure reliability
- Optimize performance
- Implement CI/CD
- Monitor and alert

Tools available:
- bash, git, docker, kubernetes tools
- file_read, file_write

DevOps standards:
- Infrastructure as code
- 12-factor app principles
- Monitoring everything
- Fast feedback loops""",
}


# ===========================================
# WORKER AGENT
# ===========================================

class WorkerAgent(BaseAgent):
    """
    Worker agent with specialized tools and prompts.
    
    Each worker type has specific tools and expertise.
    """
    
    # Tool access by agent type
    TOOL_ACCESS = {
        AgentType.CODER: ["file_read", "file_write", "file_edit", "file_glob", "file_search",
                         "bash", "git", "python_exec", "linter", "run_tests"],
        AgentType.DESIGNER: ["file_read", "file_write", "file_edit", "file_glob", "bash"],
        AgentType.RESEARCHER: ["web_search", "web_scrape", "http_request", "file_write"],
        AgentType.MARKETER: ["web_search", "web_scrape", "file_write", "file_glob"],
        AgentType.WRITER: ["file_read", "file_write", "file_edit", "file_glob", "web_search"],
        AgentType.DATA: ["file_read", "file_write", "python_exec", "bash"],
        AgentType.DEVOPS: ["bash", "git", "file_read", "file_write", "docker", "linter"],
        AgentType.GENERAL: [],  # All tools
    }
    
    def __init__(
        self,
        name: str,
        agent_type: AgentType,
        workspace: Optional[str] = None,
        memory: Optional[Any] = None,
        ai_provider: Optional[Any] = None
    ):
        # Get tools for this worker type
        tools = self.TOOL_ACCESS.get(agent_type, [])
        
        # Get system prompt
        prompt = WORKER_PROMPTS.get(agent_type, WORKER_PROMPTS[AgentType.GENERAL])
        
        super().__init__(
            agent_id=f"{agent_type.value}_{name.lower().replace(' ', '_')}",
            name=name,
            agent_type=agent_type,
            tools=tools,
            system_prompt=prompt,
            memory=memory,
            ai_provider=ai_provider
        )
        
        self.workspace = Path(workspace) if workspace else Path(f"./workspace/{agent_type.value}")
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        self.task_history: List[Dict] = []
    
    # ===========================================
    # TASK EXECUTION
    # ===========================================
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task.
        
        Args:
            task: Task definition with title, description, type
        
        Returns:
            Task result
        """
        self.state.status = "working"
        self.state.current_task = task.get("title")
        
        task_type = task.get("type", "general")
        
        try:
            # Execute based on task type
            if task_type == "coding":
                result = await self._execute_coding_task(task)
            elif task_type == "design":
                result = await self._execute_design_task(task)
            elif task_type == "research":
                result = await self._execute_research_task(task)
            elif task_type == "writing":
                result = await self._execute_writing_task(task)
            elif task_type == "data":
                result = await self._execute_data_task(task)
            elif task_type == "devops":
                result = await self._execute_devops_task(task)
            else:
                result = await self._execute_general_task(task)
            
            # Record in history
            self.task_history.append({
                "task": task,
                "result": result,
                "timestamp": datetime.now().isoformat(),
                "success": result.get("success", True)
            })
            
            # Learn from experience
            self.learn(
                f"Completed {task_type} task: {task.get('title')}",
                outcome="success" if result.get("success", True) else "failure"
            )
            
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "task_id": task.get("id")
            }
            
            self.task_history.append({
                "task": task,
                "result": error_result,
                "timestamp": datetime.now().isoformat(),
                "success": False
            })
            
            self.learn(f"Failed {task_type} task: {task.get('title')}", outcome="failure")
            
            return error_result
            
        finally:
            self.state.status = "idle"
            self.state.current_task = None
    
    async def _execute_coding_task(self, task: Dict) -> Dict:
        """Execute a coding task."""
        # Use AI to plan and execute
        prompt = f"""Write code for this task: {task.get('title')}
Description: {task.get('description', 'No description')}

Write clean, well-documented code. Create the file in {self.workspace}."""
        
        code_plan = await self.think(prompt)
        
        # For now, return the plan
        return {
            "success": True,
            "task_id": task.get("id"),
            "plan": code_plan,
            "workspace": str(self.workspace),
            "message": "Code task planned. Use tools to implement."
        }
    
    async def _execute_design_task(self, task: Dict) -> Dict:
        """Execute a design task."""
        prompt = f"""Design this: {task.get('title')}
Description: {task.get('description', 'No description')}

Create a beautiful, accessible, responsive design."""
        
        design_plan = await self.think(prompt)
        
        return {
            "success": True,
            "task_id": task.get("id"),
            "plan": design_plan,
            "workspace": str(self.workspace)
        }
    
    async def _execute_research_task(self, task: Dict) -> Dict:
        """Execute a research task."""
        query = task.get("description", task.get("title", ""))
        
        # Use web search tool
        search_result = await self.execute_tool("web_search", query=query)
        
        if search_result.success:
            return {
                "success": True,
                "task_id": task.get("id"),
                "results": search_result.data,
                "query": query
            }
        
        return {
            "success": False,
            "task_id": task.get("id"),
            "error": "Search failed"
        }
    
    async def _execute_writing_task(self, task: Dict) -> Dict:
        """Execute a writing task."""
        prompt = f"""Write content for: {task.get('title')}
Description: {task.get('description', 'No description')}

Write clear, engaging content."""
        
        content = await self.think(prompt)
        
        # Save to file
        filename = self.workspace / f"{task.get('id', 'output')}.md"
        write_result = await self.execute_tool(
            "file_write",
            path=str(filename),
            content=content
        )
        
        return {
            "success": True,
            "task_id": task.get("id"),
            "content": content,
            "saved_to": str(filename)
        }
    
    async def _execute_data_task(self, task: Dict) -> Dict:
        """Execute a data task."""
        prompt = f"""Analyze this data: {task.get('title')}
Description: {task.get('description', 'No description')}

Provide insights and recommendations."""
        
        analysis = await self.think(prompt)
        
        return {
            "success": True,
            "task_id": task.get("id"),
            "analysis": analysis
        }
    
    async def _execute_devops_task(self, task: Dict) -> Dict:
        """Execute a DevOps task."""
        prompt = f"""Plan DevOps setup for: {task.get('title')}
Description: {task.get('description', 'No description')}

Consider CI/CD, deployment, monitoring."""
        
        plan = await self.think(prompt)
        
        return {
            "success": True,
            "task_id": task.get("id"),
            "plan": plan
        }
    
    async def _execute_general_task(self, task: Dict) -> Dict:
        """Execute a general task."""
        prompt = f"""Complete this task: {task.get('title')}
Description: {task.get('description', 'No description')}"""
        
        result = await self.think(prompt)
        
        return {
            "success": True,
            "task_id": task.get("id"),
            "result": result
        }
    
    # ===========================================
    # SPECIALIZATIONS
    # ===========================================
    
    def get_specialization(self) -> str:
        """Get worker specialization."""
        return self.type.value
    
    def get_capabilities(self) -> List[str]:
        """Get worker capabilities (tools + expertise)."""
        return self.list_available_tools()
    
    def get_task_count(self) -> int:
        """Get number of tasks completed."""
        return len(self.task_history)
    
    def get_success_rate(self) -> float:
        """Get task success rate."""
        if not self.task_history:
            return 0.0
        
        successful = sum(1 for t in self.task_history if t.get("success"))
        return successful / len(self.task_history)


# ===========================================
# SPECIALIZED WORKERS
# ===========================================

class CoderAgent(WorkerAgent):
    """Specialized coder agent."""
    
    def __init__(self, name: str = "Coder", **kwargs):
        super().__init__(name, AgentType.CODER, **kwargs)


class DesignerAgent(WorkerAgent):
    """Specialized designer agent."""
    
    def __init__(self, name: str = "Designer", **kwargs):
        super().__init__(name, AgentType.DESIGNER, **kwargs)


class ResearcherAgent(WorkerAgent):
    """Specialized researcher agent."""
    
    def __init__(self, name: str = "Researcher", **kwargs):
        super().__init__(name, AgentType.RESEARCHER, **kwargs)


class MarketerAgent(WorkerAgent):
    """Specialized marketer agent."""
    
    def __init__(self, name: str = "Marketer", **kwargs):
        super().__init__(name, AgentType.MARKETER, **kwargs)


class WriterAgent(WorkerAgent):
    """Specialized writer agent."""
    
    def __init__(self, name: str = "Writer", **kwargs):
        super().__init__(name, AgentType.WRITER, **kwargs)


class DataAgent(WorkerAgent):
    """Specialized data analyst agent."""
    
    def __init__(self, name: str = "Data Analyst", **kwargs):
        super().__init__(name, AgentType.DATA, **kwargs)


class DevOpsAgent(WorkerAgent):
    """Specialized DevOps agent."""
    
    def __init__(self, name: str = "DevOps", **kwargs):
        super().__init__(name, AgentType.DEVOPS, **kwargs)
