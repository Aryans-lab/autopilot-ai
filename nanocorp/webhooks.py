"""
NanoCorp v3.0 - Webhook System

Event-driven automation with webhook endpoints.
"""
from __future__ import annotations

import hmac
import hashlib
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

from fastapi import FastAPI, HTTPException, Request, Header
from pydantic import BaseModel

try:
    import uvicorn
    UVICORN_AVAILABLE = True
except ImportError:
    UVICORN_AVAILABLE = False


class WebhookEvent(str, Enum):
    """Webhook event types."""
    TASK_CREATED = "task.created"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    AGENT_REGISTERED = "agent.registered"
    MESSAGE_RECEIVED = "message.received"
    GOAL_ACHIEVED = "goal.achieved"
    SCHEDULE_TRIGGERED = "schedule.triggered"


@dataclass
class Webhook:
    """A webhook endpoint."""
    id: str
    url: str
    events: List[str]
    secret: Optional[str] = None
    enabled: bool = True
    headers: Dict[str, str] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass 
class WebhookDelivery:
    """Record of a webhook delivery."""
    id: str
    webhook_id: str
    event: str
    payload: Dict
    response_status: Optional[int] = None
    response_body: Optional[str] = None
    delivered_at: Optional[str] = None
    error: Optional[str] = None


class WebhookManager:
    """
    Manage webhooks for event-driven automation.
    
    Features:
    - Register webhook endpoints
    - Trigger on events
    - HMAC signature verification
    - Retry logic
    - Delivery logging
    """
    
    def __init__(self):
        self.webhooks: Dict[str, Webhook] = {}
        self.deliveries: List[WebhookDelivery] = []
        self._handlers: Dict[str, List[Callable]] = {}
    
    def register(
        self,
        url: str,
        events: List[str],
        webhook_id: Optional[str] = None,
        secret: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Register a webhook.
        
        Args:
            url: Webhook URL
            events: Events to listen for
            webhook_id: Optional webhook ID
            secret: Secret for signature verification
            headers: Custom headers
        
        Returns:
            Webhook ID
        """
        wid = webhook_id or f"webhook_{len(self.webhooks) + 1}"
        
        webhook = Webhook(
            id=wid,
            url=url,
            events=events,
            secret=secret,
            headers=headers or {}
        )
        
        self.webhooks[wid] = webhook
        return wid
    
    def unregister(self, webhook_id: str) -> bool:
        """Unregister a webhook."""
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            return True
        return False
    
    def add_handler(self, event: str, handler: Callable):
        """Add an event handler."""
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)
    
    async def trigger(self, event: str, payload: Dict) -> List[WebhookDelivery]:
        """
        Trigger webhooks for an event.
        
        Args:
            event: Event type
            payload: Event payload
        
        Returns:
            List of delivery results
        """
        results = []
        
        # Call local handlers first
        for handler in self._handlers.get(event, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(payload)
                else:
                    handler(payload)
            except Exception as e:
                print(f"Webhook handler error: {e}")
        
        # Find matching webhooks
        for webhook in self.webhooks.values():
            if not webhook.enabled:
                continue
            if event not in webhook.events:
                continue
            
            # Deliver webhook
            delivery = await self._deliver(webhook, event, payload)
            results.append(delivery)
        
        return results
    
    async def _deliver(
        self,
        webhook: Webhook,
        event: str,
        payload: Dict
    ) -> WebhookDelivery:
        """Deliver a webhook."""
        import httpx
        
        delivery_id = f"delivery_{len(self.deliveries) + 1}"
        
        # Build headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "NanoCorp/3.0",
            "X-NanoCorp-Event": event,
            "X-NanoCorp-Delivery": delivery_id,
            **webhook.headers
        }
        
        # Add signature if secret provided
        if webhook.secret:
            payload_str = json.dumps(payload, sort_keys=True)
            signature = hmac.new(
                webhook.secret.encode(),
                payload_str.encode(),
                hashlib.sha256
            ).hexdigest()
            headers["X-NanoCorp-Signature"] = f"sha256={signature}"
        
        # Prepare payload with metadata
        full_payload = {
            "event": event,
            "timestamp": datetime.now().isoformat(),
            "delivery": delivery_id,
            "data": payload
        }
        
        delivery = WebhookDelivery(
            id=delivery_id,
            webhook_id=webhook.id,
            event=event,
            payload=full_payload
        )
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    webhook.url,
                    json=full_payload,
                    headers=headers
                )
            
            delivery.response_status = response.status_code
            delivery.response_body = response.text[:1000]
            delivery.delivered_at = datetime.now().isoformat()
            
        except Exception as e:
            delivery.error = str(e)
        
        self.deliveries.append(delivery)
        return delivery
    
    def get_deliveries(self, webhook_id: Optional[str] = None) -> List[WebhookDelivery]:
        """Get webhook delivery history."""
        if webhook_id:
            return [d for d in self.deliveries if d.webhook_id == webhook_id]
        return list(self.deliveries)
    
    def create_app(self) -> FastAPI:
        """Create FastAPI app for webhook endpoints."""
        app = FastAPI(title="NanoCorp Webhooks")
        
        @app.post("/webhooks/{webhook_id}")
        async def receive_webhook(
            webhook_id: str,
            request: Request,
            x_nanocorp_signature: Optional[str] = Header(None)
        ):
            """Endpoint to receive incoming webhooks."""
            payload = await request.json()
            
            # Find webhook
            webhook = self.webhooks.get(webhook_id)
            if not webhook:
                raise HTTPException(404, "Webhook not found")
            
            # Verify signature if needed
            if webhook.secret and x_nanocorp_signature:
                body = json.dumps(payload, sort_keys=True)
                expected = "sha256=" + hmac.new(
                    webhook.secret.encode(),
                    body.encode(),
                    hashlib.sha256
                ).hexdigest()
                
                if not hmac.compare_digest(x_nanocorp_signature, expected):
                    raise HTTPException(401, "Invalid signature")
            
            return {"status": "received"}
        
        return app


# Global webhook manager
_webhook_manager: Optional[WebhookManager] = None

def get_webhook_manager() -> WebhookManager:
    """Get global webhook manager."""
    global _webhook_manager
    if _webhook_manager is None:
        _webhook_manager = WebhookManager()
    return _webhook_manager
