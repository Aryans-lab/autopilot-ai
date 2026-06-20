"""
NanoCorp v3.0 - Tool Registry

Central registry of all available tools.
"""
from __future__ import annotations

from typing import Dict, List, Type, Optional, Any
from logging import getLogger

from .base import BaseTool, ToolDefinition, ToolCategory

logger = getLogger("nanocorp.tools")


class ToolRegistry:
    """
    Central registry of all NanoCorp tools.
    
    Singleton pattern for global tool access.
    """
    
    _instance: Optional[ToolRegistry] = None
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._definitions: Dict[str, ToolDefinition] = {}
        self._categories: Dict[ToolCategory, List[str]] = {}
    
    @classmethod
    def get_instance(cls) -> ToolRegistry:
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = ToolRegistry()
        return cls._instance
    
    def register(self, tool: BaseTool) -> None:
        """
        Register a tool.
        
        Args:
            tool: Tool instance to register
        """
        name = tool.name
        
        if name in self._tools:
            logger.warning(f"Tool already registered: {name}")
            return
        
        self._tools[name] = tool
        self._definitions[name] = tool.definition
        
        # Add to category
        category = tool.category
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(name)
        
        logger.debug(f"Registered tool: {name} ({category.value})")
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a tool.
        
        Returns:
            True if tool was unregistered
        """
        if name not in self._tools:
            return False
        
        tool = self._tools[name]
        category = tool.category
        
        del self._tools[name]
        del self._definitions[name]
        
        if category in self._categories:
            self._categories[category].remove(name)
        
        logger.debug(f"Unregistered tool: {name}")
        return True
    
    def get(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_all(self) -> List[str]:
        """List all tool names."""
        return list(self._tools.keys())
    
    def list_by_category(self, category: ToolCategory) -> List[str]:
        """List tools in a category."""
        return self._categories.get(category, [])
    
    def get_definitions(self) -> List[ToolDefinition]:
        """Get all tool definitions for LLM consumption."""
        return list(self._definitions.values())
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get full tool schema for agents.
        
        Returns a list of tool definitions in a format
        that LLMs can understand.
        """
        return [d.to_schema() for d in self._definitions.values()]
    
    def clear(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()
        self._definitions.clear()
        self._categories.clear()


# Convenience functions
def get_registry() -> ToolRegistry:
    """Get the global tool registry."""
    return ToolRegistry.get_instance()


def register(tool: BaseTool) -> None:
    """Register a tool."""
    get_registry().register(tool)


def get_tool(name: str) -> Optional[BaseTool]:
    """Get a tool by name."""
    return get_registry().get(name)


def list_tools() -> List[str]:
    """List all tools."""
    return get_registry().list_all()


def get_tools_by_category(category: ToolCategory) -> List[str]:
    """List tools in category."""
    return get_registry().list_by_category(category)


def get_tool_schemas() -> List[Dict[str, Any]]:
    """Get tool schemas for LLM."""
    return get_registry().get_schema()


# ===========================================
# AUTO-REGISTRATION
# ===========================================

def register_all_tools():
    """Auto-register all built-in tools."""
    from .filesystem import (
        FileReadTool, FileWriteTool, FileEditTool,
        FileGlobTool, FileSearchTool, FileInfoTool, FileListTool
    )
    from .code import BashTool, GitTool, PythonExecTool, LinterTool, TestRunnerTool
    from .web import HTTPRequestTool, WebScraperTool, WebSearchTool
    
    tools = [
        # File tools
        FileReadTool(),
        FileWriteTool(),
        FileEditTool(),
        FileGlobTool(),
        FileSearchTool(),
        FileInfoTool(),
        FileListTool(),
        # Code tools
        BashTool(),
        GitTool(),
        PythonExecTool(),
        LinterTool(),
        TestRunnerTool(),
        # Web tools
        HTTPRequestTool(),
        WebScraperTool(),
        WebSearchTool(),
    ]
    
    registry = get_registry()
    for tool in tools:
        registry.register(tool)
    
    logger.info(f"Registered {len(tools)} built-in tools")
