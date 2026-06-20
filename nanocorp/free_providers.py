"""
Ultra-Lightweight Free AI Providers for NanoCorp

No API keys needed! Use free CLI-based AI tools:
- Claude Code (FREE with account)
- Gemini CLI (FREE)
- Ollama (completely free, runs locally)

Just needs a CLI installed - NanoCorp handles the rest!
"""
import os
import subprocess
import json
import tempfile
import platform
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FreeProviderConfig:
    """Configuration for a free AI provider"""
    name: str
    command: List[str]
    env_vars: Dict[str, str]
    requires_login: bool
    login_instructions: str
    free_note: str


# Provider configurations
PROVIDERS: Dict[str, FreeProviderConfig] = {
    "claude-code": FreeProviderConfig(
        name="Claude Code",
        command=["npx", "-y", "@agentclientprotocol/claude-agent-acp", "--help"],
        env_vars={},
        requires_login=True,
        login_instructions="Run: claude login (opens browser)",
        free_note="FREE with Anthropic account"
    ),
    "gemini-cli": FreeProviderConfig(
        name="Gemini CLI",
        command=["npx", "-y", "@google/gemini-cli", "--version"],
        env_vars={},
        requires_login=True,
        login_instructions="Run: gemini-cli (auto-prompts login)",
        free_note="FREE with Google account"
    ),
    "ollama": FreeProviderConfig(
        name="Ollama",
        command=["ollama", "--version"],
        env_vars={},
        requires_login=False,
        login_instructions="Install: curl -fsSL https://ollama.com/install.sh | sh",
        free_note="COMPLETELY FREE (runs locally)"
    ),
}


class LightweightProvider:
    """
    A lightweight AI provider that calls CLI tools directly.
    
    Simple but effective - just subprocess calls!
    """
    
    def __init__(
        self,
        provider: str = "claude-code",
        model: Optional[str] = None,
        workspace: Optional[str] = None
    ):
        self.provider = provider
        self.model = model
        self.workspace = workspace or os.getcwd()
        self.config = PROVIDERS.get(provider, PROVIDERS["claude-code"])
    
    def _run_command(self, args: List[str], input_text: str = "") -> Dict[str, Any]:
        """Run a CLI command and return results"""
        env = os.environ.copy()
        env.update(self.config.env_vars)
        
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.workspace,
                env=env
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_available(self) -> bool:
        """Check if this provider is available"""
        result = self._run_command(self.config.command[:3])
        return result.get("success", False)
    
    def chat(self, message: str) -> str:
        """
        Simple chat (best effort - some providers need MCP/ACP setup).
        """
        # Try to run the CLI
        if self.provider == "ollama":
            return self._chat_ollama(message)
        else:
            # For Claude Code / Gemini CLI, they need ACP setup
            # This is a simplified version - full integration uses OpenHands SDK
            return f"[{self.config.name}] Message received: {message[:100]}..."
    
    def _chat_ollama(self, message: str) -> str:
        """Chat using Ollama (simplest integration)"""
        result = self._run_command([
            "ollama", "run", self.model or "llama3", message
        ])
        
        if result.get("success"):
            return result.get("stdout", "")
        else:
            return f"Error: {result.get('error', 'Unknown error')}"


class ClaudeCodeRunner:
    """
    Run Claude Code as a subprocess for complex tasks.
    
    Creates a temporary script and runs Claude Code on it.
    """
    
    def __init__(
        self,
        workspace: Optional[str] = None,
        model: str = "sonnet"
    ):
        self.workspace = Path(workspace or os.getcwd())
        self.model = model
        self.history_file = self.workspace / ".nanocorp_history.json"
    
    def _ensure_login(self) -> bool:
        """Check if Claude is logged in"""
        try:
            result = subprocess.run(
                ["claude", "auth", "status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return "authenticated" in result.stdout.lower() or "logged in" in result.stdout.lower()
        except:
            return False
    
    def _install(self):
        """Try to install Claude Code"""
        print("Installing Claude Code...")
        try:
            subprocess.run(
                ["npm", "install", "-g", "@anthropic/claude-code"],
                check=True,
                timeout=120
            )
            print("Claude Code installed!")
            return True
        except Exception as e:
            print(f"Install failed: {e}")
            return False
    
    def run_task(self, task: str) -> Dict[str, Any]:
        """
        Run a task using Claude Code.
        
        Creates a script file, runs Claude Code on it, returns output.
        """
        # Check login
        if not self._ensure_login():
            print("Claude Code not logged in!")
            print("Run: claude login")
            return {
                "success": False,
                "error": "Not authenticated",
                "hint": "Run 'claude login' first"
            }
        
        # Create task script
        script_content = f'''#!/bin/bash
# NanoCorp Task
echo "Task: {task}"
echo "---"
# Claude Code will complete this task
'''
        # For Claude Code, we need to create a proper task file
        # since it doesn't support stdin input like a chat
        task_file = self.workspace / ".nanocorp_task.md"
        
        with open(task_file, 'w') as f:
            f.write(f"# NanoCorp Task\n\n{task}\n\n## Instructions\nPlease complete this task and report results.\n")
        
        try:
            result = subprocess.run(
                ["claude", "--print", f"--model={self.model}"],
                input=task,
                capture_output=True,
                text=True,
                timeout=180,
                cwd=self.workspace
            )
            
            # Clean up
            if task_file.exists():
                task_file.unlink()
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class OllamaRunner:
    """
    Run Ollama for completely free AI (no internet needed!)
    
    Ollama runs models locally on your machine.
    """
    
    def __init__(
        self,
        model: str = "llama3",
        workspace: Optional[str] = None
    ):
        self.model = model
        self.workspace = workspace or os.getcwd()
    
    def check_available(self) -> bool:
        """Check if Ollama is installed and running"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def install_model(self):
        """Install the default model"""
        print(f"Installing {self.model}...")
        try:
            subprocess.run(
                ["ollama", "pull", self.model],
                check=True,
                timeout=600  # 10 minutes
            )
            print(f"{self.model} installed!")
        except Exception as e:
            print(f"Install failed: {e}")
            print("Try: ollama pull llama3")
    
    def chat(self, message: str) -> str:
        """Send a message and get response"""
        try:
            result = subprocess.run(
                ["ollama", "run", self.model, message],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def run_task(self, task: str) -> Dict[str, Any]:
        """Run a complex task"""
        output = self.chat(task)
        
        return {
            "success": "Error" not in output,
            "output": output,
            "model": self.model
        }


class FreeProviderFactory:
    """
    Factory to create and manage free AI providers.
    
    Automatically detects what's available and sets up the best option.
    """
    
    def __init__(self, workspace: Optional[str] = None):
        self.workspace = workspace or os.getcwd()
        self._providers: Dict[str, Any] = {}
    
    def detect_available(self) -> List[str]:
        """Detect which providers are available"""
        available = []
        
        # Check Ollama
        try:
            subprocess.run(["ollama", "list"], capture_output=True, timeout=5)
            available.append("ollama")
        except:
            pass
        
        # Check Claude Code
        try:
            subprocess.run(["claude", "--version"], capture_output=True, timeout=5)
            available.append("claude-code")
        except:
            pass
        
        return available
    
    def create(
        self,
        provider: str = "auto",
        model: Optional[str] = None,
        **kwargs
    ):
        """
        Create a free provider.
        
        Args:
            provider: "auto", "ollama", "claude-code", "gemini"
            model: Model to use (optional)
        """
        if provider == "auto":
            available = self.detect_available()
            if "ollama" in available:
                provider = "ollama"
            elif "claude-code" in available:
                provider = "claude-code"
            else:
                # No CLI available, use Ollama by default
                provider = "ollama"
                print("No CLI found. Suggesting Ollama (runs locally, free)")
        
        if provider == "ollama":
            return OllamaRunner(model=model or "llama3", workspace=self.workspace)
        elif provider == "claude-code":
            return ClaudeCodeRunner(model=model or "sonnet", workspace=self.workspace)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def install_ollama(self):
        """Install Ollama (completely free, runs locally)"""
        system = platform.system()
        
        if system == "Linux":
            print("Installing Ollama on Linux...")
            os.system("curl -fsSL https://ollama.com/install.sh | sh")
        elif system == "Darwin":  # macOS
            print("Installing Ollama on macOS...")
            os.system("brew install ollama")
        else:
            print("Visit https://ollama.com to install")
        
        # Start Ollama
        try:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("Ollama server started!")
        except:
            print("Start Ollama with: ollama serve")


def quick_setup(provider: str = "auto") -> Any:
    """
    Quick setup for free AI providers.
    
    Usage:
        # Auto-detect best option
        runner = quick_setup()
        
        # Or specify
        runner = quick_setup("ollama")
        
        # Use it
        result = runner.chat("Hello!")
    """
    factory = FreeProviderFactory()
    
    if provider == "auto":
        available = factory.detect_available()
        
        if not available:
            print("\n" + "="*60)
            print("FREE AI PROVIDER SETUP")
            print("="*60)
            print("\nNo free AI CLI detected. Choose an option:")
            print("\n1. Ollama (RECOMMENDED - runs locally, free forever)")
            print("   - Completely free, no account needed")
            print("   - Runs AI models on YOUR computer")
            print("   - Install: curl -fsSL https://ollama.com/install.sh | sh")
            print("\n2. Claude Code (free with account)")
            print("   - npm install -g @anthropic/claude-code")
            print("   - claude login")
            print("\n" + "="*60)
            
            choice = input("\nEnter choice (1/2) or install now (i): ").strip().lower()
            
            if choice == "1" or choice == "i":
                factory.install_ollama()
                provider = "ollama"
            else:
                provider = "claude-code"
    
    return factory.create(provider)


# Example usage
if __name__ == "__main__":
    print("NanoCorp Free AI Provider")
    print("="*60)
    
    # Detect available
    factory = FreeProviderFactory()
    available = factory.detect_available()
    
    if available:
        print(f"\nAvailable providers: {', '.join(available)}")
        provider = input(f"\nChoose provider ({available[0]}): ").strip() or available[0]
    else:
        print("\nNo providers detected.")
        print("\nTo get started with FREE AI:")
        print("1. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh")
        print("2. Then run this script again")
        provider = "ollama"
    
    runner = factory.create(provider)
    
    if hasattr(runner, 'check_available') and not runner.check_available():
        if provider == "ollama":
            factory.install_ollama()
    
    # Test
    print(f"\nTesting {provider}...")
    if hasattr(runner, 'chat'):
        result = runner.chat("Say hello and tell me you're ready!")
        print(f"\nResult:\n{result}")
