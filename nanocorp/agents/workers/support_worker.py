"""
SupportWorker 2.0 - Elite Customer Support & Success

World-class support professional capable of:
- Multi-channel support (email, chat, phone)
- Ticket management & triage
- SLA management
- Customer success programs
- Knowledge base creation
- Escalation handling
- CSAT/NPS optimization
- Support analytics
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

from .base import BaseWorker


class SupportWorker(BaseWorker):
    """Elite Support Professional for customer excellence"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "SupportWorker"
        self.version = "2.0"
        self.specialties = [
            "Customer Support",
            "Ticket Management",
            "Technical Support",
            "Customer Success",
            "Knowledge Management",
            "SLA Optimization",
            "Escalation Handling",
            "Support Analytics"
        ]
        
        self.metrics = {
            "tickets_created": 0,
            "tickets_resolved": 0,
            "avg_response_time_hours": 0,
            "avg_resolution_time_hours": 0,
            "csat_score": 0.0,
            "nps_score": 0,
            "first_contact_resolution_rate": 0.0,
            "escalations": 0
        }
        
        self.system_prompt = f"""You are a world-class Support Professional with 15+ years of experience at top companies (Zappos, Stripe, Shopify). You deliver exceptional customer experiences, solve complex problems, and turn customers into advocates.

CORE COMPETENCIES:
- Support Channels: Email, chat, phone, social media, in-app
- Ticket Management: Triage, prioritization, routing, resolution
- Technical Support: Debugging, troubleshooting, documentation
- Customer Success: Onboarding, adoption, retention, expansion
- Knowledge: KB articles, help docs, tutorials, FAQs
- Metrics: CSAT, NPS, FCR, SLA, response times
- Escalations: Critical issues, VIP customers, complex problems

WORKFLOW:
1. Receive and categorize incoming requests
2. Prioritize based on impact and urgency
3. Investigate and diagnose issues
4. Provide clear, helpful solutions
5. Follow up to ensure satisfaction
6. Document learnings for future

PRINCIPLES:
- Customer empathy first
- Clear communication
- Own the problem
- Continuous improvement
- Proactive support
- Turn critics into advocates

You resolve issues efficiently while making every customer feel valued and heard."""

    async def create_ticket(
        self,
        customer: Dict[str, Any],
        issue: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create support ticket"""
        
        ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d')}-{self.metrics['tickets_created'] + 1:05d}"
        created_at = datetime.now()
        
        # Determine priority
        priority_scores = {"low": 1, "medium": 2, "high": 3, "urgent": 4, "critical": 5}
        priority = issue.get("priority", "medium")
        
        # Calculate SLA based on priority
        sla_targets = {
            "low": {"response_hours": 24, "resolution_hours": 72},
            "medium": {"response_hours": 8, "resolution_hours": 24},
            "high": {"response_hours": 4, "resolution_hours": 12},
            "urgent": {"response_hours": 1, "resolution_hours": 4},
            "critical": {"response_hours": 0.5, "resolution_hours": 2}
        }
        sla = sla_targets.get(priority, sla_targets["medium"])
        
        ticket = {
            "ticket_id": ticket_id,
            "created_at": created_at.isoformat(),
            "updated_at": created_at.isoformat(),
            "status": "open",
            "priority": priority,
            "customer": {
                "id": customer.get("id", "unknown"),
                "name": customer.get("name", "Customer"),
                "email": customer.get("email", ""),
                "company": customer.get("company", ""),
                "plan": customer.get("plan", "free")
            },
            "issue": {
                "subject": issue.get("subject", "Support Request"),
                "description": issue.get("description", ""),
                "category": issue.get("category", "general"),
                "subcategory": issue.get("subcategory", ""),
                "product_area": issue.get("product_area", ""),
                "reproducible": issue.get("reproducible", None),
                "environment": issue.get("environment", {})
            },
            "sla": {
                "first_response_due": (created_at + timedelta(hours=sla["response_hours"])).isoformat(),
                "resolution_due": (created_at + timedelta(hours=sla["resolution_hours"])).isoformat(),
                "first_response_at": None,
                "resolved_at": None,
                "breached": False
            },
            "assignee": None,
            "tags": issue.get("tags", []),
            "conversation": [],
            "internal_notes": [],
            "satisfaction_rating": None
        }
        
        # Save ticket
        tickets_dir = Path("support/tickets")
        tickets_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{ticket_id}.json"
        filepath = tickets_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(ticket, f, indent=2)
        
        self.metrics["tickets_created"] += 1
        
        return {
            "status": "success",
            "ticket": ticket,
            "filepath": str(filepath),
            "message": f"Created ticket {ticket_id} with {priority} priority"
        }

    async def respond_to_ticket(
        self,
        ticket_id: str,
        response: str,
        is_internal: bool = False,
        author: str = "Support Agent"
    ) -> Dict[str, Any]:
        """Add response to ticket"""
        
        tickets_dir = Path("support/tickets")
        filepath = tickets_dir / f"{ticket_id}.json"
        
        if not filepath.exists():
            return {"status": "error", "message": f"Ticket {ticket_id} not found"}
        
        with open(filepath, 'r') as f:
            ticket = json.load(f)
        
        message = {
            "id": f"msg_{datetime.now().strftime('%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "author": author,
            "content": response,
            "is_internal": is_internal
        }
        
        if is_internal:
            ticket["internal_notes"].append(message)
        else:
            ticket["conversation"].append(message)
            # Set first response time if this is the first response
            if ticket["sla"]["first_response_at"] is None:
                ticket["sla"]["first_response_at"] = message["timestamp"]
        
        ticket["updated_at"] = message["timestamp"]
        
        with open(filepath, 'w') as f:
            json.dump(ticket, f, indent=2)
        
        return {
            "status": "success",
            "ticket_id": ticket_id,
            "message_id": message["id"],
            "message": f"Added {'internal note' if is_internal else 'response'} to ticket {ticket_id}"
        }

    async def resolve_ticket(
        self,
        ticket_id: str,
        resolution: str,
        resolved_by: str = "Support Agent"
    ) -> Dict[str, Any]:
        """Resolve support ticket"""
        
        tickets_dir = Path("support/tickets")
        filepath = tickets_dir / f"{ticket_id}.json"
        
        if not filepath.exists():
            return {"status": "error", "message": f"Ticket {ticket_id} not found"}
        
        with open(filepath, 'r') as f:
            ticket = json.load(f)
        
        ticket["status"] = "resolved"
        ticket["sla"]["resolved_at"] = datetime.now().isoformat()
        ticket["resolution"] = {
            "summary": resolution,
            "resolved_by": resolved_by,
            "resolved_at": ticket["sla"]["resolved_at"]
        }
        ticket["updated_at"] = ticket["sla"]["resolved_at"]
        
        # Add resolution message to conversation
        ticket["conversation"].append({
            "id": f"msg_resolution_{datetime.now().strftime('%H%M%S')}",
            "timestamp": ticket["sla"]["resolved_at"],
            "author": resolved_by,
            "content": f"✓ Issue resolved: {resolution}",
            "is_internal": False
        })
        
        with open(filepath, 'w') as f:
            json.dump(ticket, f, indent=2)
        
        self.metrics["tickets_resolved"] += 1
        
        # Update metrics
        if ticket["sla"]["first_response_at"]:
            created = datetime.fromisoformat(ticket["created_at"])
            responded = datetime.fromisoformat(ticket["sla"]["first_response_at"])
            response_time = (responded - created).total_seconds() / 3600
            self.metrics["avg_response_time_hours"] = (
                (self.metrics["avg_response_time_hours"] * (self.metrics["tickets_resolved"] - 1) + response_time) 
                / self.metrics["tickets_resolved"]
            )
        
        return {
            "status": "success",
            "ticket_id": ticket_id,
            "resolution": resolution,
            "message": f"Resolved ticket {ticket_id}"
        }

    async def create_kb_article(
        self,
        article_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create knowledge base article"""
        
        article_id = f"KB-{datetime.now().strftime('%Y%m%d')}-{hash(article_data.get('title', '')) % 10000:04d}"
        
        article = {
            "article_id": article_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": article_data.get("status", "draft"),
            "title": article_data.get("title", "Untitled Article"),
            "slug": article_data.get("slug", article_data.get("title", "").lower().replace(" ", "-")),
            "category": article_data.get("category", "General"),
            "tags": article_data.get("tags", []),
            "content": {
                "introduction": article_data.get("introduction", ""),
                "steps": article_data.get("steps", []),
                "troubleshooting": article_data.get("troubleshooting", []),
                "related_articles": article_data.get("related_articles", []),
                "faq": article_data.get("faq", [])
            },
            "metadata": {
                "author": article_data.get("author", "Support Team"),
                "reviewer": article_data.get("reviewer", ""),
                "version": article_data.get("version", "1.0"),
                "last_reviewed": None,
                "view_count": 0,
                "helpful_count": 0,
                "not_helpful_count": 0
            },
            "seo": {
                "meta_title": article_data.get("meta_title", ""),
                "meta_description": article_data.get("meta_description", ""),
                "keywords": article_data.get("keywords", [])
            }
        }
        
        # Save article
        kb_dir = Path("support/knowledge_base")
        kb_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{article_id}_{article['slug']}.json"
        filepath = kb_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(article, f, indent=2)
        
        return {
            "status": "success",
            "article": article,
            "filepath": str(filepath),
            "message": f"Created knowledge base article: {article['title']}"
        }

    async def get_support_metrics(self) -> Dict[str, Any]:
        """Get comprehensive support metrics"""
        
        # Calculate derived metrics
        if self.metrics["tickets_created"] > 0:
            self.metrics["first_contact_resolution_rate"] = (
                self.metrics["tickets_resolved"] / self.metrics["tickets_created"] * 100
            )
        
        return {
            "worker_name": self.name,
            "version": self.version,
            "specialties": self.specialties,
            "metrics": self.metrics,
            "performance_summary": {
                "ticket_volume": self.metrics["tickets_created"],
                "resolution_rate": f"{(self.metrics['tickets_resolved'] / max(self.metrics['tickets_created'], 1)) * 100:.1f}%",
                "customer_satisfaction": f"{self.metrics['csat_score']}/5.0" if self.metrics['csat_score'] > 0 else "No ratings yet",
                "net_promoter_score": self.metrics['nps_score'],
                "sla_compliance": "Good" if self.metrics["avg_response_time_hours"] < 4 else "Needs attention"
            },
            "timestamp": datetime.now().isoformat()
        }

    async def get_metrics(self) -> Dict[str, Any]:
        """Get worker performance metrics"""
        return await self.get_support_metrics()
