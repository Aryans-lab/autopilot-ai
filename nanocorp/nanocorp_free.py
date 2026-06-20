"""
NanoCorp Free - The completely FREE AI Startup System

No API key needed! Uses subscription-based AI CLI tools:
- Codex (ChatGPT Plus subscription - $20/month)
- Claude Code (Anthropic account - FREE!)
- Ollama (completely free, runs locally!)

Just install one of these and NanoCorp runs!
"""
import os
import subprocess
import platform
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class SystemStatus:
    """Overall system status"""
    is_running: bool = False
    tasks_completed: int = 0
    goals_achieved: int = 0
    uptime: float = 0.0
    ai_provider: str = "none"


class FreeAI:
    """
    Free AI wrapper using CLI tools with subscription accounts!
    
    Priority: Codex (ChatGPT Plus) > Claude Code > Ollama
    """
    
    def __init__(self, provider: str = "auto"):
        self.provider = self._detect_best_provider() or provider
        self.model = self._get_default_model()
    
    def _detect_best_provider(self) -> Optional[str]:
        """Detect the best available provider (priority: Claude ACP > Codex ACP > Ollama)"""
        # Priority 1: Claude Agent ACP (Anthropic - uses FREE Claude account!)
        # This uses the ACP protocol that OpenHands SDK supports
        if self._check_npx_package("@agentclientprotocol/claude-agent-acp"):
            return "claude-acp"
        
        # Priority 2: Codex ACP (ChatGPT Plus - $20/month)
        # This uses the ACP protocol with Codex
        if self._check_npx_package("@zed-industries/codex-acp"):
            return "codex-acp"
        
        # Priority 3: Claude Code CLI (if installed directly)
        if self._check_command("claude"):
            return "claude-cli"
        
        # Priority 4: Ollama (completely free, local)
        if self._check_command("ollama"):
            return "ollama"
        
        return None
    
    def _check_command(self, cmd: str) -> bool:
        """Check if command exists"""
        try:
            result = subprocess.run(
                ["which", cmd],
                capture_output=True, timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_npx_package(self, package: str) -> bool:
        """Check if npx package is available"""
        try:
            result = subprocess.run(
                ["npx", "-y", package, "--version"],
                capture_output=True, timeout=20
            )
            return result.returncode == 0
        except:
            return False
    
    def _get_default_model(self) -> str:
        """Get default model for provider"""
        models = {
            "claude-acp": "sonnet",     # Claude Sonnet (good quality)
            "codex-acp": "gpt-4o",      # GPT-4o
            "claude-cli": "haiku",       # Claude Haiku
            "ollama": "llama3"           # Local model
        }
        return models.get(self.provider, "sonnet")
    
    def chat(self, message: str) -> str:
        """Send message to AI"""
        if self.provider == "claude-acp":
            return self._chat_claude_acp(message)
        elif self.provider == "codex-acp":
            return self._chat_codex_acp(message)
        elif self.provider == "claude-cli":
            return self._chat_claude_cli(message)
        elif self.provider == "ollama":
            return self._chat_ollama(message)
        else:
            return "[No AI available. Install Claude ACP: npx -y @agentclientprotocol/claude-agent-acp]"
    
    def _chat_claude_acp(self, message: str) -> str:
        """Chat using Claude Agent ACP (Anthropic - FREE!)"""
        try:
            result = subprocess.run(
                ["npx", "-y", "@agentclientprotocol/claude-agent-acp", "--print", 
                 "--model", self.model, "--system-prompt", "You are a helpful business AI assistant."],
                input=message,
                capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _chat_codex_acp(self, message: str) -> str:
        """Chat using Codex ACP (ChatGPT Plus - $20/month)"""
        try:
            result = subprocess.run(
                ["npx", "-y", "@zed-industries/codex-acp", "--print"],
                input=message,
                capture_output=True, text=True, timeout=120,
                env={**os.environ, "CODEX_MODEL": self.model}
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _chat_claude_cli(self, message: str) -> str:
        """Chat using Claude Code CLI (if installed directly)"""
        try:
            result = subprocess.run(
                ["claude", "--print", "--model=haiku"],
                input=message,
                capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _chat_ollama(self, message: str) -> str:
        """Chat using Ollama (completely free, local)"""
        try:
            result = subprocess.run(
                ["ollama", "run", self.model, message],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def is_available(self) -> bool:
        """Check if AI is available"""
        return self.provider is not None
    
    def get_info(self) -> Dict[str, str]:
        """Get provider info"""
        info = {
            "claude-acp": {
                "name": "Claude Agent ACP",
                "cost": "FREE (Anthropic account)",
                "setup": "npx -y @agentclientprotocol/claude-agent-acp && claude login",
                "models": "Claude Opus, Sonnet, Haiku"
            },
            "codex-acp": {
                "name": "Codex ACP (ChatGPT Plus)",
                "cost": "$20/month (ChatGPT Plus)",
                "setup": "npx -y @zed-industries/codex-acp",
                "models": "GPT-4o, GPT-5"
            },
            "claude-cli": {
                "name": "Claude Code CLI",
                "cost": "FREE (Anthropic account)",
                "setup": "npm install -g @anthropic/claude-code && claude login",
                "models": "Claude Opus, Sonnet, Haiku"
            },
            "ollama": {
                "name": "Ollama",
                "cost": "FREE (runs locally)",
                "setup": "curl -fsSL https://ollama.com/install.sh | sh",
                "models": "Llama3, Mistral, Codellama"
            }
        }
        return info.get(self.provider, {})


class Worker:
    """A simple worker using free AI"""
    
    def __init__(self, name: str, ai: FreeAI, workspace: Path):
        self.name = name
        self.ai = ai
        self.workspace = workspace
        self.task_history = []
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task"""
        prompt = self._build_prompt(task)
        output = self.ai.chat(prompt)
        
        result = {
            "success": True,
            "worker": self.name,
            "task": task.get("title", "Untitled"),
            "output": output,
            "timestamp": datetime.now().isoformat()
        }
        
        self.task_history.append(result)
        self._save_output(task, output)
        
        return result
    
    def _build_prompt(self, task: Dict[str, Any]) -> str:
        """Build prompt for task"""
        role_prompts = {
            "WebDev": "You are a web developer. Create websites, landing pages, and web applications.",
            "Marketing": "You are a marketing expert. Create marketing strategies, campaigns, and content.",
            "Content": "You are a content writer. Create blog posts, articles, and copy.",
            "SocialMedia": "You are a social media manager. Create engaging social posts and strategies.",
            "Email": "You are an email marketing specialist. Create email campaigns and sequences.",
            "Document": "You are a business writer. Create proposals, plans, and reports.",
            "Researcher": "You are a market researcher. Analyze markets, competitors, and trends.",
            "Networker": "You are a networking expert. Create outreach strategies and partnerships."
        }
        
        role = role_prompts.get(self.name, "You are a helpful assistant.")
        
        prompt = f"""{role}

Task: {task.get('title', 'No title')}
Description: {task.get('description', 'No description')}

"""
        
        if task.get('context'):
            prompt += f"Context: {task['context']}\n"
        
        prompt += "\nPlease complete this task thoroughly and provide your output."
        
        return prompt
    
    def _save_output(self, task: Dict, output: str):
        """Save output to workspace"""
        category = task.get('category', 'general').lower().replace(' ', '_')
        output_dir = self.workspace / category
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{task.get('title', 'task').lower().replace(' ', '-')}.md"
        filepath = output_dir / filename
        
        content = f"""# {task.get('title', 'Task Output')}

**Worker:** {self.name}
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Category:** {task.get('category', 'general')}

---

## Task Description

{task.get('description', 'No description')}

---

## Output

{output}
"""
        
        with open(filepath, 'w') as f:
            f.write(content)


class NanoCorpFree:
    """
    NanoCorp Free - The completely FREE AI Startup System
    
    No API key needed! Uses free CLI-based AI tools.
    
    Usage:
        nano = NanoCorpFree()
        nano.set_mission("Build an AI startup")
        nano.create_task("Create landing page", worker="WebDev")
        nano.run()
    """
    
    def __init__(
        self,
        workspace_path: str = None,
        provider: str = "auto"
    ):
        # Workspace
        if workspace_path:
            self.workspace = Path(workspace_path)
        else:
            self.workspace = Path.cwd() / "nanocorp_workspace"
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        # Initialize Free AI
        self.ai = FreeAI(provider=provider)
        
        # Show status
        print("\n" + "="*60)
        print("NanoCorp Free - AI Startup System")
        print("="*60)
        
        if self.ai.is_available():
            print(f"\nAI Provider: {self.ai.provider.upper()}")
            print(f"Model: {self.ai.model}")
            print("Cost: $0.00 (completely free!)")
        else:
            print("\n[WARNING] No free AI detected!")
            print("\nTo get started FREE, install Ollama:")
            print("  curl -fsSL https://ollama.com/install.sh | sh")
            print("\nThen run this script again!")
        print("="*60 + "\n")
        
        # Workers
        self.workers: Dict[str, Worker] = {}
        self._init_workers()
        
        # Tasks
        self.tasks: List[Dict[str, Any]] = []
        self.completed_tasks: List[Dict] = []
        
        # Goals
        self.goals: List[Dict] = []
        
        # State
        self.company = {
            "name": "NanoCorp",
            "mission": "",
            "vision": ""
        }
        
        self.is_running = False
        self.start_time: Optional[datetime] = None
    
    def _init_workers(self):
        """Initialize all workers"""
        worker_names = [
            "WebDev", "Marketing", "Content", "SocialMedia",
            "Email", "Document", "Researcher", "Networker"
        ]
        
        for name in worker_names:
            self.workers[name] = Worker(name, self.ai, self.workspace)
    
    # --- Company Setup ---
    
    def set_mission(self, mission: str, vision: str = ""):
        """Set company mission"""
        self.company["mission"] = mission
        self.company["vision"] = vision
        print(f"Mission set: {mission[:50]}...")
    
    # --- Task Management ---
    
    def create_task(
        self,
        title: str,
        description: str = "",
        worker: str = "Content",
        category: str = "general",
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create a new task"""
        task = {
            "id": f"task_{len(self.tasks)}",
            "title": title,
            "description": description,
            "worker": worker,
            "category": category,
            "context": context or {},
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        self.tasks.append(task)
        return task
    
    def create_website(self, name: str, website_type: str = "landing", **kwargs):
        """Create a website task"""
        descriptions = {
            "landing": f"Create a high-converting landing page for {name}",
            "business": f"Create a professional business website for {name}",
            "portfolio": f"Create a portfolio website for {name}"
        }
        
        return self.create_task(
            title=f"Create {name} {website_type} website",
            description=descriptions.get(website_type, descriptions["landing"]),
            worker="WebDev",
            category="web_dev",
            context=kwargs
        )
    
    def create_campaign(self, name: str, channels: List[str] = None, **kwargs):
        """Create a marketing campaign"""
        channels = channels or ["social", "email"]
        return self.create_task(
            title=f"Create marketing campaign for {name}",
            description=f"Create a multi-channel marketing campaign for {name}",
            worker="Marketing",
            category="marketing",
            context={"channels": channels, **kwargs}
        )
    
    def research(self, topic: str, research_type: str = "market", **kwargs):
        """Create a research task"""
        return self.create_task(
            title=f"{research_type.title()} research: {topic}",
            description=f"Conduct {research_type} research on {topic}",
            worker="Researcher",
            category="research",
            context=kwargs
        )
    
    # --- Goal Management ---
    
    def set_goal(self, title: str, description: str = "") -> Dict:
        """Set a goal"""
        goal = {
            "id": f"goal_{len(self.goals)}",
            "title": title,
            "description": description,
            "progress": 0.0,
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        
        self.goals.append(goal)
        return goal
    
    def decompose_goal(self, goal_id: str, sub_goals: List[str]) -> List[Dict]:
        """Break down goal into tasks"""
        goal = next((g for g in self.goals if g["id"] == goal_id), None)
        if not goal:
            return []
        
        tasks = []
        for i, sub in enumerate(sub_goals):
            task = self.create_task(
                title=sub,
                description=f"Sub-goal {i+1} of: {goal['title']}",
                worker=["Content", "Marketing", "WebDev", "Researcher"][i % 4]
            )
            tasks.append(task)
        
        return tasks
    
    # --- Execution ---
    
    def run(self, max_tasks: int = 10):
        """
        Run pending tasks
        
        Args:
            max_tasks: Maximum number of tasks to execute
        """
        if not self.ai.is_available():
            print("[ERROR] No AI available. Cannot execute tasks.")
            return
        
        pending = [t for t in self.tasks if t["status"] == "pending"][:max_tasks]
        
        if not pending:
            print("No pending tasks!")
            return
        
        print(f"\nExecuting {len(pending)} tasks...\n")
        
        for task in pending:
            print(f"[{task['worker']}] {task['title'][:50]}...")
            
            worker = self.workers.get(task["worker"])
            if worker:
                result = worker.execute(task)
                task["status"] = "completed"
                task["result"] = result
                self.completed_tasks.append(task)
                print(f"  -> Done!")
            else:
                print(f"  -> Worker not found!")
        
        print(f"\nCompleted {len(self.completed_tasks)} tasks!")
    
    def autopilot(self, duration_seconds: float = 60):
        """
        Run in autopilot mode
        
        Args:
            duration_seconds: How long to run
        """
        if not self.ai.is_available():
            print("[ERROR] No AI available. Cannot run autopilot.")
            return
        
        self.is_running = True
        self.start_time = datetime.now()
        
        print("\n" + "="*60)
        print("AUTOPILOT MODE ENGAGED")
        print("="*60)
        print(f"Duration: {duration_seconds} seconds")
        print("Press Ctrl+C to stop\n")
        
        start = time.time()
        cycle = 0
        
        try:
            while self.is_running and (time.time() - start) < duration_seconds:
                cycle += 1
                elapsed = time.time() - start
                
                # Create tasks based on goals
                if not self.tasks or len(self.tasks) < 5:
                    self._autopilot_create_tasks()
                
                # Execute pending tasks
                self.run(max_tasks=3)
                
                # Status
                print(f"[{elapsed:.0f}s] Cycle #{cycle} | "
                      f"Tasks: {len(self.tasks)} | "
                      f"Completed: {len(self.completed_tasks)}")
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nAutopilot interrupted!")
        
        print("\n" + "="*60)
        print("AUTOPILOT COMPLETE")
        print(f"Tasks completed: {len(self.completed_tasks)}")
        print("="*60)
    
    def _autopilot_create_tasks(self):
        """Auto-create tasks based on company goals"""
        if not self.company.get("mission"):
            # Default startup tasks
            tasks = [
                ("Create landing page", "WebDev", "Create a compelling landing page"),
                ("Write blog post", "Content", "Write an engaging blog post about our product"),
                ("Research competitors", "Researcher", "Analyze the competitive landscape"),
                ("Create social posts", "SocialMedia", "Create social media content"),
            ]
        else:
            tasks = [
                ("Develop website", "WebDev", "Build and launch company website"),
                ("Marketing campaign", "Marketing", "Create launch marketing campaign"),
                ("Create content", "Content", "Produce content for launch"),
            ]
        
        for title, worker, desc in tasks:
            if not any(t["title"] == title for t in self.tasks):
                self.create_task(title, desc, worker)
    
    # --- Status ---
    
    def get_status(self) -> SystemStatus:
        """Get system status"""
        uptime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        return SystemStatus(
            is_running=self.is_running,
            tasks_completed=len(self.completed_tasks),
            goals_achieved=sum(1 for g in self.goals if g.get("status") == "completed"),
            uptime=uptime,
            ai_provider=self.ai.provider or "none"
        )
    
    def dashboard(self) -> Dict[str, Any]:
        """Get dashboard data"""
        return {
            "status": asdict(self.get_status()),
            "company": self.company,
            "tasks": {
                "pending": len([t for t in self.tasks if t["status"] == "pending"]),
                "completed": len(self.completed_tasks),
                "total": len(self.tasks)
            },
            "goals": self.goals,
            "workers": {
                name: len(w.task_history)
                for name, w in self.workers.items()
            }
        }


# --- Quick Start ---

def quick_start(
    company_name: str = "My Startup",
    mission: str = "",
    workspace: str = None
) -> NanoCorpFree:
    """
    Quick start NanoCorp Free
    
    Usage:
        nano = quick_start("My Company", "Build an AI product")
        nano.create_website("My Product", "landing")
        nano.run()
    """
    nano = NanoCorpFree(workspace_path=workspace)
    nano.company["name"] = company_name
    if mission:
        nano.set_mission(mission)
    return nano


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   NanoCorp Free - AI Startup System                          ║
    ║   No API Key Needed!                                         ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    Getting started:
    
    1. INSTALL OLLAMA (recommended - completely free!)
       curl -fsSL https://ollama.com/install.sh | sh
       
       Then start: ollama serve
    
    2. OR Install Claude Code (free with Anthropic account)
       npm install -g @anthropic/claude-code
       claude login
    
    3. OR Install Gemini CLI (free with Google account)
       npx -y @google/gemini-cli
    
    Then run your startup!
    
    Example:
    >>> nano = quick_start("My AI Startup", "Build amazing products")
    >>> nano.create_website("My Product", "landing")
    >>> nano.create_campaign("Launch", ["social", "email"])
    >>> nano.run()
    
    Or run in autopilot:
    >>> nano.autopilot(duration_seconds=60)
    """)
