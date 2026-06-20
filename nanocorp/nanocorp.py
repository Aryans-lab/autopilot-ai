"""
NanoCorp - Autonomous AI Startup System
Main orchestrator for the AI-powered business automation
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from openhands.sdk import LLM

from .config import config, get_config, update_business_info
from .agents import (
    CEOSystem,
    TaskManager,
    Task,
    TaskStatus,
    TaskPriority,
    TaskCategory,
)
from .agents.workers import (
    WebDevWorker,
    MarketingWorker,
    EmailWorker,
    SocialMediaWorker,
    DocumentWorker,
    ContentWorker,
    ResearcherWorker,
    NetworkerWorker,
)


class NanoCorp:
    """
    NanoCorp - The Autonomous AI Startup System
    
    A complete AI-powered business automation system with:
    - CEO Agent for strategic planning and coordination
    - Specialized Worker Agents for different business functions
    - Task management and execution system
    - Workspace for organizing outputs
    
    Usage:
        nanocorp = NanoCorp(api_key="your-api-key")
        nanocorp.set_company("My Company", "Mission statement...")
        nanocorp.assign("Create a landing page", worker="WebDev")
        nanocorp.run()
    """
    
    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        base_url: str = None,
        workspace_path: str = None,
        debug: bool = False
    ):
        """
        Initialize NanoCorp
        
        Args:
            api_key: LLM API key (or set OPENAI_API_KEY env var)
            model: Model to use (default: gpt-4o)
            base_url: Custom API base URL for other providers
            workspace_path: Custom workspace directory
            debug: Enable debug mode
        """
        # Set up configuration
        if api_key:
            os.environ["LLM_API_KEY"] = api_key
        if model:
            config.llm.model = model
        if base_url:
            config.llm.base_url = base_url
        if debug:
            config.debug_mode = True
        
        # Set up workspace
        if workspace_path:
            config.workspace.root = Path(workspace_path)
        else:
            config.workspace.root = Path(__file__).parent / "workspace"
        
        config.workspace.root.mkdir(parents=True, exist_ok=True)
        config.workspace.projects_dir.mkdir(parents=True, exist_ok=True)
        config.workspace.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize LLM
        self.llm = LLM(
            model=config.llm.model,
            api_key=config.llm.api_key or os.environ.get("LLM_API_KEY"),
            base_url=config.llm.base_url,
        )
        
        # Initialize task manager
        self.task_manager = TaskManager(
            storage_path=config.workspace.root / "tasks.json"
        )
        
        # Initialize CEO system
        self.ceo = CEOSystem(
            llm=self.llm,
            task_manager=self.task_manager,
            workspace_path=config.workspace.root,
            max_concurrent_workers=config.max_concurrent_workers
        )
        
        # Initialize worker agents
        self._initialize_workers()
        
        # Status
        self.is_running = False
    
    def _initialize_workers(self):
        """Initialize all worker agents"""
        workspace = config.workspace.root
        
        self.workers = {
            "WebDev": WebDevWorker(self.llm, workspace),
            "Marketing": MarketingWorker(self.llm, workspace),
            "Email": EmailWorker(self.llm, workspace),
            "SocialMedia": SocialMediaWorker(self.llm, workspace),
            "Document": DocumentWorker(self.llm, workspace),
            "Content": ContentWorker(self.llm, workspace),
            "Researcher": ResearcherWorker(self.llm, workspace),
            "Networker": NetworkerWorker(self.llm, workspace),
        }
        
        # Register workers with CEO
        for worker in self.workers.values():
            self.ceo.register_worker(worker)
    
    def set_company(
        self,
        name: str,
        mission: str = "",
        industry: str = "Technology",
        target_market: str = ""
    ):
        """Set company information"""
        self.ceo.set_company_info(name, mission)
        update_business_info(
            company_name=name,
            company_description=mission,
            industry=industry,
            target_market=target_market
        )
    
    # ============ TASK CREATION ============
    
    def create_task(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        category: str = "custom",
        context: Dict[str, Any] = None
    ) -> Task:
        """Create a new task"""
        return self.task_manager.create_task(
            title=title,
            description=description,
            priority=TaskPriority(priority),
            category=TaskCategory(category),
            context=context or {}
        )
    
    def assign(self, task_or_title: str, worker: str = None, **kwargs) -> Task:
        """
        Create and assign a task to a worker
        
        Args:
            task_or_title: Task title or existing task
            worker: Worker name (WebDev, Marketing, Email, SocialMedia, Document, Researcher, Networker)
            **kwargs: Additional task context
        
        Returns:
            Created task
        """
        if isinstance(task_or_title, Task):
            task = task_or_title
        else:
            task = self.create_task(task_or_title, context=kwargs)
        
        if worker:
            self.ceo.delegate_task(task.id, worker)
        elif kwargs.get("category"):
            self.ceo.delegate_task(task.id)
        
        return task
    
    # ============ SPECIALIZED CREATION METHODS ============
    
    def create_website(
        self,
        name: str,
        website_type: str = "landing",
        **kwargs
    ) -> Dict[str, Any]:
        """Create a website (landing page, business site, or portfolio)"""
        task = self.create_task(
            title=f"Create {name} {website_type} website",
            category=TaskCategory.WEB_DEV,
            context={
                "action": f"create_{website_type}_website",
                "product_name": name,
                **kwargs
            }
        )
        self.ceo.delegate_task(task.id, "WebDev")
        result = self.ceo.execute_task(task.id)
        return result
    
    def create_marketing_campaign(
        self,
        name: str,
        channels: List[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a marketing campaign"""
        if channels is None:
            channels = ["social", "email", "content"]
        
        task = self.create_task(
            title=f"Marketing campaign for {name}",
            category=TaskCategory.MARKETING,
            context={
                "action": "create_campaign",
                "campaign_name": name,
                "channels": channels,
                **kwargs
            }
        )
        self.ceo.delegate_task(task.id, "Marketing")
        result = self.ceo.execute_task(task.id)
        return result
    
    def create_email_campaign(
        self,
        campaign_type: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create an email campaign"""
        action_map = {
            "newsletter": "create_newsletter",
            "cold": "create_cold_email",
            "drip": "create_drip_sequence",
            "promotional": "create_promotional_email",
        }
        
        task = self.create_task(
            title=f"Email {campaign_type} campaign",
            category=TaskCategory.EMAIL,
            context={
                "action": action_map.get(campaign_type, "create_newsletter"),
                **kwargs
            }
        )
        self.ceo.delegate_task(task.id, "Email")
        result = self.ceo.execute_task(task.id)
        return result
    
    def create_social_content(
        self,
        topic: str,
        platforms: List[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create social media content"""
        if platforms is None:
            platforms = ["twitter", "linkedin"]
        
        task = self.create_task(
            title=f"Social media content about {topic}",
            category=TaskCategory.SOCIAL_MEDIA,
            context={
                "action": "create_posts",
                "topic": topic,
                "platforms": platforms,
                **kwargs
            }
        )
        self.ceo.delegate_task(task.id, "SocialMedia")
        result = self.ceo.execute_task(task.id)
        return result
    
    def create_document(
        self,
        doc_type: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a business document"""
        action_map = {
            "proposal": "create_proposal",
            "meeting": "create_meeting_notes",
            "plan": "create_business_plan",
            "press": "create_press_release",
        }
        
        task = self.create_task(
            title=f"Create {doc_type} document",
            category=TaskCategory.DOCUMENTATION,
            context={
                "action": action_map.get(doc_type, "create_proposal"),
                **kwargs
            }
        )
        self.ceo.delegate_task(task.id, "Document")
        result = self.ceo.execute_task(task.id)
        return result
    
    def research(
        self,
        topic: str,
        research_type: str = "market",
        **kwargs
    ) -> Dict[str, Any]:
        """Conduct research"""
        task = self.create_task(
            title=f"{research_type.title()} research on {topic}",
            category=TaskCategory.RESEARCH,
            context={
                "action": f"{research_type}_research",
                f"{research_type}_name": topic,
                **kwargs
            }
        )
        self.ceo.delegate_task(task.id, "Researcher")
        result = self.ceo.execute_task(task.id)
        return result
    
    def network(
        self,
        outreach_type: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create networking outreach"""
        task = self.create_task(
            title=f"{outreach_type.title()} networking",
            category=TaskCategory.NETWORKING,
            context={
                "action": f"{outreach_type}_outreach",
                **kwargs
            }
        )
        self.ceo.delegate_task(task.id, "Networker")
        result = self.ceo.execute_task(task.id)
        return result
    
    # ============ EXECUTION ============
    
    def run(self, max_tasks: int = None):
        """Execute pending tasks"""
        results = self.ceo.execute_ready_tasks(max_tasks=max_tasks)
        return results
    
    def execute_task(self, task_id: str) -> Dict[str, Any]:
        """Execute a specific task"""
        return self.ceo.execute_task(task_id)
    
    # ============ STATUS & REPORTING ============
    
    def status(self) -> Dict[str, Any]:
        """Get current status"""
        return self.ceo.get_status_report()
    
    def board(self) -> Dict[str, List]:
        """Get Kanban-style task board"""
        return self.task_manager.get_board_view()
    
    def stats(self) -> Dict[str, Any]:
        """Get task statistics"""
        return self.task_manager.get_statistics()
    
    def save(self, path: str = None):
        """Save system state"""
        if path is None:
            path = config.workspace.root / "nanocorp_state.json"
        self.ceo.save_state(Path(path))
    
    def load(self, path: str = None):
        """Load system state"""
        if path is None:
            path = config.workspace.root / "nanocorp_state.json"
        self.ceo.load_state(Path(path))
    
    # ============ INTERACTIVE MODE ============
    
    def chat(self, message: str) -> str:
        """Chat with the CEO agent"""
        return self.ceo.handle_user_request(message)
    
    def start(self):
        """Start NanoCorp in interactive mode"""
        self.is_running = True
        print("=" * 60)
        print("🤖 NanoCorp - Autonomous AI Startup System")
        print("=" * 60)
        print(f"\nCompany: {config.business.company_name}")
        print(f"Workers: {', '.join(self.workers.keys())}")
        print("\nCommands:")
        print("  status  - Show current status")
        print("  board   - Show task board")
        print("  stats   - Show statistics")
        print("  run     - Execute pending tasks")
        print("  save    - Save current state")
        print("  help    - Show this help")
        print("  exit    - Exit NanoCorp")
        print("\n" + "=" * 60)
        
        while self.is_running:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["exit", "quit", "q"]:
                    self.save()
                    print("\n👋 Goodbye! State saved.")
                    self.is_running = False
                elif user_input.lower() == "status":
                    status = self.status()
                    print(json.dumps(status, indent=2))
                elif user_input.lower() == "board":
                    board = self.board()
                    print(json.dumps(board, indent=2))
                elif user_input.lower() == "stats":
                    stats = self.stats()
                    print(json.dumps(stats, indent=2))
                elif user_input.lower() == "run":
                    results = self.run()
                    print(f"\n✅ Executed {len(results)} tasks")
                elif user_input.lower() == "save":
                    self.save()
                    print("✅ State saved")
                elif user_input.lower() == "help":
                    print("\nQuick Commands:")
                    print("  create_website('Product Name', type='landing')")
                    print("  create_marketing_campaign('Campaign Name', channels=['social', 'email'])")
                    print("  create_email_campaign('newsletter', ...)")
                    print("  create_social_content('Topic', platforms=['twitter', 'linkedin'])")
                    print("  create_document('proposal', client_name='...', ...)")
                    print("  research('Market Name', type='market')")
                    print("  network('partnership', partner_type='...')")
                else:
                    response = self.chat(user_input)
                    print(f"\nCEO: {response}")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! State saved.")
                self.save()
                self.is_running = False
            except Exception as e:
                print(f"\n❌ Error: {e}")


def quick_start(
    company_name: str = "NanoCorp",
    mission: str = "Build amazing things with AI",
    api_key: str = None,
    **kwargs
) -> NanoCorp:
    """
    Quick start NanoCorp with a single function call
    
    Args:
        company_name: Your company name
        mission: Company mission statement
        api_key: LLM API key
        **kwargs: Additional NanoCorp config
    
    Returns:
        Configured NanoCorp instance
    """
    nanocorp = NanoCorp(api_key=api_key, **kwargs)
    nanocorp.set_company(company_name, mission)
    return nanocorp
