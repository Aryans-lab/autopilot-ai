"""
NanoCorp v3.0 - REST API

FastAPI-based API for external access.
"""
from __future__ import annotations

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Optional imports
try:
    import uvicorn
    UVICORN_AVAILABLE = True
except ImportError:
    UVICORN_AVAILABLE = False


# ===========================================
# REQUEST/RESPONSE MODELS
# ===========================================

class TaskRequest(BaseModel):
    """Task execution request."""
    title: str
    task_type: str
    description: Optional[str] = ""
    priority: str = "medium"
    metadata: Dict[str, Any] = {}


class TaskResponse(BaseModel):
    """Task response."""
    id: str
    title: str
    status: str
    result: Optional[Dict] = None


class AgentRequest(BaseModel):
    """Agent action request."""
    agent_id: str
    action: str
    params: Dict[str, Any] = {}


class MessageRequest(BaseModel):
    """Send message request."""
    to_agent: str
    content: str
    msg_type: str = "message"


class CompanyRequest(BaseModel):
    """Set company request."""
    name: str
    mission: str = ""


# ===========================================
# API SERVER
# ===========================================

class NanoCorpAPI:
    """
    NanoCorp REST API Server.
    
    Endpoints:
    - GET / - Health check
    - GET /health - Detailed health
    - GET /agents - List agents
    - POST /tasks - Create task
    - GET /tasks/{id} - Get task
    - POST /message - Send message
    - POST /company - Set company
    - GET /stats - Workforce stats
    """
    
    def __init__(
        self,
        agent_manager: Any = None,
        host: str = "0.0.0.0",
        port: int = 8000
    ):
        self.agent_manager = agent_manager
        self.host = host
        self.port = port
        self.app = self._create_app()
        self.server = None
    
    def _create_app(self) -> FastAPI:
        """Create FastAPI app."""
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            print(f"NanoCorp API starting on {self.host}:{self.port}")
            yield
            # Shutdown
            print("NanoCorp API shutting down")
        
        app = FastAPI(
            title="NanoCorp API",
            description="Autonomous AI Agent System API",
            version="3.0.0",
            lifespan=lifespan
        )
        
        # CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Health endpoints
        @app.get("/")
        async def root():
            return {
                "service": "NanoCorp API",
                "version": "3.0.0",
                "status": "running"
            }
        
        @app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "agents_registered": len(self.agent_manager.agents) if self.agent_manager else 0
            }
        
        # Agent endpoints
        @app.get("/agents")
        async def list_agents():
            if not self.agent_manager:
                raise HTTPException(503, "Agent manager not configured")
            
            return {
                "agents": [
                    agent.to_dict() 
                    for agent in self.agent_manager.agents.values()
                ]
            }
        
        @app.get("/agents/{agent_id}")
        async def get_agent(agent_id: str):
            if not self.agent_manager:
                raise HTTPException(503, "Agent manager not configured")
            
            agent = self.agent_manager.get_agent(agent_id)
            if not agent:
                raise HTTPException(404, f"Agent not found: {agent_id}")
            
            return agent.to_dict()
        
        # Task endpoints
        @app.post("/tasks", response_model=TaskResponse)
        async def create_task(task: TaskRequest):
            if not self.agent_manager:
                raise HTTPException(503, "Agent manager not configured")
            
            task_dict = task.model_dump()
            task_dict["id"] = f"task_{datetime.now().timestamp()}"
            
            # Execute task
            result = await self.agent_manager.execute_task(task_dict)
            
            return TaskResponse(
                id=task_dict["id"],
                title=task.title,
                status="completed" if result.get("success") else "failed",
                result=result
            )
        
        @app.post("/tasks/batch")
        async def batch_tasks(tasks: List[TaskRequest]):
            if not self.agent_manager:
                raise HTTPException(503, "Agent manager not configured")
            
            task_dicts = []
            for i, task in enumerate(tasks):
                d = task.model_dump()
                d["id"] = f"task_{datetime.now().timestamp()}_{i}"
                task_dicts.append(d)
            
            results = await self.agent_manager.execute_parallel(task_dicts)
            
            return {
                "submitted": len(tasks),
                "results": [
                    TaskResponse(
                        id=t["id"],
                        title=t["title"],
                        status="completed" if results[i].get("success") else "failed",
                        result=results[i]
                    )
                    for i, t in enumerate(task_dicts)
                ]
            }
        
        # Message endpoint
        @app.post("/message")
        async def send_message(msg: MessageRequest):
            if not self.agent_manager:
                raise HTTPException(503, "Agent manager not configured")
            
            # Find sender (for now, use ceo)
            from_agent = "ceo"
            
            success = await self.agent_manager.send_message(
                from_agent=from_agent,
                to_agent=msg.to_agent,
                content=msg.content,
                msg_type=msg.msg_type
            )
            
            if not success:
                raise HTTPException(400, "Failed to send message")
            
            return {"status": "sent"}
        
        # Company endpoint
        @app.post("/company")
        async def set_company(company: CompanyRequest):
            if not self.agent_manager:
                raise HTTPException(503, "Agent manager not configured")
            
            ceo = self.agent_manager.get_agent("ceo")
            if ceo:
                ceo.set_company(company.name, company.mission)
            
            return {"status": "updated", "company": company.name}
        
        # Stats endpoint
        @app.get("/stats")
        async def get_stats():
            if not self.agent_manager:
                raise HTTPException(503, "Agent manager not configured")
            
            return self.agent_manager.get_dashboard()
        
        return app
    
    def run(self, blocking: bool = True):
        """Run the API server."""
        if not UVICORN_AVAILABLE:
            print("uvicorn not installed. Run: pip install uvicorn")
            return
        
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        self.server = uvicorn.Server(config)
        
        if blocking:
            asyncio.run(self.server.serve())
        else:
            asyncio.create_task(self.server.serve())
    
    def stop(self):
        """Stop the API server."""
        if self.server:
            self.server.should_exit = True


# ===========================================
# WEBSOCKET MANAGER
# ===========================================

class WebSocketManager:
    """Manage WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept and store a WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: Dict):
        """Broadcast message to all connections."""
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        # Clean up disconnected
        for ws in disconnected:
            self.disconnect(ws)
    
    async def send_personal(self, websocket: WebSocket, message: Dict):
        """Send message to specific connection."""
        try:
            await websocket.send_json(message)
        except:
            self.disconnect(websocket)


# Global WebSocket manager
ws_manager = WebSocketManager()
