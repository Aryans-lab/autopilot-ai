"""
Free AI Provider System for NanoCorp

Allows using free/subscription-based AI services without API keys:
- Claude Code (browser login, no API key needed!)
- Codex (ChatGPT Plus subscription)
- Gemini CLI (free tier available)

These use the Agent Client Protocol (ACP) to delegate to local CLI agents.
"""
import os
import subprocess
import platform
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import json

# Try to import OpenHands SDK components
try:
    from openhands.sdk.agent.acp_agent import ACPAgent
    from openhands.sdk.conversation import Conversation
    OPENHANDS_AVAILABLE = True
except ImportError:
    OPENHANDS_AVAILABLE = False
    ACPAgent = None
    Conversation = None


class ProviderType(str, Enum):
    """Supported free AI providers"""
    CLAUDE_CODE = "claude-code"
    CODEX = "codex"
    GEMINI_CLI = "gemini-cli"
    # Fallback providers
    OLLAMA = "ollama"
    LM_STUDIO = "lm-studio"


@dataclass
class ProviderInfo:
    """Information about an AI provider"""
    name: str
    provider_type: ProviderType
    description: str
    requires_api_key: bool
    supports_browser_login: bool
    models: List[str]
    website: str
    free_tier: str


# Provider registry
PROVIDERS: Dict[str, ProviderInfo] = {
    "claude-code": ProviderInfo(
        name="Claude Code",
        provider_type=ProviderType.CLAUDE_CODE,
        description="Anthropic's CLI agent with Claude models. Supports browser login - NO API KEY NEEDED!",
        requires_api_key=False,
        supports_browser_login=True,
        models=["claude-opus-4", "claude-sonnet-4", "claude-haiku"],
        website="https://docs.anthropic.com/en/docs/claude-code",
        free_tier="FREE with Anthropic account (browser login)"
    ),
    "codex": ProviderInfo(
        name="Codex (ChatGPT)",
        provider_type=ProviderType.CODEX,
        description="OpenAI's agent using ChatGPT. Works with ChatGPT Plus subscription!",
        requires_api_key=False,
        supports_browser_login=True,
        models=["gpt-5", "gpt-4o"],
        website="https://openai.com/index/introducing-codex",
        free_tier="Included with ChatGPT Plus ($20/month)"
    ),
    "gemini-cli": ProviderInfo(
        name="Gemini CLI",
        provider_type=ProviderType.GEMINI_CLI,
        description="Google's CLI agent with Gemini models. Has free tier!",
        requires_api_key=False,
        supports_browser_login=True,
        models=["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0"],
        website="https://github.com/google/gemini-cli",
        free_tier="FREE with Google account"
    ),
    "ollama": ProviderInfo(
        name="Ollama",
        provider_type=ProviderType.OLLAMA,
        description="Run open-source models locally. Completely free!",
        requires_api_key=False,
        supports_browser_login=False,
        models=["llama3", "mistral", "codellama", "qwen2"],
        website="https://ollama.com",
        free_tier="FREE (runs locally)"
    ),
}


class FreeProvider:
    """
    Wrapper for free AI providers using ACP protocol.
    
    Usage:
        provider = FreeProvider("claude-code")
        result = provider.chat("Hello!")
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
        
        if not OPENHANDS_AVAILABLE:
            raise ImportError(
                "OpenHands SDK not installed. Run: pip install openhands-sdk"
            )
        
        # Initialize ACP agent
        self._init_agent()
    
    def _init_agent(self):
        """Initialize the ACP agent based on provider"""
        if self.provider == "claude-code":
            self._init_claude_code()
        elif self.provider == "codex":
            self._init_codex()
        elif self.provider == "gemini-cli":
            self._init_gemini_cli()
        elif self.provider == "ollama":
            self._init_ollama()
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def _init_claude_code(self):
        """Initialize Claude Code agent"""
        self.agent = ACPAgent(
            acp_server="claude-code",
            acp_model=self.model,
        )
        self.conversation = Conversation(
            agent=self.agent,
            workspace=self.workspace
        )
    
    def _init_codex(self):
        """Initialize Codex agent"""
        self.agent = ACPAgent(
            acp_server="codex",
            acp_model=self.model,
        )
        self.conversation = Conversation(
            agent=self.agent,
            workspace=self.workspace
        )
    
    def _init_gemini_cli(self):
        """Initialize Gemini CLI agent"""
        self.agent = ACPAgent(
            acp_server="gemini-cli",
            acp_model=self.model or "auto",
        )
        self.conversation = Conversation(
            agent=self.agent,
            workspace=self.workspace
        )
    
    def _init_ollama(self):
        """Initialize Ollama agent (local)"""
        # Ollama uses a local server
        self.agent = ACPAgent(
            acp_server="custom",
            acp_command=["ollama", "run", self.model or "llama3"],
        )
        self.conversation = Conversation(
            agent=self.agent,
            workspace=self.workspace
        )
    
    def chat(self, message: str, max_steps: int = 10) -> str:
        """
        Send a message and get response.
        
        Args:
            message: The message to send
            max_steps: Maximum agent steps (for complex tasks)
        """
        self.conversation.send_message(message)
        
        # Run the conversation
        for _ in range(max_steps):
            self.conversation.step()
            if self.conversation.is_done():
                break
        
        # Get final response
        events = list(self.conversation.get_events())
        if events:
            last_event = events[-1]
            if hasattr(last_event, 'content'):
                return str(last_event.content)
        
        return "No response"
    
    def run_task(self, task: str) -> Dict[str, Any]:
        """
        Run a complex task with the agent.
        
        Args:
            task: The task description
        """
        self.conversation.send_message(task)
        
        results = []
        for _ in range(50):  # Max steps
            self.conversation.step()
            if self.conversation.is_done():
                break
            
            # Collect observations
            for event in self.conversation.get_events():
                if hasattr(event, 'content'):
                    results.append(str(event.content))
        
        return {
            "success": True,
            "provider": self.provider,
            "task": task,
            "steps": len(results),
            "output": "\n".join(results[-5:])  # Last 5 messages
        }


class ProviderManager:
    """
    Manages multiple AI providers with automatic fallback.
    
    Usage:
        manager = ProviderManager()
        manager.set_primary("claude-code")
        manager.add_fallback("gemini-cli")
        
        # Use with automatic fallback
        result = manager.chat("Hello!")
    """
    
    def __init__(self):
        self.providers: Dict[str, FreeProvider] = {}
        self.primary: Optional[str] = None
        self.fallbacks: List[str] = []
        self.workspace: Optional[str] = None
    
    def add_provider(
        self,
        name: str,
        provider_type: str = "claude-code",
        model: Optional[str] = None
    ) -> bool:
        """
        Add a provider.
        
        Returns True if successful, False otherwise.
        """
        try:
            self.providers[name] = FreeProvider(
                provider=provider_type,
                model=model,
                workspace=self.workspace
            )
            return True
        except Exception as e:
            print(f"Failed to add provider {name}: {e}")
            return False
    
    def set_primary(self, name: str):
        """Set the primary provider"""
        self.primary = name
    
    def add_fallback(self, name: str):
        """Add a fallback provider"""
        if name not in self.fallbacks:
            self.fallbacks.append(name)
    
    def chat(self, message: str) -> Optional[str]:
        """Chat with automatic fallback"""
        # Try primary first
        if self.primary and self.primary in self.providers:
            try:
                return self.providers[self.primary].chat(message)
            except Exception as e:
                print(f"Primary provider failed: {e}")
        
        # Try fallbacks
        for name in self.fallbacks:
            if name in self.providers:
                try:
                    return self.providers[name].chat(message)
                except Exception as e:
                    print(f"Fallback {name} failed: {e}")
        
        return None
    
    def detect_available_providers(self) -> List[str]:
        """
        Detect which providers are available on this system.
        """
        available = []
        
        # Check for Claude Code
        if self._check_command("claude"):
            available.append("claude-code")
        
        # Check for Codex
        if self._check_command("codex") or self._check_npx("codex"):
            available.append("codex")
        
        # Check for Gemini CLI
        if self._check_command("gemini") or self._check_npx("gemini"):
            available.append("gemini-cli")
        
        # Check for Ollama
        if self._check_command("ollama"):
            available.append("ollama")
        
        return available
    
    def _check_command(self, cmd: str) -> bool:
        """Check if a command exists"""
        try:
            result = subprocess.run(
                ["which", cmd] if platform.system() != "Windows" else ["where", cmd],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_npx(self, pkg: str) -> bool:
        """Check if an npx package is available"""
        try:
            result = subprocess.run(
                ["npx", "-y", f"@{pkg}/cli" if pkg == "gemini" else f"@google/gemini-cli", "--version"],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False


# Auto-setup function
def setup_free_provider(
    provider: str = "auto",
    model: Optional[str] = None
) -> FreeProvider:
    """
    Automatically set up the best available free provider.
    
    Priority:
    1. Claude Code (best quality, free browser login)
    2. Gemini CLI (good quality, free tier)
    3. Codex (requires ChatGPT Plus)
    4. Ollama (local, completely free)
    
    Usage:
        provider = setup_free_provider()
        provider.chat("Hello!")
    """
    manager = ProviderManager()
    available = manager.detect_available_providers()
    
    if not available:
        print("No CLI agents detected. Installing Claude Code...")
        _install_claude_code()
        available = ["claude-code"]
    
    # Use specified provider or best available
    if provider == "auto":
        provider = available[0] if available else "claude-code"
    
    print(f"Setting up {provider}...")
    
    try:
        return FreeProvider(provider=provider, model=model)
    except Exception as e:
        print(f"Failed to setup {provider}: {e}")
        print("Trying next available provider...")
        for p in available:
            if p != provider:
                try:
                    return FreeProvider(provider=p, model=model)
                except:
                    continue
        
        raise RuntimeError("No free providers available. Please install one.")


def _install_claude_code():
    """Install Claude Code via npm"""
    try:
        print("Installing @agentclientprotocol/claude-agent-acp...")
        subprocess.run(
            ["npm", "install", "-g", "@agentclientprotocol/claude-agent-acp"],
            check=True,
            timeout=60
        )
        print("Claude Code installed!")
    except Exception as e:
        print(f"Failed to install: {e}")
        print("Try manually: npm install -g @agentclientprotocol/claude-agent-acp")


def list_free_providers() -> List[Dict[str, Any]]:
    """List all available free providers with info"""
    return [
        {
            "id": key,
            "name": info.name,
            "description": info.description,
            "free_tier": info.free_tier,
            "website": info.website
        }
        for key, info in PROVIDERS.items()
    ]
