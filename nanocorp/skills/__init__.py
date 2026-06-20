"""
NanoCorp v3.0 - Skills System

Reusable skill bundles inspired by OpenHands.
Skills bundle tools, prompts, and workflows together.
"""
from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import importlib.util

from pydantic import BaseModel


# ===========================================
# SKILL DEFINITION
# ===========================================

class SkillDefinition(BaseModel):
    """Skill metadata."""
    name: str
    description: str
    version: str = "1.0.0"
    author: Optional[str] = None
    tags: List[str] = []
    requires: Dict[str, str] = {}  # Required config/environment


@dataclass
class SkillResult:
    """Result from skill execution."""
    success: bool
    output: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# ===========================================
# BASE SKILL
# ===========================================

class BaseSkill(ABC):
    """
    Base class for all skills.
    
    Skills bundle tools, prompts, and workflows.
    """
    
    definition: SkillDefinition
    
    def __init__(self):
        self._initialized = False
        self._tools = []
        self._config = {}
    
    @property
    def name(self) -> str:
        return self.definition.name
    
    @property
    def description(self) -> str:
        return self.definition.description
    
    def configure(self, **kwargs):
        """Configure the skill."""
        self._config.update(kwargs)
    
    def requires_config(self) -> Dict[str, str]:
        """Return required configuration."""
        return self.definition.requires
    
    def is_configured(self) -> bool:
        """Check if skill has required config."""
        for key in self.requires_config():
            if key not in self._config and key not in os.environ:
                return False
        return True
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> SkillResult:
        """
        Execute the skill.
        
        Args:
            context: Execution context with inputs
        
        Returns:
            SkillResult with output or error
        """
        pass
    
    async def initialize(self):
        """Initialize skill resources."""
        self._initialized = True
    
    async def cleanup(self):
        """Cleanup skill resources."""
        pass


# ===========================================
# SKILL REGISTRY
# ===========================================

class SkillRegistry:
    """
    Registry of available skills.
    
    Manages skill loading and execution.
    """
    
    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}
        self._paths: List[Path] = []
    
    def add_search_path(self, path: str):
        """Add a directory to search for skills."""
        self._paths.append(Path(path))
    
    def register(self, skill: BaseSkill):
        """Register a skill."""
        self._skills[skill.name] = skill
    
    def unregister(self, name: str) -> bool:
        """Unregister a skill."""
        if name in self._skills:
            del self._skills[name]
            return True
        return False
    
    def get(self, name: str) -> Optional[BaseSkill]:
        """Get a skill by name."""
        return self._skills.get(name)
    
    def list_all(self) -> List[str]:
        """List all registered skill names."""
        return list(self._skills.keys())
    
    def list_by_tag(self, tag: str) -> List[str]:
        """List skills with a specific tag."""
        return [
            name for name, skill in self._skills.items()
            if tag in skill.definition.tags
        ]
    
    def discover(self):
        """Discover skills from search paths."""
        for path in self._paths:
            if not path.exists():
                continue
            
            for skill_file in path.glob("*.py"):
                self._load_skill_file(skill_file)
    
    def _load_skill_file(self, path: Path):
        """Load a skill from a Python file."""
        try:
            spec = importlib.util.spec_from_file_location(path.stem, path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Look for Skill subclasses
                for name in dir(module):
                    obj = getattr(module, name)
                    if isinstance(obj, type) and issubclass(obj, BaseSkill) and obj != BaseSkill:
                        skill = obj()
                        self.register(skill)
        except Exception as e:
            print(f"Failed to load skill from {path}: {e}")


# ===========================================
# SKILL EXECUTOR
# ===========================================

class SkillExecutor:
    """
    Execute skills with context management.
    """
    
    def __init__(self, registry: SkillRegistry):
        self.registry = registry
    
    async def execute(
        self,
        skill_name: str,
        context: Dict[str, Any]
    ) -> SkillResult:
        """
        Execute a skill by name.
        
        Args:
            skill_name: Name of skill to execute
            context: Execution context
        
        Returns:
            SkillResult
        """
        skill = self.registry.get(skill_name)
        
        if not skill:
            return SkillResult(
                success=False,
                error=f"Skill not found: {skill_name}"
            )
        
        if not skill.is_configured():
            missing = [
                k for k in skill.requires_config()
                if k not in skill._config and k not in os.environ
            ]
            return SkillResult(
                success=False,
                error=f"Skill not configured. Missing: {missing}"
            )
        
        try:
            if not skill._initialized:
                await skill.initialize()
            
            result = await skill.execute(context)
            return result
            
        except Exception as e:
            return SkillResult(
                success=False,
                error=str(e)
            )
        finally:
            await skill.cleanup()


# ===========================================
# BUILT-IN SKILLS
# ===========================================

class TavilyResearchSkill(BaseSkill):
    """
    Web research skill using Tavily API.
    
    Provides comprehensive web search and content extraction.
    """
    
    def __init__(self):
        super().__init__()
        self.definition = SkillDefinition(
            name="tavily",
            description="Web research with comprehensive search and extraction",
            tags=["research", "web", "search"],
            requires={"TAVILY_API_KEY": "Tavily API key"}
        )
    
    async def execute(self, context: Dict[str, Any]) -> SkillResult:
        """
        Execute web research.
        
        Context:
            query: Search query
            max_results: Max results (default 5)
            search_depth: basic or advanced
        """
        try:
            import httpx
            
            api_key = self._config.get("TAVILY_API_KEY") or os.getenv("TAVILY_API_KEY")
            
            response = httpx.post(
                "https://api.tavily.com/search",
                json={
                    "query": context.get("query", ""),
                    "search_depth": context.get("search_depth", "basic"),
                    "max_results": context.get("max_results", 5),
                    "api_key": api_key
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            return SkillResult(
                success=True,
                output={
                    "query": data.get("query"),
                    "results": data.get("results", []),
                    "answer": data.get("answer"),
                    "response_time": data.get("response_time")
                }
            )
            
        except Exception as e:
            return SkillResult(success=False, error=str(e))


class GitHubSkill(BaseSkill):
    """
    GitHub integration skill.
    
    Create repos, manage issues, PRs, and more.
    """
    
    def __init__(self):
        super().__init__()
        self.definition = SkillDefinition(
            name="github",
            description="GitHub operations - repos, issues, PRs, and more",
            tags=["github", "git", "version-control"],
            requires={"GITHUB_TOKEN": "GitHub personal access token"}
        )
    
    async def execute(self, context: Dict[str, Any]) -> SkillResult:
        """
        Execute GitHub operation.
        
        Context:
            operation: create_repo, create_issue, create_pr, etc.
            params: Operation-specific parameters
        """
        try:
            import httpx
            
            token = self._config.get("GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN")
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"
            }
            
            base_url = "https://api.github.com"
            operation = context.get("operation", "")
            
            if operation == "create_repo":
                response = httpx.post(
                    f"{base_url}/user/repos",
                    json=context.get("params", {}),
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                
                return SkillResult(
                    success=True,
                    output={
                        "name": result.get("name"),
                        "url": result.get("html_url"),
                        "clone_url": result.get("clone_url")
                    }
                )
            
            elif operation == "create_issue":
                response = httpx.post(
                    f"{base_url}/repos/{context['params']['owner']}/{context['params']['repo']}/issues",
                    json=context.get("params", {}),
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                
                return SkillResult(
                    success=True,
                    output={
                        "number": result.get("number"),
                        "title": result.get("title"),
                        "url": result.get("html_url")
                    }
                )
            
            return SkillResult(success=False, error=f"Unknown operation: {operation}")
            
        except Exception as e:
            return SkillResult(success=False, error=str(e))


class SlackSkill(BaseSkill):
    """
    Slack messaging skill.
    
    Send messages to Slack channels.
    """
    
    def __init__(self):
        super().__init__()
        self.definition = SkillDefinition(
            name="slack",
            description="Send messages to Slack channels",
            tags=["slack", "messaging", "communication"],
            requires={"SLACK_BOT_TOKEN": "Slack bot token"}
        )
    
    async def execute(self, context: Dict[str, Any]) -> SkillResult:
        """
        Send Slack message.
        
        Context:
            channel: Channel name or ID
            text: Message text
            blocks: Optional Slack blocks
        """
        try:
            import httpx
            
            token = self._config.get("SLACK_BOT_TOKEN") or os.getenv("SLACK_BOT_TOKEN")
            
            response = httpx.post(
                "https://slack.com/api/chat.postMessage",
                json={
                    "channel": context.get("channel"),
                    "text": context.get("text"),
                    "blocks": context.get("blocks")
                },
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            data = response.json()
            
            if not data.get("ok"):
                return SkillResult(success=False, error=data.get("error"))
            
            return SkillResult(
                success=True,
                output={
                    "ts": data.get("ts"),
                    "channel": data.get("channel")
                }
            )
            
        except Exception as e:
            return SkillResult(success=False, error=str(e))


class LinearSkill(BaseSkill):
    """
    Linear issue tracking skill.
    
    Create and manage Linear issues.
    """
    
    def __init__(self):
        super().__init__()
        self.definition = SkillDefinition(
            name="linear",
            description="Linear issue tracking - create and manage issues",
            tags=["linear", "project-management", "issues"],
            requires={"LINEAR_API_KEY": "Linear API key"}
        )
    
    async def execute(self, context: Dict[str, Any]) -> SkillResult:
        """
        Execute Linear operation.
        
        Context:
            operation: create_issue, list_issues, etc.
            params: Operation parameters
        """
        try:
            import httpx
            
            api_key = self._config.get("LINEAR_API_KEY") or os.getenv("LINEAR_API_KEY")
            
            operation = context.get("operation", "")
            
            if operation == "create_issue":
                query = """
                mutation CreateIssue($title: String!, $description: String) {
                    issueCreate(input: {title: $title, description: $description}) {
                        success
                        issue {
                            id
                            identifier
                            title
                            url
                        }
                    }
                }
                """
                
                response = httpx.post(
                    "https://api.linear.app/graphql",
                    json={
                        "query": query,
                        "variables": {
                            "title": context["params"]["title"],
                            "description": context["params"].get("description")
                        }
                    },
                    headers={
                        "Authorization": api_key,
                        "Content-Type": "application/json"
                    },
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("errors"):
                    return SkillResult(success=False, error=str(data["errors"]))
                
                result = data["data"]["issueCreate"]
                return SkillResult(
                    success=result["success"],
                    output=result["issue"]
                )
            
            return SkillResult(success=False, error=f"Unknown operation: {operation}")
            
        except Exception as e:
            return SkillResult(success=False, error=str(e))


# ===========================================
# GLOBAL INSTANCES
# ===========================================

_registry: Optional[SkillRegistry] = None

def get_skill_registry() -> SkillRegistry:
    """Get the global skill registry."""
    global _registry
    if _registry is None:
        _registry = SkillRegistry()
        
        # Register built-in skills
        _registry.register(TavilyResearchSkill())
        _registry.register(GitHubSkill())
        _registry.register(SlackSkill())
        _registry.register(LinearSkill())
    
    return _registry
