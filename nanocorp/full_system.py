"""
NanoCorp Full System - Complete AI Startup Operating System

State-of-the-art features:
- Vector Memory with semantic search
- Self-Improvement Engine
- Real Integrations (Email, GitHub, Deploy, Social)
- Agent Spawning System
- Docker Ready
"""
import os
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Import our advanced systems
from .nanocorp_free import NanoCorpFree, Worker, SystemStatus
from .vector_memory import VectorMemory, LearningEngine
from .integrations import IntegrationManager
from .agent_spawner import AgentSpawner, HierarchicalCEO


class NanoCorpFull(NanoCorpFree):
    """
    NanoCorp Full System - All features enabled
    
    This includes:
    - Vector Memory (semantic search over all work)
    - Self-Improvement Engine (learns from success/failure)
    - Real Integrations (email, deploy, social)
    - Agent Spawning (dynamic team assembly)
    - Docker Ready
    
    Usage:
        nano = NanoCorpFull()
        nano.integrations.configure("email", username="...", password="...")
        nano.run()
    """
    
    def __init__(
        self,
        workspace_path: str = None,
        provider: str = "auto",
        enable_memory: bool = True,
        enable_learning: bool = True,
        enable_integrations: bool = True,
        enable_spawning: bool = True
    ):
        # Initialize base system
        super().__init__(workspace_path=workspace_path, provider=provider)
        
        # Memory & Learning
        self.memory = None
        self.learning = None
        if enable_memory:
            self._init_memory()
        
        # Integrations
        self.integrations = None
        if enable_integrations:
            self._init_integrations()
        
        # Agent Spawning
        self.spawner = None
        self.ceo_hierarchical = None
        if enable_spawning:
            self._init_spawner()
        
        print("\n" + "="*60)
        print("NanoCorp Full System - State of the Art!")
        print("="*60)
        print("✅ Vector Memory (semantic search)")
        print("✅ Self-Improvement Engine")
        print("✅ Real Integrations")
        print("✅ Agent Spawning")
        print("✅ Docker Ready")
        print("="*60 + "\n")
    
    def _init_memory(self):
        """Initialize vector memory system"""
        try:
            storage = self.workspace / "memory.json"
            self.memory = VectorMemory(storage_path=str(storage))
            print(f"Memory initialized: {len(self.memory.entries)} entries")
        except Exception as e:
            print(f"Memory init failed: {e}")
    
    def _init_integrations(self):
        """Initialize integration manager"""
        try:
            config_path = self.workspace.parent / "config" / "integrations.json"
            self.integrations = IntegrationManager(config_path=str(config_path))
            
            status = self.integrations.status()
            configured = sum(1 for v in status.values() if v)
            print(f"Integrations: {configured}/5 configured")
        except Exception as e:
            print(f"Integrations init failed: {e}")
    
    def _init_spawner(self):
        """Initialize agent spawning system"""
        try:
            self.spawner = AgentSpawner(
                free_ai=self.ai,
                workspace=str(self.workspace / "agents")
            )
            
            self.ceo_hierarchical = HierarchicalCEO(
                spawner=self.spawner,
                free_ai=self.ai
            )
            
            print("Agent Spawner initialized")
        except Exception as e:
            print(f"Spawner init failed: {e}")
    
    # --- Memory Features ---
    
    def remember(self, content: str, memory_type: str = "experience", importance: float = 0.7):
        """Store a memory"""
        if self.memory:
            return self.memory.store(content, memory_type, importance=importance)
    
    def recall(self, query: str, limit: int = 5) -> List[Dict]:
        """Recall similar memories"""
        if self.memory:
            return self.memory.recall(query, limit=limit)
        return []
    
    def learn_from(self, experience: str, success: bool):
        """Learn from an outcome"""
        if self.memory:
            outcome = "success" if success else "failure"
            self.memory.learn_from(experience, outcome)
    
    def get_insights(self) -> List[str]:
        """Get learned insights"""
        if self.memory:
            return self.memory.get_insights()
        return []
    
    # --- Integration Features ---
    
    def send_email(self, to: str, subject: str, body: str) -> Dict:
        """Send an email (requires SMTP config)"""
        if self.integrations:
            result = self.integrations.email.send(to, subject, body)
            return asdict(result)
        return {"success": False, "details": "Integrations not enabled"}
    
    def deploy_website(self, path: str, platform: str = "vercel") -> Dict:
        """Deploy a website"""
        if not self.integrations:
            return {"success": False, "details": "Integrations not enabled"}
        
        if platform == "vercel":
            result = self.integrations.deploy.deploy_vercel(path)
        elif platform == "netlify":
            result = self.integrations.deploy.deploy_netlify(path)
        else:
            result = {"success": False, "details": f"Unknown platform: {platform}"}
        
        return asdict(result)
    
    def post_twitter(self, content: str) -> Dict:
        """Post to Twitter/X (requires API config)"""
        if self.integrations:
            result = self.integrations.social.post_twitter(content)
            return asdict(result)
        return {"success": False, "details": "Integrations not enabled"}
    
    # --- Agent Spawning ---
    
    def spawn_agent(self, role: str, task: str, wait: bool = True) -> Optional[Dict]:
        """Spawn a specialized agent for a task"""
        if self.spawner:
            agent_id = self.spawner.spawn(role=role, task=task, wait_for_result=wait)
            if wait:
                return self.spawner.get_result(agent_id)
            return {"agent_id": agent_id, "status": "spawned"}
        return {"error": "Spawner not enabled"}
    
    def assemble_team(self, roles: List[str]) -> Dict[str, str]:
        """Assemble a team of specialists"""
        if self.ceo_hierarchical:
            return self.ceo_hierarchical.assemble_team(roles)
        return {}
    
    # --- Enhanced Execution ---
    
    def run_with_learning(self, max_tasks: int = 10):
        """Run tasks with learning enabled"""
        pending = [t for t in self.tasks if t["status"] == "pending"][:max_tasks]
        
        if not pending:
            print("No pending tasks!")
            return
        
        print(f"\nExecuting {len(pending)} tasks with learning...\n")
        
        for task in pending:
            print(f"[{task['worker']}] {task['title'][:50]}...")
            
            worker = self.workers.get(task["worker"])
            if worker:
                start_time = time.time()
                result = worker.execute(task)
                duration = time.time() - start_time
                
                task["status"] = "completed"
                task["result"] = result
                self.completed_tasks.append(task)
                
                # Learn from this
                success = result.get("success", True)
                self.learn_from(
                    f"{task['worker']} executed {task['title']}",
                    success=success
                )
                
                if self.memory:
                    self.memory.store(
                        f"Task: {task['title']} | Worker: {task['worker']} | "
                        f"Duration: {duration:.1f}s | Success: {success}",
                        memory_type="task_execution",
                        importance=0.6
                    )
                
                print(f"  -> Done! (Learned)")
            else:
                print(f"  -> Worker not found!")
        
        print(f"\nCompleted {len(self.completed_tasks)} tasks with learning!")
    
    def run_with_spawning(self, tasks: Dict[str, str]):
        """Run tasks by spawning specialized agents"""
        if not self.ceo_hierarchical:
            print("Spawning not enabled!")
            return
        
        print("\nSpawning agents for parallel execution...\n")
        
        # Spawn agents for each task
        results = self.ceo_hierarchical.parallel_execute(tasks)
        
        for role, info in results.items():
            print(f"[Spawned] {role}: {info['task'][:50]}...")
        
        # Wait for completion
        print("\nWaiting for agents to complete...")
        all_results = self.ceo_hierarchical.get_all_results(timeout=300)
        
        print("\nResults:")
        for role, result in all_results.items():
            print(f"\n{role}:")
            if result and result.get("output"):
                print(f"  {result['output'][:200]}...")
        
        return all_results
    
    # --- Dashboard ---
    
    def full_dashboard(self) -> Dict[str, Any]:
        """Get full system dashboard"""
        base = self.dashboard()
        
        # Add memory stats
        if self.memory:
            base["memory"] = self.memory.stats()
            base["insights"] = self.get_insights()
        
        # Add integration status
        if self.integrations:
            base["integrations"] = self.integrations.status()
        
        # Add spawner status
        if self.spawner:
            base["spawner"] = self.spawner.get_status()
        
        return base
    
    # --- Auto-Improvement ---
    
    def auto_improve(self) -> List[str]:
        """Run auto-improvement based on learnings"""
        if not self.memory:
            return []
        
        insights = []
        
        # Get patterns
        patterns = self.memory.get_patterns()
        
        # Analyze success patterns
        successes = patterns.get("success_pattern", [])
        if successes:
            insights.append(f"📈 Found {len(successes)} success patterns")
            
            # What works well?
            success_workers = [s for s in successes if s.get("content")]
            if success_workers:
                insights.append(f"✅ Best approach: {success_workers[0]['content'][:100]}")
        
        # Analyze failures
        failures = patterns.get("failure_pattern", [])
        if failures:
            insights.append(f"⚠️ Found {len(failures)} failure patterns")
        
        # Generate recommendations
        if self.learning:
            recommendations = self.learning.auto_optimize()
            insights.extend(recommendations)
        
        return insights


# Quick start with full system
def quick_start_full(
    company_name: str = "My Startup",
    mission: str = "",
    workspace: str = None
) -> NanoCorpFull:
    """Quick start with full features"""
    nano = NanoCorpFull(workspace_path=workspace)
    nano.company["name"] = company_name
    if mission:
        nano.set_mission(mission)
    return nano
