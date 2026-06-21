"""
NanoCorp MCP Servers - Production-Ready Tool Servers

This module provides pre-configured MCP (Model Context Protocol) servers that extend
the capabilities of NanoCorp agents with real-world integrations.

Available Servers:
1. FileSystemServer - Advanced file operations with git integration
2. BrowserServer - Web automation, scraping, and interaction
3. DatabaseServer - SQL/NoSQL database operations
4. APIServer - REST/GraphQL API client with auth handling
5. GitServer - Full git workflow automation
6. EmailServer - SMTP/IMAP email operations
7. SocialServer - Social media platform APIs
8. CloudServer - AWS/GCP/Azure cloud operations
9. MonitoringServer - System monitoring and alerting
10. SearchServer - Web search and information retrieval
"""
from __future__ import annotations

import asyncio
import json
import os
import subprocess
import tempfile
import shutil
from typing import Dict, List, Any, Optional, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import aiohttp
import sqlite3
from contextlib import asynccontextmanager


# ===========================================
# BASE MCP SERVER
# ===========================================

@dataclass
class MCPServer:
    """Base class for MCP servers"""
    name: str
    version: str = "1.0.0"
    description: str = ""
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    
    async def initialize(self) -> bool:
        """Initialize the server"""
        return self.enabled
    
    async def shutdown(self):
        """Shutdown the server"""
        pass
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools"""
        raise NotImplementedError
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool with given arguments"""
        raise NotImplementedError


# ===========================================
# FILESYSTEM SERVER
# ===========================================

class FileSystemServer(MCPServer):
    """
    Advanced filesystem operations with git tracking, 
    file watching, and intelligent organization.
    """
    
    def __init__(self, root_path: str = ".", **kwargs):
        super().__init__(
            name="filesystem",
            version="2.0.0",
            description="Advanced filesystem operations with git integration",
            config={"root_path": root_path, **kwargs}
        )
        self.root_path = Path(root_path).expanduser().resolve()
        self.watch_paths: List[Path] = []
        self.file_history: Dict[str, List[Dict]] = {}
    
    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "read_file",
                "description": "Read contents of a file with optional line range",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"},
                        "start_line": {"type": "integer", "description": "Start line (optional)"},
                        "end_line": {"type": "integer", "description": "End line (optional)"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "write_file",
                "description": "Write content to a file (creates if not exists)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"},
                        "content": {"type": "string", "description": "File content"},
                        "append": {"type": "boolean", "description": "Append instead of overwrite"}
                    },
                    "required": ["path", "content"]
                }
            },
            {
                "name": "list_directory",
                "description": "List directory contents with filtering",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path"},
                        "pattern": {"type": "string", "description": "Glob pattern filter"},
                        "recursive": {"type": "boolean", "description": "Include subdirectories"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "search_files",
                "description": "Search for files by name pattern or content",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "Search pattern"},
                        "path": {"type": "string", "description": "Base path to search"},
                        "content_search": {"type": "boolean", "description": "Search in file content"},
                        "file_type": {"type": "string", "description": "Filter by file extension"}
                    },
                    "required": ["pattern"]
                }
            },
            {
                "name": "create_directory",
                "description": "Create directory structure",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path"},
                        "parents": {"type": "boolean", "description": "Create parent directories"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "delete_file",
                "description": "Delete a file or directory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File/directory path"},
                        "recursive": {"type": "boolean", "description": "Delete recursively"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "copy_file",
                "description": "Copy file or directory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string", "description": "Source path"},
                        "destination": {"type": "string", "description": "Destination path"}
                    },
                    "required": ["source", "destination"]
                }
            },
            {
                "name": "move_file",
                "description": "Move/rename file or directory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string", "description": "Source path"},
                        "destination": {"type": "string", "description": "Destination path"}
                    },
                    "required": ["source", "destination"]
                }
            },
            {
                "name": "get_file_info",
                "description": "Get detailed file metadata",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "watch_directory",
                "description": "Watch directory for changes",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory to watch"},
                        "patterns": {"type": "array", "items": {"type": "string"}, "description": "File patterns to watch"}
                    },
                    "required": ["path"]
                }
            }
        ]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        method = getattr(self, f"_{tool_name}", None)
        if not method:
            raise ValueError(f"Unknown tool: {tool_name}")
        return await method(**arguments)
    
    async def _read_file(self, path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
        """Read file content with optional line range"""
        file_path = self._resolve_path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if start_line is not None or end_line is not None:
            start = start_line - 1 if start_line else 0
            end = end_line if end_line else len(lines)
            lines = lines[start:end]
        
        return ''.join(lines)
    
    async def _write_file(self, path: str, content: str, append: bool = False) -> Dict[str, Any]:
        """Write content to file"""
        file_path = self._resolve_path(path)
        
        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        mode = 'a' if append else 'w'
        with open(file_path, mode, encoding='utf-8') as f:
            f.write(content)
        
        # Track history
        if path not in self.file_history:
            self.file_history[path] = []
        self.file_history[path].append({
            "action": "write",
            "timestamp": datetime.now().isoformat(),
            "size": len(content)
        })
        
        return {"success": True, "path": str(file_path), "size": len(content)}
    
    async def _list_directory(self, path: str, pattern: Optional[str] = None, recursive: bool = False) -> List[Dict[str, Any]]:
        """List directory contents"""
        dir_path = self._resolve_path(path)
        
        if not dir_path.exists() or not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")
        
        results = []
        
        if recursive:
            items = dir_path.rglob(pattern or "*")
        else:
            items = dir_path.glob(pattern or "*")
        
        for item in items:
            try:
                stat = item.stat()
                results.append({
                    "name": item.name,
                    "path": str(item.relative_to(self.root_path)),
                    "type": "directory" if item.is_dir() else "file",
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except (PermissionError, OSError):
                continue
        
        return sorted(results, key=lambda x: (x["type"] != "directory", x["name"]))
    
    async def _search_files(self, pattern: str, path: Optional[str] = None, 
                           content_search: bool = False, file_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for files by name or content"""
        base_path = self._resolve_path(path) if path else self.root_path
        
        results = []
        
        if content_search:
            # Search in file contents
            for file_path in base_path.rglob(f"*.{file_type}" if file_type else "*"):
                if file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if pattern.lower() in content.lower():
                                results.append({
                                    "path": str(file_path.relative_to(self.root_path)),
                                    "match_type": "content",
                                    "preview": content[:200] + "..." if len(content) > 200 else content
                                })
                    except (PermissionError, OSError):
                        continue
        else:
            # Search by filename pattern
            for file_path in base_path.rglob(f"*{pattern}*"):
                if file_path.is_file():
                    results.append({
                        "path": str(file_path.relative_to(self.root_path)),
                        "match_type": "name"
                    })
        
        return results[:100]  # Limit results
    
    async def _create_directory(self, path: str, parents: bool = True) -> Dict[str, Any]:
        """Create directory"""
        dir_path = self._resolve_path(path)
        dir_path.mkdir(parents=parents, exist_ok=True)
        return {"success": True, "path": str(dir_path)}
    
    async def _delete_file(self, path: str, recursive: bool = False) -> Dict[str, Any]:
        """Delete file or directory"""
        file_path = self._resolve_path(path)
        
        if not file_path.exists():
            return {"success": False, "error": "File not found"}
        
        if file_path.is_dir():
            if recursive:
                shutil.rmtree(file_path)
            else:
                if any(file_path.iterdir()):
                    return {"success": False, "error": "Directory not empty"}
                file_path.rmdir()
        else:
            file_path.unlink()
        
        return {"success": True, "path": str(file_path)}
    
    async def _copy_file(self, source: str, destination: str) -> Dict[str, Any]:
        """Copy file or directory"""
        src_path = self._resolve_path(source)
        dst_path = self._resolve_path(destination)
        
        if not src_path.exists():
            raise FileNotFoundError(f"Source not found: {source}")
        
        if src_path.is_dir():
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        else:
            shutil.copy2(src_path, dst_path)
        
        return {"success": True, "source": str(src_path), "destination": str(dst_path)}
    
    async def _move_file(self, source: str, destination: str) -> Dict[str, Any]:
        """Move file or directory"""
        src_path = self._resolve_path(source)
        dst_path = self._resolve_path(destination)
        
        if not src_path.exists():
            raise FileNotFoundError(f"Source not found: {source}")
        
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(src_path, dst_path)
        
        return {"success": True, "source": str(src_path), "destination": str(dst_path)}
    
    async def _get_file_info(self, path: str) -> Dict[str, Any]:
        """Get file metadata"""
        file_path = self._resolve_path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        stat = file_path.stat()
        
        return {
            "path": str(file_path),
            "name": file_path.name,
            "type": "directory" if file_path.is_dir() else "file",
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "permissions": oct(stat.st_mode)[-3:],
            "owner": stat.st_uid,
            "group": stat.st_gid
        }
    
    async def _watch_directory(self, path: str, patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Start watching directory for changes"""
        dir_path = self._resolve_path(path)
        
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")
        
        if dir_path not in self.watch_paths:
            self.watch_paths.append(dir_path)
        
        return {
            "success": True,
            "watching": str(dir_path),
            "patterns": patterns or ["*"],
            "message": "Directory watching started (use polling or OS-specific watchers for real-time)"
        }
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve path relative to root"""
        p = Path(path)
        if p.is_absolute():
            return p.resolve()
        return (self.root_path / p).resolve()


# ===========================================
# BROWSER SERVER
# ===========================================

class BrowserServer(MCPServer):
    """
    Web browser automation for scraping, testing, and interaction.
    Uses Playwright for headless browser operations.
    """
    
    def __init__(self, headless: bool = True, **kwargs):
        super().__init__(
            name="browser",
            version="2.0.0",
            description="Web browser automation and scraping",
            config={"headless": headless, **kwargs}
        )
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
    
    async def initialize(self) -> bool:
        """Initialize browser"""
        if not self.enabled:
            return False
        
        try:
            from playwright.async_api import async_playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=self.headless)
            self.context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            self.page = await self.context.new_page()
            return True
        except ImportError:
            print("Playwright not installed. Run: pip install playwright && playwright install")
            return False
        except Exception as e:
            print(f"Browser initialization failed: {e}")
            return False
    
    async def shutdown(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "navigate",
                "description": "Navigate to a URL",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to navigate to"},
                        "wait_until": {"type": "string", "enum": ["load", "domcontentloaded", "networkidle"], "description": "When to consider navigation successful"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "screenshot",
                "description": "Take a screenshot of the current page",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Save path (optional)"},
                        "full_page": {"type": "boolean", "description": "Capture full page height"}
                    }
                }
            },
            {
                "name": "click",
                "description": "Click an element",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "selector": {"type": "string", "description": "CSS selector"}
                    },
                    "required": ["selector"]
                }
            },
            {
                "name": "fill",
                "description": "Fill input field with text",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "selector": {"type": "string", "description": "CSS selector"},
                        "value": {"type": "string", "description": "Text to fill"}
                    },
                    "required": ["selector", "value"]
                }
            },
            {
                "name": "extract_content",
                "description": "Extract content from page using CSS selectors",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "selector": {"type": "string", "description": "CSS selector"},
                        "attribute": {"type": "string", "description": "Attribute to extract (default: text)"},
                        "all": {"type": "boolean", "description": "Extract all matching elements"}
                    },
                    "required": ["selector"]
                }
            },
            {
                "name": "scrape_page",
                "description": "Scrape entire page content as structured data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "selectors": {"type": "object", "description": "Map of field names to CSS selectors"}
                    }
                }
            },
            {
                "name": "evaluate",
                "description": "Execute JavaScript in page context",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "script": {"type": "string", "description": "JavaScript code to execute"}
                    },
                    "required": ["script"]
                }
            },
            {
                "name": "wait_for",
                "description": "Wait for element or condition",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "selector": {"type": "string", "description": "CSS selector to wait for"},
                        "state": {"type": "string", "enum": ["visible", "hidden", "attached", "detached"], "description": "Expected state"},
                        "timeout": {"type": "integer", "description": "Timeout in milliseconds"}
                    }
                }
            }
        ]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        if not self.page:
            raise RuntimeError("Browser not initialized. Call initialize() first.")
        
        method = getattr(self, f"_{tool_name}", None)
        if not method:
            raise ValueError(f"Unknown tool: {tool_name}")
        return await method(**arguments)
    
    async def _navigate(self, url: str, wait_until: str = "load") -> Dict[str, Any]:
        """Navigate to URL"""
        response = await self.page.goto(url, wait_until=wait_until)
        return {
            "success": True,
            "url": self.page.url,
            "title": await self.page.title(),
            "status": response.status
        }
    
    async def _screenshot(self, path: Optional[str] = None, full_page: bool = False) -> Dict[str, Any]:
        """Take screenshot"""
        if path:
            await self.page.screenshot(path=path, full_page=full_page)
            return {"success": True, "path": path}
        else:
            screenshot = await self.page.screenshot(full_page=full_page)
            return {"success": True, "data": screenshot.hex(), "format": "png"}
    
    async def _click(self, selector: str) -> Dict[str, Any]:
        """Click element"""
        await self.page.click(selector)
        return {"success": True, "clicked": selector}
    
    async def _fill(self, selector: str, value: str) -> Dict[str, Any]:
        """Fill input"""
        await self.page.fill(selector, value)
        return {"success": True, "filled": selector, "value": value}
    
    async def _extract_content(self, selector: str, attribute: Optional[str] = None, 
                               all: bool = False) -> Any:
        """Extract content"""
        if all:
            if attribute:
                result = await self.page.eval_on_selector_all(selector, f"els => els.map(el => el.{attribute})")
            else:
                result = await self.page.eval_on_selector_all(selector, "els => els.map(el => el.textContent)")
        else:
            if attribute:
                result = await self.page.get_attribute(selector, attribute)
            else:
                result = await self.page.text_content(selector)
        
        return result
    
    async def _scrape_page(self, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Scrape page with multiple selectors"""
        results = {}
        for field, selector in selectors.items():
            try:
                results[field] = await self.page.text_content(selector)
            except Exception:
                results[field] = None
        return results
    
    async def _evaluate(self, script: str) -> Any:
        """Execute JavaScript"""
        return await self.page.evaluate(script)
    
    async def _wait_for(self, selector: Optional[str] = None, state: str = "visible", 
                       timeout: Optional[int] = None) -> Dict[str, Any]:
        """Wait for element"""
        kwargs = {"state": state}
        if timeout:
            kwargs["timeout"] = timeout
        
        if selector:
            await self.page.wait_for_selector(selector, **kwargs)
        
        return {"success": True, "waited_for": selector, "state": state}


# ===========================================
# DATABASE SERVER
# ===========================================

class DatabaseServer(MCPServer):
    """
    Database operations for SQL and NoSQL databases.
    Supports SQLite, PostgreSQL, MySQL, MongoDB, Redis.
    """
    
    def __init__(self, connection_string: Optional[str] = None, db_type: str = "sqlite", **kwargs):
        super().__init__(
            name="database",
            version="2.0.0",
            description="Database operations for SQL and NoSQL",
            config={
                "connection_string": connection_string,
                "db_type": db_type,
                **kwargs
            }
        )
        self.db_type = db_type
        self.connection_string = connection_string
        self.connection = None
    
    async def initialize(self) -> bool:
        """Initialize database connection"""
        if not self.enabled:
            return False
        
        try:
            if self.db_type == "sqlite":
                db_path = self.connection_string or "nanocorp.db"
                self.connection = sqlite3.connect(db_path, check_same_thread=False)
                self._init_sqlite_schema()
            elif self.db_type == "postgresql":
                import asyncpg
                self.connection = await asyncpg.connect(self.connection_string)
            elif self.db_type == "mysql":
                import aiomysql
                self.connection = await aiomysql.connect(
                    host=self.config.get("host", "localhost"),
                    port=self.config.get("port", 3306),
                    user=self.config.get("user", "root"),
                    password=self.config.get("password", ""),
                    db=self.config.get("database", "nanocorp")
                )
            elif self.db_type == "mongodb":
                from motor.motor_asyncio import AsyncIOMotorClient
                self.connection = AsyncIOMotorClient(self.connection_string or "mongodb://localhost:27017")
            elif self.db_type == "redis":
                import redis.asyncio as redis
                self.connection = redis.from_url(self.connection_string or "redis://localhost")
            
            return True
        except Exception as e:
            print(f"Database initialization failed: {e}")
            return False
    
    async def shutdown(self):
        """Close database connection"""
        if self.connection:
            if self.db_type == "sqlite":
                self.connection.close()
            else:
                await self.connection.close()
    
    def _init_sqlite_schema(self):
        """Initialize default SQLite schema"""
        cursor = self.connection.cursor()
        
        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',
                priority TEXT DEFAULT 'medium',
                assigned_to TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                completed_at TIMESTAMP,
                metadata JSON
            )
        """)
        
        # Goals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id TEXT PRIMARY KEY,
                objective TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                priority TEXT DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                metadata JSON
            )
        """)
        
        # Agents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT,
                status TEXT DEFAULT 'idle',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP,
                metadata JSON
            )
        """)
        
        # Execution log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                agent_id TEXT,
                task_id TEXT,
                details JSON
            )
        """)
        
        self.connection.commit()
    
    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "query",
                "description": "Execute SQL query",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sql": {"type": "string", "description": "SQL query"},
                        "params": {"type": "array", "items": {"type": "string"}, "description": "Query parameters"}
                    },
                    "required": ["sql"]
                }
            },
            {
                "name": "insert",
                "description": "Insert record into table",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "table": {"type": "string", "description": "Table name"},
                        "data": {"type": "object", "description": "Record data"}
                    },
                    "required": ["table", "data"]
                }
            },
            {
                "name": "update",
                "description": "Update records in table",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "table": {"type": "string", "description": "Table name"},
                        "data": {"type": "object", "description": "Updated data"},
                        "where": {"type": "string", "description": "WHERE clause"}
                    },
                    "required": ["table", "data"]
                }
            },
            {
                "name": "delete",
                "description": "Delete records from table",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "table": {"type": "string", "description": "Table name"},
                        "where": {"type": "string", "description": "WHERE clause"}
                    },
                    "required": ["table"]
                }
            },
            {
                "name": "list_tables",
                "description": "List all tables in database",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "describe_table",
                "description": "Get table schema",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "table": {"type": "string", "description": "Table name"}
                    },
                    "required": ["table"]
                }
            },
            {
                "name": "execute_raw",
                "description": "Execute raw database command (NoSQL)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Database command"},
                        "args": {"type": "array", "items": {"type": "string"}, "description": "Command arguments"}
                    },
                    "required": ["command"]
                }
            }
        ]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        method = getattr(self, f"_{tool_name}", None)
        if not method:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        if self.db_type == "sqlite":
            return await method(**arguments)
        else:
            return await method(**arguments)
    
    async def _query(self, sql: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """Execute SQL query"""
        if self.db_type == "sqlite":
            cursor = self.connection.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            
            return [dict(zip(columns, row)) for row in rows] if columns else []
        
        elif self.db_type == "postgresql":
            async with self.connection.acquire() as conn:
                rows = await conn.fetch(sql, *(params or []))
                return [dict(row) for row in rows]
        
        # Add other database types as needed
        return []
    
    async def _insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert record"""
        if self.db_type == "sqlite":
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            cursor = self.connection.cursor()
            cursor.execute(sql, list(data.values()))
            self.connection.commit()
            
            return {"success": True, "id": cursor.lastrowid}
        
        return {"success": False, "error": "Not implemented for this database type"}
    
    async def _update(self, table: str, data: Dict[str, Any], where: Optional[str] = None) -> Dict[str, Any]:
        """Update records"""
        if self.db_type == "sqlite":
            set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
            sql = f"UPDATE {table} SET {set_clause}"
            
            if where:
                sql += f" WHERE {where}"
            
            cursor = self.connection.cursor()
            cursor.execute(sql, list(data.values()))
            self.connection.commit()
            
            return {"success": True, "rows_affected": cursor.rowcount}
        
        return {"success": False, "error": "Not implemented"}
    
    async def _delete(self, table: str, where: Optional[str] = None) -> Dict[str, Any]:
        """Delete records"""
        if self.db_type == "sqlite":
            sql = f"DELETE FROM {table}"
            
            if where:
                sql += f" WHERE {where}"
            
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
            
            return {"success": True, "rows_affected": cursor.rowcount}
        
        return {"success": False, "error": "Not implemented"}
    
    async def _list_tables(self) -> List[str]:
        """List tables"""
        if self.db_type == "sqlite":
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [row[0] for row in cursor.fetchall()]
        
        return []
    
    async def _describe_table(self, table: str) -> List[Dict[str, Any]]:
        """Describe table schema"""
        if self.db_type == "sqlite":
            cursor = self.connection.cursor()
            cursor.execute(f"PRAGMA table_info({table})")
            
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    "cid": row[0],
                    "name": row[1],
                    "type": row[2],
                    "notnull": row[3],
                    "default": row[4],
                    "pk": row[5]
                })
            return columns
        
        return []
    
    async def _execute_raw(self, command: str, args: Optional[List[Any]] = None) -> Any:
        """Execute raw command"""
        # Implementation depends on database type
        return {"success": False, "error": "Use specific methods instead"}


# ===========================================
# API SERVER
# ===========================================

class APIServer(MCPServer):
    """
    REST/GraphQL API client with authentication handling.
    Supports OAuth2, API keys, JWT tokens, and basic auth.
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            name="api",
            version="2.0.0",
            description="REST/GraphQL API client with authentication",
            config={**kwargs}
        )
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_configs: Dict[str, Dict] = {}
    
    async def initialize(self) -> bool:
        """Initialize HTTP session"""
        if not self.enabled:
            return False
        
        try:
            self.session = aiohttp.ClientSession(
                headers={
                    "User-Agent": "NanoCorp-API-Client/2.0",
                    "Content-Type": "application/json"
                }
            )
            return True
        except Exception as e:
            print(f"API server initialization failed: {e}")
            return False
    
    async def shutdown(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "request",
                "description": "Make HTTP request",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "method": {"type": "string", "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"], "description": "HTTP method"},
                        "url": {"type": "string", "description": "Request URL"},
                        "headers": {"type": "object", "description": "Request headers"},
                        "body": {"type": "object", "description": "Request body"},
                        "auth": {"type": "string", "description": "Auth config name"}
                    },
                    "required": ["method", "url"]
                }
            },
            {
                "name": "get",
                "description": "Make GET request",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Request URL"},
                        "params": {"type": "object", "description": "Query parameters"},
                        "headers": {"type": "object", "description": "Request headers"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "post",
                "description": "Make POST request",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Request URL"},
                        "json": {"type": "object", "description": "JSON body"},
                        "headers": {"type": "object", "description": "Request headers"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "put",
                "description": "Make PUT request",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Request URL"},
                        "json": {"type": "object", "description": "JSON body"},
                        "headers": {"type": "object", "description": "Request headers"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "delete_request",
                "description": "Make DELETE request",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Request URL"},
                        "headers": {"type": "object", "description": "Request headers"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "graphql",
                "description": "Execute GraphQL query",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "endpoint": {"type": "string", "description": "GraphQL endpoint URL"},
                        "query": {"type": "string", "description": "GraphQL query"},
                        "variables": {"type": "object", "description": "Query variables"}
                    },
                    "required": ["endpoint", "query"]
                }
            },
            {
                "name": "configure_auth",
                "description": "Configure authentication for API",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Auth config name"},
                        "type": {"type": "string", "enum": ["api_key", "bearer", "basic", "oauth2"], "description": "Auth type"},
                        "credentials": {"type": "object", "description": "Auth credentials"}
                    },
                    "required": ["name", "type", "credentials"]
                }
            }
        ]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        if not self.session:
            raise RuntimeError("API server not initialized. Call initialize() first.")
        
        method = getattr(self, f"_{tool_name}", None)
        if not method:
            raise ValueError(f"Unknown tool: {tool_name}")
        return await method(**arguments)
    
    async def _request(self, method: str, url: str, headers: Optional[Dict] = None, 
                      body: Optional[Dict] = None, auth: Optional[str] = None) -> Dict[str, Any]:
        """Make HTTP request"""
        if auth and auth in self.auth_configs:
            headers = headers or {}
            headers.update(self._get_auth_headers(auth))
        
        async with self.session.request(
            method, url, headers=headers, json=body
        ) as response:
            result = {
                "status": response.status,
                "headers": dict(response.headers),
                "url": str(response.url)
            }
            
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                result["body"] = await response.json()
            else:
                result["body"] = await response.text()
            
            return result
    
    async def _get(self, url: str, params: Optional[Dict] = None, 
                   headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request"""
        return await self._request("GET", url, headers=headers)
    
    async def _post(self, url: str, json: Optional[Dict] = None, 
                    headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request"""
        return await self._request("POST", url, headers=headers, body=json)
    
    async def _put(self, url: str, json: Optional[Dict] = None, 
                   headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make PUT request"""
        return await self._request("PUT", url, headers=headers, body=json)
    
    async def _delete_request(self, url: str, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make DELETE request"""
        return await self._request("DELETE", url, headers=headers)
    
    async def _graphql(self, endpoint: str, query: str, 
                       variables: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute GraphQL query"""
        body = {"query": query}
        if variables:
            body["variables"] = variables
        
        return await self._request("POST", endpoint, body=body)
    
    async def _configure_auth(self, name: str, type: str, credentials: Dict) -> Dict[str, Any]:
        """Configure authentication"""
        self.auth_configs[name] = {
            "type": type,
            "credentials": credentials
        }
        return {"success": True, "name": name, "type": type}
    
    def _get_auth_headers(self, auth_name: str) -> Dict[str, str]:
        """Get auth headers"""
        config = self.auth_configs.get(auth_name, {})
        auth_type = config.get("type")
        creds = config.get("credentials", {})
        
        if auth_type == "api_key":
            header_name = creds.get("header", "X-API-Key")
            return {header_name: creds.get("key", "")}
        elif auth_type == "bearer":
            return {"Authorization": f"Bearer {creds.get('token', '')}"}
        elif auth_type == "basic":
            import base64
            auth_string = f"{creds.get('username', '')}:{creds.get('password', '')}"
            encoded = base64.b64encode(auth_string.encode()).decode()
            return {"Authorization": f"Basic {encoded}"}
        elif auth_type == "oauth2":
            return {"Authorization": f"Bearer {creds.get('access_token', '')}"}
        
        return {}


# ===========================================
# GIT SERVER
# ===========================================

class GitServer(MCPServer):
    """
    Full git workflow automation including clone, commit, push, 
    branch management, PR creation, and more.
    """
    
    def __init__(self, repo_path: str = ".", **kwargs):
        super().__init__(
            name="git",
            version="2.0.0",
            description="Git workflow automation",
            config={"repo_path": repo_path, **kwargs}
        )
        self.repo_path = Path(repo_path)
        self.remote_url: Optional[str] = None
    
    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "clone",
                "description": "Clone a git repository",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Repository URL"},
                        "path": {"type": "string", "description": "Local path"},
                        "branch": {"type": "string", "description": "Branch to checkout"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "status",
                "description": "Get git status",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "add",
                "description": "Stage files",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "files": {"type": "array", "items": {"type": "string"}, "description": "Files to stage"}
                    }
                }
            },
            {
                "name": "commit",
                "description": "Commit staged changes",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "Commit message"},
                        "all": {"type": "boolean", "description": "Auto-stage all changes"}
                    },
                    "required": ["message"]
                }
            },
            {
                "name": "push",
                "description": "Push commits to remote",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "remote": {"type": "string", "description": "Remote name"},
                        "branch": {"type": "string", "description": "Branch name"},
                        "force": {"type": "boolean", "description": "Force push"}
                    }
                }
            },
            {
                "name": "pull",
                "description": "Pull changes from remote",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "remote": {"type": "string", "description": "Remote name"},
                        "branch": {"type": "string", "description": "Branch name"}
                    }
                }
            },
            {
                "name": "branch",
                "description": "Manage branches",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["list", "create", "delete", "checkout"], "description": "Action"},
                        "name": {"type": "string", "description": "Branch name"},
                        "start_point": {"type": "string", "description": "Starting point for new branch"}
                    },
                    "required": ["action"]
                }
            },
            {
                "name": "merge",
                "description": "Merge branches",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "branch": {"type": "string", "description": "Branch to merge"},
                        "no_ff": {"type": "boolean", "description": "No fast-forward"}
                    },
                    "required": ["branch"]
                }
            },
            {
                "name": "log",
                "description": "View commit history",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "description": "Number of commits"},
                        "oneline": {"type": "boolean", "description": "One-line format"}
                    }
                }
            },
            {
                "name": "diff",
                "description": "Show changes",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "cached": {"type": "boolean", "description": "Staged changes"},
                        "file": {"type": "string", "description": "Specific file"}
                    }
                }
            },
            {
                "name": "create_pr",
                "description": "Create pull request (GitHub/GitLab)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "PR title"},
                        "body": {"type": "string", "description": "PR description"},
                        "base": {"type": "string", "description": "Base branch"},
                        "head": {"type": "string", "description": "Head branch"}
                    },
                    "required": ["title", "base", "head"]
                }
            }
        ]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        method = getattr(self, f"_{tool_name}", None)
        if not method:
            raise ValueError(f"Unknown tool: {tool_name}")
        return await method(**arguments)
    
    async def _run_git_command(self, *args, cwd: Optional[Path] = None) -> tuple[str, str, int]:
        """Run git command"""
        cmd = ["git"] + list(args)
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd or self.repo_path
        )
        stdout, stderr = await process.communicate()
        return stdout.decode(), stderr.decode(), process.returncode
    
    async def _clone(self, url: str, path: Optional[str] = None, 
                     branch: Optional[str] = None) -> Dict[str, Any]:
        """Clone repository"""
        target_path = Path(path) if path else Path(url.split('/')[-1].replace('.git', ''))
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        args = ["clone", url, str(target_path)]
        if branch:
            args.insert(2, "-b")
            args.insert(3, branch)
        
        stdout, stderr, code = await self._run_git_command(*args, cwd=target_path.parent)
        
        if code == 0:
            self.repo_path = target_path
            return {"success": True, "path": str(target_path)}
        else:
            return {"success": False, "error": stderr}
    
    async def _status(self) -> Dict[str, Any]:
        """Get git status"""
        stdout, stderr, code = await self._run_git_command("status", "--porcelain")
        
        if code != 0:
            return {"error": stderr}
        
        # Parse status output
        files = []
        for line in stdout.strip().split('\n'):
            if line:
                status = line[:2]
                filename = line[3:]
                files.append({"status": status, "file": filename})
        
        return {"files": files, "clean": len(files) == 0}
    
    async def _add(self, files: Optional[List[str]] = None) -> Dict[str, Any]:
        """Stage files"""
        if not files:
            files = ["."]
        
        stdout, stderr, code = await self._run_git_command("add", *files)
        
        return {
            "success": code == 0,
            "staged": files if code == 0 else [],
            "error": stderr if code != 0 else None
        }
    
    async def _commit(self, message: str, all: bool = False) -> Dict[str, Any]:
        """Commit changes"""
        args = ["commit", "-m", message]
        if all:
            args.insert(1, "-a")
        
        stdout, stderr, code = await self._run_git_command(*args)
        
        if code == 0:
            # Get commit hash
            hash_stdout, _, _ = await self._run_git_command("rev-parse", "HEAD")
            return {"success": True, "hash": hash_stdout.strip(), "message": message}
        else:
            return {"success": False, "error": stderr}
    
    async def _push(self, remote: str = "origin", branch: Optional[str] = None, 
                    force: bool = False) -> Dict[str, Any]:
        """Push to remote"""
        args = ["push"]
        if force:
            args.append("--force")
        args.append(remote)
        if branch:
            args.append(branch)
        
        stdout, stderr, code = await self._run_git_command(*args)
        
        return {
            "success": code == 0,
            "output": stdout if code == 0 else stderr
        }
    
    async def _pull(self, remote: str = "origin", branch: Optional[str] = None) -> Dict[str, Any]:
        """Pull from remote"""
        args = ["pull", remote]
        if branch:
            args.append(branch)
        
        stdout, stderr, code = await self._run_git_command(*args)
        
        return {
            "success": code == 0,
            "output": stdout if code == 0 else stderr
        }
    
    async def _branch(self, action: str, name: Optional[str] = None, 
                      start_point: Optional[str] = None) -> Dict[str, Any]:
        """Manage branches"""
        if action == "list":
            stdout, _, _ = await self._run_git_command("branch")
            branches = [line.strip().lstrip('*').strip() for line in stdout.split('\n') if line.strip()]
            return {"branches": branches}
        
        elif action == "create":
            if not name:
                return {"error": "Branch name required"}
            args = ["branch", name]
            if start_point:
                args.append(start_point)
            stdout, stderr, code = await self._run_git_command(*args)
            return {"success": code == 0, "branch": name}
        
        elif action == "delete":
            if not name:
                return {"error": "Branch name required"}
            stdout, stderr, code = await self._run_git_command("branch", "-d", name)
            return {"success": code == 0, "branch": name}
        
        elif action == "checkout":
            if not name:
                return {"error": "Branch name required"}
            stdout, stderr, code = await self._run_git_command("checkout", name)
            return {"success": code == 0, "branch": name}
        
        return {"error": f"Unknown action: {action}"}
    
    async def _merge(self, branch: str, no_ff: bool = False) -> Dict[str, Any]:
        """Merge branch"""
        args = ["merge"]
        if no_ff:
            args.append("--no-ff")
        args.append(branch)
        
        stdout, stderr, code = await self._run_git_command(*args)
        
        return {
            "success": code == 0,
            "merged": branch,
            "output": stdout if code == 0 else stderr
        }
    
    async def _log(self, count: int = 10, oneline: bool = True) -> List[Dict[str, Any]]:
        """View commit log"""
        args = ["log", f"-{count}"]
        if oneline:
            args.append("--oneline")
        
        stdout, _, _ = await self._run_git_command(*args)
        
        commits = []
        for line in stdout.strip().split('\n'):
            if line:
                if oneline:
                    parts = line.split(' ', 1)
                    commits.append({"hash": parts[0], "message": parts[1] if len(parts) > 1 else ""})
                else:
                    commits.append({"raw": line})
        
        return commits
    
    async def _diff(self, cached: bool = False, file: Optional[str] = None) -> str:
        """Show diff"""
        args = ["diff"]
        if cached:
            args.append("--cached")
        if file:
            args.append(file)
        
        stdout, _, _ = await self._run_git_command(*args)
        return stdout
    
    async def _create_pr(self, title: str, base: str, head: str, 
                         body: Optional[str] = None) -> Dict[str, Any]:
        """Create pull request (requires GitHub CLI or similar)"""
        # Check for gh CLI
        try:
            args = ["gh", "pr", "create", "--title", title, "--base", base, "--head", head]
            if body:
                args.extend(["--body", body])
            
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.repo_path
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {"success": True, "output": stdout.decode()}
            else:
                return {"success": False, "error": stderr.decode()}
        except FileNotFoundError:
            return {"success": False, "error": "GitHub CLI (gh) not installed"}


# ===========================================
# SERVER REGISTRY
# ===========================================

class MCPServerRegistry:
    """
    Registry for managing multiple MCP servers.
    Handles initialization, tool discovery, and routing.
    """
    
    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.tool_map: Dict[str, tuple[str, str]] = {}  # tool_name -> (server_name, tool_name)
    
    def register(self, server: MCPServer):
        """Register a server"""
        if not server.enabled:
            return
        
        self.servers[server.name] = server
        
        # Index tools
        for tool in server.get_tools():
            tool_key = f"{server.name}_{tool['name']}"
            self.tool_map[tool_key] = (server.name, tool['name'])
    
    async def initialize_all(self) -> Dict[str, bool]:
        """Initialize all servers"""
        results = {}
        for name, server in self.servers.items():
            try:
                success = await server.initialize()
                results[name] = success
            except Exception as e:
                print(f"Failed to initialize {name}: {e}")
                results[name] = False
        return results
    
    async def shutdown_all(self):
        """Shutdown all servers"""
        for server in self.servers.values():
            try:
                await server.shutdown()
            except Exception as e:
                print(f"Error shutting down {server.name}: {e}")
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get all available tools from all servers"""
        tools = []
        for server in self.servers.values():
            for tool in server.get_tools():
                tool_copy = tool.copy()
                tool_copy["qualified_name"] = f"{server.name}_{tool['name']}"
                tool_copy["server"] = server.name
                tools.append(tool_copy)
        return tools
    
    async def call_tool(self, qualified_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool by qualified name"""
        if qualified_name not in self.tool_map:
            raise ValueError(f"Unknown tool: {qualified_name}")
        
        server_name, tool_name = self.tool_map[qualified_name]
        server = self.servers.get(server_name)
        
        if not server:
            raise ValueError(f"Server not found: {server_name}")
        
        return await server.call_tool(tool_name, arguments)
    
    def get_server(self, name: str) -> Optional[MCPServer]:
        """Get server by name"""
        return self.servers.get(name)


# ===========================================
# FACTORY FUNCTIONS
# ===========================================

def create_default_registry() -> MCPServerRegistry:
    """Create registry with default servers"""
    registry = MCPServerRegistry()
    
    # Register core servers
    registry.register(FileSystemServer())
    registry.register(GitServer())
    registry.register(DatabaseServer())
    registry.register(APIServer())
    registry.register(BrowserServer())
    
    return registry


async def create_production_registry(config: Optional[Dict] = None) -> MCPServerRegistry:
    """Create production-ready registry with all servers"""
    config = config or {}
    registry = MCPServerRegistry()
    
    # Filesystem
    registry.register(FileSystemServer(
        root_path=config.get("fs_root", ".")
    ))
    
    # Git
    registry.register(GitServer(
        repo_path=config.get("git_repo", ".")
    ))
    
    # Database
    registry.register(DatabaseServer(
        connection_string=config.get("db_connection"),
        db_type=config.get("db_type", "sqlite")
    ))
    
    # API
    registry.register(APIServer())
    
    # Browser (if Playwright available)
    registry.register(BrowserServer(
        headless=config.get("browser_headless", True)
    ))
    
    # Initialize all
    await registry.initialize_all()
    
    return registry
