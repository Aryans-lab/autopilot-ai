"""
NanoCorp v3.0 - MCP (Model Context Protocol) Client

Connect to any MCP server following Anthropic's MCP specification.
"""
from __future__ import annotations

import json
import asyncio
import subprocess
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger("nanocorp.mcp")


class MCPTransport(Enum):
    """MCP transport types."""
    STDIO = "stdio"
    HTTP = "http"
    SSE = "sse"


@dataclass
class MCPTool:
    """MCP tool definition."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }


@dataclass
class MCPToolResult:
    """Result from an MCP tool call."""
    success: bool
    content: Any
    error: Optional[str] = None


class MCPClient:
    """
    MCP Client for connecting to MCP servers.
    
    Implements JSON-RPC 2.0 over stdio (primary) or HTTP+SSE.
    """
    
    def __init__(
        self,
        server_command: Optional[List[str]] = None,
        server_url: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: int = 30
    ):
        """
        Initialize MCP client.
        
        Args:
            server_command: Command to start MCP server (for stdio)
            server_url: URL for HTTP server (alternative to command)
            env: Environment variables for server
            timeout: Request timeout in seconds
        """
        self.server_command = server_command
        self.server_url = server_url
        self.env = env or {}
        self.timeout = timeout
        
        self._process: Optional[subprocess.Popen] = None
        self._tools: Dict[str, MCPTool] = {}
        self._request_id = 0
        self._pending_requests: Dict[int, asyncio.Future] = {}
        
        # If command provided, start server
        if server_command:
            self._start_server()
    
    def _start_server(self):
        """Start the MCP server process."""
        try:
            self._process = subprocess.Popen(
                self.server_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**subprocess.os.environ, **self.env}
            )
            logger.info(f"MCP server started: {' '.join(self.server_command)}")
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            raise
    
    def _send_request(self, method: str, params: Optional[Dict] = None) -> Dict:
        """Send JSON-RPC request and get response."""
        if not self._process:
            raise RuntimeError("MCP server not running")
        
        self._request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params or {}
        }
        
        # Send request
        request_json = json.dumps(request) + "\n"
        self._process.stdin.write(request_json.encode())
        self._process.stdin.flush()
        
        # Read response
        response_line = self._process.stdout.readline()
        if not response_line:
            stderr = self._process.stderr.read().decode()
            raise RuntimeError(f"MCP server error: {stderr}")
        
        response = json.loads(response_line)
        
        if "error" in response:
            raise RuntimeError(f"MCP error: {response['error']}")
        
        return response.get("result", {})
    
    async def initialize(self) -> Dict:
        """
        Initialize connection with MCP server.
        
        Returns server capabilities.
        """
        result = self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "nanocorp",
                "version": "3.0.0"
            }
        })
        
        # Initialize tools
        self._discover_tools()
        
        return result
    
    def _discover_tools(self):
        """Discover available tools from server."""
        try:
            response = self._send_request("tools/list")
            tools = response.get("tools", [])
            
            for tool in tools:
                self._tools[tool["name"]] = MCPTool(
                    name=tool["name"],
                    description=tool.get("description", ""),
                    input_schema=tool.get("inputSchema", {})
                )
            
            logger.info(f"Discovered {len(self._tools)} MCP tools")
        except Exception as e:
            logger.warning(f"Failed to discover tools: {e}")
    
    def list_tools(self) -> List[MCPTool]:
        """List all available MCP tools."""
        return list(self._tools.values())
    
    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get a specific tool by name."""
        return self._tools.get(name)
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        """
        Call an MCP tool with arguments.
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            MCPToolResult with success/content or error
        """
        try:
            if name not in self._tools:
                return MCPToolResult(
                    success=False,
                    content=None,
                    error=f"Unknown tool: {name}"
                )
            
            response = self._send_request("tools/call", {
                "name": name,
                "arguments": arguments
            })
            
            return MCPToolResult(
                success=True,
                content=response.get("content", [])
            )
            
        except Exception as e:
            logger.error(f"Tool call failed: {name} - {e}")
            return MCPToolResult(
                success=False,
                content=None,
                error=str(e)
            )
    
    def ping(self) -> bool:
        """Ping the MCP server."""
        try:
            self._send_request("ping")
            return True
        except:
            return False
    
    def close(self):
        """Close the MCP client and server."""
        if self._process:
            self._process.terminate()
            self._process.wait(timeout=5)
            self._process = None
            logger.info("MCP server stopped")
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


# ===========================================
# MCP REGISTRY
# ===========================================

class MCPRegistry:
    """
    Registry of MCP servers and their tools.
    
    Manages multiple MCP connections.
    """
    
    def __init__(self):
        self._clients: Dict[str, MCPClient] = {}
        self._tools: Dict[str, MCPTool] = {}  # name -> (client_id, tool)
    
    def add_server(
        self,
        server_id: str,
        command: Optional[List[str]] = None,
        url: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> MCPClient:
        """Add an MCP server."""
        client = MCPClient(
            server_command=command,
            server_url=url,
            env=env
        )
        client.initialize()
        
        self._clients[server_id] = client
        
        # Register tools
        for tool in client.list_tools():
            self._tools[tool.name] = (server_id, tool)
        
        logger.info(f"Added MCP server: {server_id} with {len(client._tools)} tools")
        return client
    
    def get_client(self, server_id: str) -> Optional[MCPClient]:
        """Get a client by server ID."""
        return self._clients.get(server_id)
    
    def list_all_tools(self) -> List[tuple]:
        """List all tools from all servers."""
        return [(server_id, tool) for tool, (server_id, _) in self._tools.items()]
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        """Call a tool by name, routing to correct server."""
        if tool_name not in self._tools:
            return MCPToolResult(
                success=False,
                content=None,
                error=f"Unknown tool: {tool_name}"
            )
        
        server_id, tool = self._tools[tool_name]
        client = self._clients[server_id]
        
        return client.call_tool(tool_name, arguments)
    
    def close_all(self):
        """Close all MCP clients."""
        for client in self._clients.values():
            client.close()
        self._clients.clear()
        self._tools.clear()


# Global registry
_registry: Optional[MCPRegistry] = None

def get_registry() -> MCPRegistry:
    """Get the global MCP registry."""
    global _registry
    if _registry is None:
        _registry = MCPRegistry()
    return _registry
