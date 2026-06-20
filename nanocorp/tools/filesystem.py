"""
NanoCorp v3.0 - Filesystem Tools

File operations with safety checks.
"""
from __future__ import annotations

import os
import shutil
import glob as glob_module
from pathlib import Path
from typing import List, Optional
import hashlib
from datetime import datetime

from .base import BaseTool, ToolOutput, success_result, error_result, ToolCategory


# ===========================================
# FILE READ TOOL
# ===========================================

class FileReadTool(BaseTool):
    """Read file contents with encoding detection."""
    
    @property
    def name(self) -> str:
        return "file_read"
    
    @property
    def description(self) -> str:
        return "Read the contents of a file. Returns the file content as text."
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.FILE
    
    def execute(
        self,
        path: str,
        encoding: str = "utf-8",
        lines: Optional[int] = None,
        offset: int = 0
    ) -> ToolOutput:
        """
        Read file contents.
        
        Args:
            path: File path to read
            encoding: Text encoding (default: utf-8)
            lines: Number of lines to read (None for all)
            offset: Line offset to start reading from
        
        Returns:
            File contents
        """
        try:
            file_path = Path(path).expanduser().resolve()
            
            if not file_path.exists():
                return error_result(f"File not found: {path}")
            
            if not file_path.is_file():
                return error_result(f"Path is not a file: {path}")
            
            with open(file_path, "r", encoding=encoding) as f:
                if lines:
                    # Read specific lines
                    for _ in range(offset):
                        f.readline()
                    content = "".join(f.readline() for _ in range(lines))
                else:
                    content = f.read()
            
            return success_result(
                content,
                path=str(file_path),
                lines=len(content.splitlines()) if lines else None,
                size=file_path.stat().st_size
            )
            
        except UnicodeDecodeError:
            # Binary file
            return error_result(f"File is binary, cannot read as text: {path}")
        except Exception as e:
            return error_result(f"Failed to read file: {e}")


# ===========================================
# FILE WRITE TOOL
# ===========================================

class FileWriteTool(BaseTool):
    """Write content to a file with backup."""
    
    def __init__(self, backup: bool = True):
        super().__init__()
        self.backup = backup
    
    @property
    def name(self) -> str:
        return "file_write"
    
    @property
    def description(self) -> str:
        return "Write content to a file. Creates parent directories if needed."
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.FILE
    
    def execute(
        self,
        path: str,
        content: str,
        encoding: str = "utf-8",
        create_backup: bool = True
    ) -> ToolOutput:
        """
        Write content to file.
        
        Args:
            path: File path to write
            content: Content to write
            encoding: Text encoding
            create_backup: Create backup of existing file
        
        Returns:
            Success status and file path
        """
        try:
            file_path = Path(path).expanduser().resolve()
            
            # Create parent directories
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Backup existing file
            backup_path = None
            if create_backup and file_path.exists():
                backup_path = file_path.with_suffix(file_path.suffix + ".bak")
                shutil.copy2(file_path, backup_path)
            
            # Write content
            with open(file_path, "w", encoding=encoding) as f:
                f.write(content)
            
            return success_result(
                {"path": str(file_path), "backup": str(backup_path) if backup_path else None},
                bytes_written=len(content.encode(encoding))
            )
            
        except Exception as e:
            return error_result(f"Failed to write file: {e}")


# ===========================================
# FILE EDIT TOOL
# ===========================================

class FileEditTool(BaseTool):
    """Edit specific parts of a file using search and replace."""
    
    @property
    def name(self) -> str:
        return "file_edit"
    
    @property
    def description(self) -> str:
        return "Edit a file by replacing specific text. Searches for old_str and replaces with new_str."
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.FILE
    
    def execute(
        self,
        path: str,
        old_str: str,
        new_str: str,
        count: int = 1
    ) -> ToolOutput:
        """
        Edit file with search and replace.
        
        Args:
            path: File path to edit
            old_str: Text to find
            new_str: Text to replace with
            count: Number of replacements (1 for first, -1 for all)
        
        Returns:
            Number of replacements made
        """
        try:
            file_path = Path(path).expanduser().resolve()
            
            if not file_path.exists():
                return error_result(f"File not found: {path}")
            
            # Read content
            with open(file_path, "r") as f:
                content = f.read()
            
            # Count occurrences
            occurrences = content.count(old_str)
            
            if occurrences == 0:
                return error_result(f"Text not found in file: {old_str[:50]}...")
            
            # Replace
            if count == -1:
                new_content = content.replace(old_str, new_str)
                replacements = occurrences
            else:
                new_content = content.replace(old_str, new_str, count)
                replacements = 1
            
            # Write back
            with open(file_path, "w") as f:
                f.write(new_content)
            
            return success_result(
                {"path": str(file_path), "replacements": replacements},
                occurrences_found=occurrences
            )
            
        except Exception as e:
            return error_result(f"Failed to edit file: {e}")


# ===========================================
# FILE GLOB TOOL
# ===========================================

class FileGlobTool(BaseTool):
    """Find files by pattern."""
    
    @property
    def name(self) -> str:
        return "file_glob"
    
    @property
    def description(self) -> str:
        return "Find files matching a glob pattern. Supports *, **, ? wildcards."
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.FILE
    
    def execute(
        self,
        pattern: str,
        root: Optional[str] = None,
        recursive: bool = True,
        include_hidden: bool = False
    ) -> ToolOutput:
        """
        Find files matching pattern.
        
        Args:
            pattern: Glob pattern (e.g., "*.py", "**/*.js")
            root: Root directory to search from
            recursive: Search recursively
            include_hidden: Include hidden files
        
        Returns:
            List of matching file paths
        """
        try:
            if root:
                search_root = Path(root).expanduser().resolve()
            else:
                search_root = Path.cwd()
            
            # Handle recursive pattern
            if "**" in pattern:
                glob_pattern = pattern
            elif recursive:
                glob_pattern = f"**/{pattern}"
            else:
                glob_pattern = pattern
            
            matches = []
            for match in search_root.glob(glob_pattern):
                if match.is_file():
                    if not match.name.startswith(".") or include_hidden:
                        matches.append(str(match))
            
            return success_result(matches, count=len(matches))
            
        except Exception as e:
            return error_result(f"Glob failed: {e}")


# ===========================================
# FILE SEARCH TOOL
# ===========================================

class FileSearchTool(BaseTool):
    """Search for text within files."""
    
    @property
    def name(self) -> str:
        return "file_search"
    
    @property
    def description(self) -> str:
        return "Search for text within files using grep-like patterns."
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.FILE
    
    def execute(
        self,
        pattern: str,
        path: str = ".",
        file_pattern: str = "*",
        case_sensitive: bool = True,
        regex: bool = True,
        context_lines: int = 0
    ) -> ToolOutput:
        """
        Search for pattern in files.
        
        Args:
            pattern: Text or regex pattern to search
            path: Directory to search in
            file_pattern: Only search in files matching this glob
            case_sensitive: Case-sensitive search
            regex: Treat pattern as regex
            context_lines: Number of context lines around matches
        
        Returns:
            List of matches with file:line:content
        """
        try:
            import re
            
            search_path = Path(path).expanduser().resolve()
            
            # Compile pattern
            flags = 0 if case_sensitive else re.IGNORECASE
            if regex:
                compiled = re.compile(pattern, flags)
            else:
                compiled = re.compile(re.escape(pattern), flags)
            
            matches = []
            
            for file_path in search_path.rglob(file_pattern):
                if not file_path.is_file():
                    continue
                if file_path.name.startswith("."):
                    continue
                
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                    
                    for i, line in enumerate(lines, 1):
                        if compiled.search(line):
                            match_info = {
                                "file": str(file_path.relative_to(search_path)),
                                "line": i,
                                "content": line.rstrip()
                            }
                            
                            if context_lines > 0:
                                start = max(0, i - context_lines - 1)
                                end = min(len(lines), i + context_lines)
                                match_info["context"] = [
                                    lines[j].rstrip() 
                                    for j in range(start, end)
                                ]
                            
                            matches.append(match_info)
                            
                except (UnicodeDecodeError, PermissionError):
                    continue
            
            return success_result(matches, count=len(matches))
            
        except Exception as e:
            return error_result(f"Search failed: {e}")


# ===========================================
# FILE INFO TOOL
# ===========================================

class FileInfoTool(BaseTool):
    """Get file/directory information."""
    
    @property
    def name(self) -> str:
        return "file_info"
    
    @property
    def description(self) -> str:
        return "Get information about a file or directory."
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.FILE
    
    def execute(self, path: str) -> ToolOutput:
        """
        Get file/directory info.
        
        Returns size, timestamps, type, etc.
        """
        try:
            file_path = Path(path).expanduser().resolve()
            
            if not file_path.exists():
                return error_result(f"Path does not exist: {path}")
            
            stat = file_path.stat()
            
            info = {
                "path": str(file_path),
                "name": file_path.name,
                "type": "directory" if file_path.is_dir() else "file",
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "is_file": file_path.is_file(),
                "is_dir": file_path.is_dir(),
                "is_symlink": file_path.is_symlink(),
            }
            
            if file_path.is_file():
                # Calculate hash
                with open(file_path, "rb") as f:
                    info["md5"] = hashlib.md5(f.read()).hexdigest()
            
            if file_path.is_dir():
                # Count contents
                info["file_count"] = sum(1 for _ in file_path.rglob("*") if _.is_file())
                info["dir_count"] = sum(1 for _ in file_path.rglob("*") if _.is_dir())
            
            return success_result(info)
            
        except Exception as e:
            return error_result(f"Failed to get file info: {e}")


# ===========================================
# FILE LIST TOOL
# ===========================================

class FileListTool(BaseTool):
    """List directory contents."""
    
    @property
    def name(self) -> str:
        return "file_list"
    
    @property
    def description(self) -> str:
        return "List contents of a directory."
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.FILE
    
    def execute(
        self,
        path: str = ".",
        show_hidden: bool = False,
        recursive: bool = False,
        details: bool = True
    ) -> ToolOutput:
        """
        List directory contents.
        
        Args:
            path: Directory to list
            show_hidden: Include hidden files
            recursive: List recursively
            details: Include file details
        
        Returns:
            List of files/directories
        """
        try:
            dir_path = Path(path).expanduser().resolve()
            
            if not dir_path.exists():
                return error_result(f"Directory not found: {path}")
            
            if not dir_path.is_dir():
                return error_result(f"Path is not a directory: {path}")
            
            results = []
            
            if recursive:
                iterator = dir_path.rglob("*")
            else:
                iterator = dir_path.iterdir()
            
            for item in iterator:
                if not show_hidden and item.name.startswith("."):
                    continue
                
                if details:
                    stat = item.stat()
                    results.append({
                        "name": item.name,
                        "type": "dir" if item.is_dir() else "file",
                        "size": stat.st_size if item.is_file() else None,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    })
                else:
                    results.append(item.name)
            
            return success_result(results, count=len(results))
            
        except Exception as e:
            return error_result(f"Failed to list directory: {e}")


# ===========================================
# EXPORTS
# ===========================================

__all__ = [
    "FileReadTool",
    "FileWriteTool",
    "FileEditTool",
    "FileGlobTool",
    "FileSearchTool",
    "FileInfoTool",
    "FileListTool",
]
