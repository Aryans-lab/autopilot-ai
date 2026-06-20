"""
NanoCorp v3.0 - REST API Server

FastAPI server for the NanoCorp AI agent system.
"""
import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# Disable OpenHands telemetry
os.environ['OPENHANDS_SUPPRESS_BANNER'] = '1'
os.environ['OTEL_SDK_DISABLED'] = 'true'

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from nanocorp.agents import AgentManager, AgentType
from nanocorp.tools.registry import register_all_tools
from nanocorp.ai import get_ai_hub


# ===========================================
# REQUEST/RESPONSE MODELS
# ===========================================

class TaskCreate(BaseModel):
    title: str
    type: str
    description: Optional[str] = ""
    priority: Optional[str] = "medium"


class MessageCreate(BaseModel):
    agent_id: str
    content: str


class WorkforceCreate(BaseModel):
    company_name: str
    mission: str


# ===========================================
# API SERVER
# ===========================================

class NanoCorpAPI:
    """FastAPI server for NanoCorp."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        
        # Initialize system
        os.environ['OPENHANDS_SUPPRESS_BANNER'] = '1'
        os.environ['OTEL_SDK_DISABLED'] = 'true'
        
        self.ai = get_ai_hub()
        self.manager = AgentManager(ai_provider=self.ai)
        self.ceo = None
        
        # Create FastAPI app
        self.app = FastAPI(
            title="NanoCorp API",
            description="Autonomous AI Agent System API",
            version="3.0.0"
        )
        
        # CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes."""
        app = self.app
        
        @app.get("/")
        async def root():
            return {
                "name": "NanoCorp API",
                "version": "3.0.0",
                "status": "running"
            }
        
        @app.get("/health")
        async def health():
            return {"status": "healthy"}
        
        @app.post("/workforce")
        async def create_workforce(data: WorkforceCreate):
            """Create a new workforce."""
            self.ceo = self.manager.create_workforce(
                company_name=data.company_name,
                mission=data.mission
            )
            return {
                "success": True,
                "company": self.ceo.company_name,
                "workers": len(self.ceo.workers)
            }
        
        @app.get("/agents")
        async def list_agents():
            """List all agents."""
            if not self.ceo:
                return {"agents": [], "count": 0}
            
            agents = []
            for wid, worker in self.ceo.workers.items():
                agents.append({
                    "id": worker.id,
                    "name": worker.name,
                    "type": worker.type.value,
                    "status": worker.state.status,
                    "current_task": worker.state.current_task
                })
            
            return {"agents": agents, "count": len(agents)}
        
        @app.post("/tasks")
        async def create_task(data: TaskCreate):
            """Execute a task."""
            if not self.ceo:
                raise HTTPException(status_code=400, detail="No workforce created")
            
            task = {
                "id": f"task_{datetime.now().timestamp()}",
                "title": data.title,
                "type": data.type,
                "description": data.description
            }
            
            result = await self.manager.execute_task(task)
            
            return {
                "success": result.get("success", True),
                "task": task,
                "result": str(result)[:500]
            }
        
        @app.get("/stats")
        async def get_stats():
            """Get workforce stats."""
            if not self.ceo:
                return {"workers": 0, "tasks": 0}
            
            return {
                "workers": len(self.ceo.workers),
                "tasks_total": len(self.ceo.tasks),
                "tasks_pending": len([t for t in self.ceo.tasks if t.get("status") == "pending"]),
                "tasks_completed": len([t for t in self.ceo.tasks if t.get("status") == "completed"]),
                "goals": len(self.ceo.goals)
            }
        
        @app.get("/tasks")
        async def list_tasks():
            """List all tasks."""
            if not self.ceo:
                return {"tasks": []}
            return {"tasks": self.ceo.tasks}
    
    def run(self):
        """Run the server."""
        print(f"\n🚀 NanoCorp API Server starting on http://{self.host}:{self.port}")
        print(f"   API Docs: http://{self.host}:{self.port}/docs")
        print()
        
        uvicorn.run(self.app, host=self.host, port=self.port)


def main():
    """Run the API server."""
    api = NanoCorpAPI(host="0.0.0.0", port=8000)
    api.run()


if __name__ == "__main__":
    main()
