"""
NanoCorp v3.0 - Unified Tool Interface

Every tool implements the same protocol.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import inspect

from pydantic import BaseModel, Field


# ===========================================
# TOOL CATEGORIES
# ===========================================

class ToolCategory(Enum):
    """Tool categories for organization."""
    CODE = "code"          # Code execution, testing
    FILE = "file"          # File operations
    WEB = "web"           # Web requests, scraping
    DATA = "data"          # Database, CSV, JSON
    COMM = "comm"          # Email, Slack, etc
    SYSTEM = "system"      # OS, process management
    AI = "ai"              # AI model interactions
    CUSTOM = "custom"      # Custom tools


# ===========================================
# TOOL SCHEMAS
# ===========================================

class ToolInput(BaseModel):
    """Base input for tools."""
    pass


class ToolOutput(BaseModel):
    """Base output for tools."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# ===========================================
# TOOL DEFINITION
# ===========================================

@dataclass
class ToolDefinition:
    """
    Tool metadata and schema.
    
    All tools have these properties.
    """
    name: str
    description: str
    category: ToolCategory
    
    # Parameters schema
    parameters: Dict[str, Any] = field(default_factory=dict)
    required: List[str] = field(default_factory=list)
    
    # Return schema
    returns: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    examples: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    deprecated: bool = False
    deprecation_message: Optional[str] = None
    
    def to_schema(self) -> Dict[str, Any]:
        """Convert to JSON schema for LLM consumption."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": self.parameters,
                "required": self.required
            }
        }


# ===========================================
# BASE TOOL
# ===========================================

class BaseTool(ABC):
    """
    Abstract base class for all tools.
    
    All NanoCorp tools inherit from this.
    """
    
    def __init__(self):
        self._definition: Optional[ToolDefinition] = None
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass
    
    @property
    def category(self) -> ToolCategory:
        """Tool category."""
        return ToolCategory.CUSTOM
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolOutput:
        """
        Execute the tool.
        
        Returns ToolOutput with success/data/error.
        """
        pass
    
    @property
    def definition(self) -> ToolDefinition:
        """Get tool definition for schema generation."""
        if self._definition is None:
            self._definition = self._build_definition()
        return self._definition
    
    def _build_definition(self) -> ToolDefinition:
        """Build tool definition from execute signature."""
        sig = inspect.signature(self.execute)
        params = sig.parameters
        
        parameters = {}
        required = []
        
        for name, param in params.items():
            if name == "self":
                continue
            
            # Get type
            if param.annotation != inspect.Parameter.empty:
                try:
                    type_str = param.annotation.__name__
                except AttributeError:
                    type_str = "string"
            else:
                type_str = "string"
            
            # Get description
            if hasattr(param.default, 'description'):
                desc = param.default.description
            elif param.default != inspect.Parameter.empty and isinstance(param.default, str):
                desc = f"Parameter {name} (default: {param.default})"
            else:
                desc = f"Parameter {name}"
            
            parameters[name] = {
                "type": type_str,
                "description": desc
            }
            
            if param.default == inspect.Parameter.empty:
                required.append(name)
        
        return ToolDefinition(
            name=self.name,
            description=self.description,
            category=self.category,
            parameters=parameters,
            required=required
        )
    
    def validate_input(self, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate input parameters."""
        for req in self.definition.required:
            if req not in kwargs:
                return False, f"Missing required parameter: {req}"
        return True, None
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"


# ===========================================
# TOOL RESULT HELPERS
# ===========================================

def success_result(data: Any = None, **metadata) -> ToolOutput:
    """Create a success result."""
    return ToolOutput(success=True, data=data, metadata=metadata)


def error_result(error: str, data: Any = None) -> ToolOutput:
    """Create an error result."""
    return ToolOutput(success=False, error=error, data=data)


# ===========================================
# TOOL DECORATORS
# ===========================================

def tool(
    name: str,
    description: str,
    category: ToolCategory = ToolCategory.CUSTOM,
    **kwargs
):
    """
    Decorator to register a tool.
    
    Usage:
        @tool(name="my_tool", description="Does something")
        class MyTool(BaseTool):
            ...
    """
    def decorator(cls):
        cls._tool_name = name
        cls._tool_description = description
        cls._tool_category = category
        cls._tool_kwargs = kwargs
        return cls
    return decorator


def register_tool(tool_class: type):
    """Register a tool class in the global registry."""
    from .registry import get_registry
    registry = get_registry()
    instance = tool_class()
    registry.register(instance)
    return tool_class


# ===========================================
# COMPOSITE TOOLS
# ===========================================

class ToolChain:
    """
    Chain tools together sequentially.
    
    Output of one tool becomes input of next.
    """
    
    def __init__(self, tools: List[BaseTool]):
        self.tools = tools
    
    def execute(self, initial_input: Dict[str, Any]) -> ToolOutput:
        """Execute all tools in sequence."""
        current_input = initial_input
        
        for tool in self.tools:
            result = tool.execute(**current_input)
            
            if not result.success:
                return result
            
            # Pass output to next tool
            if isinstance(result.data, dict):
                current_input.update(result.data)
            elif result.data is not None:
                current_input["result"] = result.data
        
        return success_result(current_input)


class ToolParallel:
    """
    Execute tools in parallel.
    
    All tools run simultaneously.
    """
    
    def __init__(self, tools: List[BaseTool]):
        self.tools = tools
    
    def execute(self, input: Dict[str, Any]) -> Dict[str, ToolOutput]:
        """Execute all tools in parallel."""
        import concurrent.futures
        
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(tool.execute, **input): tool
                for tool in self.tools
            }
            
            for future in concurrent.futures.as_completed(futures):
                tool = futures[future]
                try:
                    results[tool.name] = future.result()
                except Exception as e:
                    results[tool.name] = error_result(str(e))
        
        return results


# ===========================================
# PARAMETER HELPERS
# ===========================================

@dataclass
class Param:
    """Parameter with metadata for schema generation."""
    name: str
    type: str = "string"
    description: str = ""
    default: Any = None
    required: bool = False
    enum: List[Any] = None
    min_items: int = None
    max_items: int = None
    
    def __post_init__(self):
        if self.enum:
            self.required = True


def string_param(name: str, description: str = "", **kwargs) -> Param:
    """Create a string parameter."""
    return Param(name=name, type="string", description=description, **kwargs)


def integer_param(name: str, description: str = "", **kwargs) -> Param:
    """Create an integer parameter."""
    return Param(name=name, type="integer", description=description, **kwargs)


def boolean_param(name: str, description: str = "", **kwargs) -> Param:
    """Create a boolean parameter."""
    return Param(name=name, type="boolean", description=description, **kwargs)


def array_param(name: str, description: str = "", **kwargs) -> Param:
    """Create an array parameter."""
    return Param(name=name, type="array", description=description, **kwargs)


def object_param(name: str, description: str = "", **kwargs) -> Param:
    """Create an object parameter."""
    return Param(name=name, type="object", description=description, **kwargs)
