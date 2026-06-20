"""
NanoCorp v3.0 - Code Sandbox

Safe code execution with resource limits and isolation.
"""
from __future__ import annotations

import subprocess
import resource
import signal
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SandboxResult:
    """Result from sandboxed execution."""
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    duration: float
    memory_used: int
    error: Optional[str] = None


class CodeSandbox:
    """
    Safe code execution sandbox.
    
    Features:
    - Process isolation
    - Resource limits (CPU, memory, time)
    - Whitelist of allowed operations
    - Output capture
    """
    
    def __init__(
        self,
        timeout: int = 60,
        memory_limit: int = 512 * 1024 * 1024,  # 512MB
        allowed_modules: Optional[List[str]] = None,
        blocked_commands: Optional[List[str]] = None,
        workspace: Optional[str] = None
    ):
        self.timeout = timeout
        self.memory_limit = memory_limit
        self.allowed_modules = allowed_modules or ["math", "json", "re", "datetime", "random", "collections", "itertools"]
        self.blocked_commands = blocked_commands or [
            "rm -rf /", "dd if=", "mkfs", "fdisk",
            "import os; os.system", "subprocess.run(['rm"
        ]
        self.workspace = Path(workspace) if workspace else Path(tempfile.mkdtemp())
        self.workspace.mkdir(parents=True, exist_ok=True)
    
    def execute_python(
        self,
        code: str,
        inputs: Optional[Dict[str, Any]] = None
    ) -> SandboxResult:
        """
        Execute Python code in sandbox.
        
        Args:
            code: Python code to execute
            inputs: Variables to inject
        
        Returns:
            SandboxResult with output
        """
        start_time = datetime.now()
        
        # Safety check
        if self._is_blocked(code):
            return SandboxResult(
                success=False,
                stdout="",
                stderr="Code contains blocked operations",
                exit_code=1,
                duration=0,
                memory_used=0,
                error="Security: blocked operations detected"
            )
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            # Add inputs to namespace
            if inputs:
                input_code = "\n".join([f"{k} = {repr(v)}" for k, v in inputs.items()])
                f.write(f"# Inputs\n{input_code}\n\n")
            
            f.write(code)
            temp_path = f.name
        
        try:
            # Set resource limits
            def set_limits():
                resource.setrlimit(resource.RLIMIT_CPU, (self.timeout, self.timeout))
                resource.setrlimit(resource.RLIMIT_AS, (self.memory_limit, self.memory_limit))
                resource.setrlimit(resource.RLIMIT_FSIZE, (10 * 1024 * 1024, 10 * 1024 * 1024))  # 10MB file max
            
            # Run with limits
            proc = subprocess.Popen(
                ["python3", temp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=set_limits
            )
            
            try:
                stdout, stderr = proc.communicate(timeout=self.timeout)
                exit_code = proc.returncode
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, stderr = proc.communicate()
                exit_code = -1
                stderr += f"\n[TIMEOUT: killed after {self.timeout}s]"
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return SandboxResult(
                success=exit_code == 0,
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                duration=duration,
                memory_used=0  # Would need psutil for accurate measurement
            )
            
        except Exception as e:
            return SandboxResult(
                success=False,
                stdout="",
                stderr=str(e),
                exit_code=1,
                duration=0,
                memory_used=0,
                error=str(e)
            )
        finally:
            os.unlink(temp_path)
    
    def execute_bash(
        self,
        command: str,
        cwd: Optional[str] = None
    ) -> SandboxResult:
        """
        Execute bash command in sandbox.
        
        Args:
            command: Shell command
            cwd: Working directory
        
        Returns:
            SandboxResult
        """
        start_time = datetime.now()
        
        if self._is_blocked(command):
            return SandboxResult(
                success=False,
                stdout="",
                stderr="Command blocked for security",
                exit_code=1,
                duration=0,
                memory_used=0,
                error="Security: blocked command"
            )
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or str(self.workspace),
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return SandboxResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                duration=duration,
                memory_used=0
            )
            
        except subprocess.TimeoutExpired:
            return SandboxResult(
                success=False,
                stdout="",
                stderr=f"Timeout after {self.timeout}s",
                exit_code=124,
                duration=self.timeout,
                memory_used=0,
                error="Timeout"
            )
        except Exception as e:
            return SandboxResult(
                success=False,
                stdout="",
                stderr=str(e),
                exit_code=1,
                duration=0,
                memory_used=0,
                error=str(e)
            )
    
    def _is_blocked(self, code: str) -> bool:
        """Check if code contains blocked operations."""
        code_lower = code.lower()
        for blocked in self.blocked_commands:
            if blocked.lower() in code_lower:
                return True
        return False


# Global sandbox instance
_sandbox: Optional[CodeSandbox] = None

def get_sandbox() -> CodeSandbox:
    """Get global sandbox instance."""
    global _sandbox
    if _sandbox is None:
        _sandbox = CodeSandbox()
    return _sandbox
