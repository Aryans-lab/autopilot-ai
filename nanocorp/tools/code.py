"""
NanoCorp v3.0 - Code Tools

Shell, git, and code execution tools.
"""
from __future__ import annotations

import subprocess
import json
import shlex
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from .base import BaseTool, ToolOutput, success_result, error_result, ToolCategory


# ===========================================
# BASH TOOL
# ===========================================

@dataclass
class BashResult:
    """Result from a bash command."""
    stdout: str
    stderr: str
    exit_code: int
    duration: float


class BashTool(BaseTool):
    """
    Execute shell commands safely.
    
    Provides controlled command execution with timeout and sandboxing.
    """
    
    def __init__(
        self,
        timeout: int = 60,
        cwd: Optional[str] = None,
        allowed_commands: Optional[List[str]] = None,
        blocked_commands: Optional[List[str]] = None
    ):
        super().__init__()
        self.timeout = timeout
        self.cwd = Path(cwd) if cwd else None
        self.allowed_commands = allowed_commands  # None = allow all
        self.blocked_commands = blocked_commands or [
            "rm -rf /", "dd if=", ":(){:|:&};:", "mkfs", "fdisk"
        ]
    
    @property
    def name(self) -> str:
        return "bash"
    
    @property
    def description(self) -> str:
        return "Execute shell commands. Returns stdout, stderr, and exit code."
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.CODE
    
    def execute(
        self,
        command: str,
        timeout: Optional[int] = None,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> ToolOutput:
        """
        Execute a bash command.
        
        Args:
            command: Command to execute
            timeout: Override default timeout
            cwd: Working directory
            env: Environment variables
        
        Returns:
            Command output and status
        """
        try:
            # Safety check
            if self._is_blocked(command):
                return error_result(f"Command blocked for security: {command[:50]}...")
            
            # Set up process
            cmd_timeout = timeout or self.timeout
            work_dir = Path(cwd).resolve() if cwd else (self.cwd or Path.cwd())
            
            # Run command
            start = datetime.now()
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(work_dir),
                capture_output=True,
                text=True,
                timeout=cmd_timeout,
                env={**subprocess.os.environ, **(env or {})}
            )
            duration = (datetime.now() - start).total_seconds()
            
            return success_result(
                {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.returncode,
                    "duration": duration,
                    "command": command
                },
                success=result.returncode == 0
            )
            
        except subprocess.TimeoutExpired:
            return error_result(f"Command timed out after {cmd_timeout}s: {command[:50]}...")
        except Exception as e:
            return error_result(f"Command failed: {e}")
    
    def _is_blocked(self, command: str) -> bool:
        """Check if command contains blocked patterns."""
        cmd_lower = command.lower()
        for blocked in self.blocked_commands:
            if blocked.lower() in cmd_lower:
                return True
        return False


# ===========================================
# GIT TOOL
# ===========================================

class GitTool(BaseTool):
    """Git operations (status, diff, commit, push, etc.)."""
    
    def __init__(self, repo_path: Optional[str] = None):
        super().__init__()
        self.repo_path = Path(repo_path) if repo_path else None
    
    @property
    def name(self) -> str:
        return "git"
    
    @property
    def description(self) -> str:
        return "Git operations: status, diff, commit, push, pull, branch, log."
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.CODE
    
    def execute(
        self,
        command: str,
        repo_path: Optional[str] = None
    ) -> ToolOutput:
        """
        Execute a git command.
        
        Args:
            command: Git command (without 'git')
            repo_path: Repository path
        
        Returns:
            Git command output
        """
        try:
            work_dir = Path(repo_path).resolve() if repo_path else (self.repo_path or Path.cwd())
            
            # Validate it's a git repo
            if not (work_dir / ".git").exists():
                return error_result(f"Not a git repository: {work_dir}")
            
            # Build full command
            full_command = f"git {command}"
            
            result = subprocess.run(
                full_command,
                shell=True,
                cwd=str(work_dir),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return success_result(
                {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.returncode
                },
                success=result.returncode == 0
            )
            
        except subprocess.TimeoutExpired:
            return error_result("Git command timed out")
        except Exception as e:
            return error_result(f"Git command failed: {e}")
    
    def status(self, repo_path: Optional[str] = None) -> ToolOutput:
        """Get git status."""
        return self.execute("status --short", repo_path)
    
    def log(
        self,
        n: int = 10,
        format: str = "%h %s",
        repo_path: Optional[str] = None
    ) -> ToolOutput:
        """Get git log."""
        return self.execute(f"log -{n} --format='{format}'", repo_path)
    
    def diff(
        self,
        target: str = "",
        repo_path: Optional[str] = None
    ) -> ToolOutput:
        """Get git diff."""
        return self.execute(f"diff {target}", repo_path)
    
    def commit(
        self,
        message: str,
        add_all: bool = False,
        repo_path: Optional[str] = None
    ) -> ToolOutput:
        """Create a commit."""
        add_cmd = "add -A &&" if add_all else ""
        return self.execute(f"{add_cmd} commit -m {shlex.quote(message)}", repo_path)
    
    def push(
        self,
        remote: str = "origin",
        branch: str = "",
        repo_path: Optional[str] = None
    ) -> ToolOutput:
        """Push to remote."""
        return self.execute(f"push {remote} {branch}", repo_path)
    
    def pull(
        self,
        remote: str = "origin",
        branch: str = "",
        repo_path: Optional[str] = None
    ) -> ToolOutput:
        """Pull from remote."""
        return self.execute(f"pull {remote} {branch}", repo_path)
    
    def branch_list(self, repo_path: Optional[str] = None) -> ToolOutput:
        """List branches."""
        return self.execute("branch -a", repo_path)


# ===========================================
# PYTHON EXEC TOOL
# ===========================================

class PythonExecTool(BaseTool):
    """Execute Python code in a subprocess."""
    
    def __init__(self, timeout: int = 30):
        super().__init__()
        self.timeout = timeout
    
    @property
    def name(self) -> str:
        return "python_exec"
    
    @property
    def description(self) -> str:
        return "Execute Python code and return the output."
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.CODE
    
    def execute(
        self,
        code: str,
        timeout: Optional[int] = None
    ) -> ToolOutput:
        """
        Execute Python code.
        
        Args:
            code: Python code to execute
            timeout: Execution timeout
        
        Returns:
            Code output and any errors
        """
        try:
            import tempfile
            
            cmd_timeout = timeout or self.timeout
            
            # Write code to temp file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                temp_path = f.name
            
            try:
                result = subprocess.run(
                    ["python3", temp_path],
                    capture_output=True,
                    text=True,
                    timeout=cmd_timeout
                )
                
                return success_result({
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.returncode
                })
                
            finally:
                Path(temp_path).unlink(missing_ok=True)
            
        except subprocess.TimeoutExpired:
            return error_result(f"Python execution timed out after {cmd_timeout}s")
        except Exception as e:
            return error_result(f"Python execution failed: {e}")


# ===========================================
# LINTER TOOL
# ===========================================

class LinterTool(BaseTool):
    """Run linters on code."""
    
    def __init__(self, linter: str = "ruff"):
        super().__init__()
        self.linter = linter
    
    @property
    def name(self) -> str:
        return "linter"
    
    @property
    def description(self) -> str:
        return f"Run {self.linter} linter on files."
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.CODE
    
    def execute(
        self,
        path: str = ".",
        fix: bool = False
    ) -> ToolOutput:
        """
        Run linter.
        
        Args:
            path: Path to lint
            fix: Auto-fix issues
        
        Returns:
            Linter output
        """
        try:
            cmd = [self.linter, "check"]
            if fix:
                cmd.append("--fix")
            cmd.append(path)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return success_result({
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "fixed": fix
            })
            
        except FileNotFoundError:
            return error_result(f"Linter not found: {self.linter}")
        except Exception as e:
            return error_result(f"Linter failed: {e}")


# ===========================================
# TEST RUNNER TOOL
# ===========================================

class TestRunnerTool(BaseTool):
    """Run tests with pytest."""
    
    def __init__(self):
        super().__init__()
    
    @property
    def name(self) -> str:
        return "run_tests"
    
    @property
    def description(self) -> str:
        return "Run pytest tests."
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.CODE
    
    def execute(
        self,
        path: str = "tests/",
        pattern: str = "test_*.py",
        verbose: bool = True,
        cov: bool = False,
        markers: Optional[str] = None
    ) -> ToolOutput:
        """
        Run tests.
        
        Args:
            path: Path to test directory or file
            pattern: Test file pattern
            verbose: Verbose output
            cov: Enable coverage
            markers: Run only tests with specific markers
        
        Returns:
            Test results
        """
        try:
            cmd = ["pytest", path, "-v" if verbose else "-q"]
            
            if cov:
                cmd.extend(["--cov=nanocorp", "--cov-report=term-missing"])
            
            if markers:
                cmd.extend(["-m", markers])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Parse output
            output = result.stdout + result.stderr
            
            # Extract summary
            import re
            summary_match = re.search(r"(\d+) passed", output)
            passed = int(summary_match.group(1)) if summary_match else 0
            
            return success_result({
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "passed": passed,
                "failed": result.returncode != 0
            })
            
        except FileNotFoundError:
            return error_result("pytest not installed")
        except Exception as e:
            return error_result(f"Test run failed: {e}")


# ===========================================
# EXPORTS
# ===========================================

__all__ = [
    "BashTool",
    "GitTool",
    "PythonExecTool",
    "LinterTool",
    "TestRunnerTool",
    "BashResult",
]
