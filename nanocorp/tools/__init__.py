"""
NanoCorp v3.0 - Tools Module

Unified tool interface with filesystem, code, web, and more tools.
"""
from .base import (
    BaseTool,
    ToolDefinition,
    ToolOutput,
    ToolCategory,
    ToolChain,
    ToolParallel,
    success_result,
    error_result,
    register_tool,
)

from .registry import (
    ToolRegistry,
    get_registry,
    register,
    get_tool,
    list_tools,
    get_tool_schemas,
    register_all_tools,
)

from .filesystem import (
    FileReadTool,
    FileWriteTool,
    FileEditTool,
    FileGlobTool,
    FileSearchTool,
    FileInfoTool,
    FileListTool,
)

from .code import (
    BashTool,
    GitTool,
    PythonExecTool,
    LinterTool,
    TestRunnerTool,
)

from .web import (
    HTTPRequestTool,
    WebScraperTool,
    WebSearchTool,
)

__all__ = [
    # Base
    "BaseTool",
    "ToolDefinition", 
    "ToolOutput",
    "ToolCategory",
    "ToolChain",
    "ToolParallel",
    "success_result",
    "error_result",
    "register_tool",
    # Registry
    "ToolRegistry",
    "get_registry",
    "register",
    "get_tool",
    "list_tools",
    "get_tool_schemas",
    "register_all_tools",
    # Filesystem
    "FileReadTool",
    "FileWriteTool",
    "FileEditTool",
    "FileGlobTool",
    "FileSearchTool",
    "FileInfoTool",
    "FileListTool",
    # Code
    "BashTool",
    "GitTool",
    "PythonExecTool",
    "LinterTool",
    "TestRunnerTool",
    # Web
    "HTTPRequestTool",
    "WebScraperTool",
    "WebSearchTool",
]
