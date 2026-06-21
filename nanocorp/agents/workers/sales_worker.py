"""SalesWorker 2.0 - Elite Sales Automation & Revenue Generation"""

import os
from typing import Dict, List, Any
from datetime import datetime, timedelta
from pathlib import Path

from .base import BaseWorker


class SalesWorker(BaseWorker):
    """Elite Sales Professional for revenue generation"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "SalesWorker"
        self.version = "2.0"
        self.specialties = ["Lead Gen", "Outreach", "CRM", "Closing", "Negotiation"]
        
        self.metrics = {
            "leads_generated": 0, "outreach_sent": 0, "meetings_booked": 0,
            "deals_closed": 0, "revenue_generated": 0.0, "conversion_rate": 0.0
        }
        
        self.system_prompt = "You are a world-class Sales Professional who generates leads, builds relationships, and closes deals."

    async def generate_leads(self, icp: Dict[str, Any], limit: int = 20) -> Dict[str, Any]:
        """Generate qualified leads"""
        leads = []
        for i in range(limit):
            leads.append({
                "id": f"lead_{i}", "company": f"Company {i}",
                "contact": f"Contact {i}", "email": f"contact{i}@company.com",
                "score": 85 - i * 2
            })
        self.metrics["leads_generated"] += len(leads)
        return {"status": "success", "leads": leads, "count": len(leads)}

    async def create_outreach_sequence(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Create personalized outreach sequence"""
        sequence = {
            "emails": [
                f"Hi {lead.get('contact', 'there')}, I noticed {lead.get('company', 'your company')}...",
                "Following up on my previous note...",
                "Last try - feel free to reach out when timing is better..."
            ],
            "linkedin": ["Connection request", "Follow-up message"]
        }
        self.metrics["outreach_sent"] += len(sequence["emails"])
        return {"status": "success", "sequence": sequence}

    async def create_proposal(self, deal_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sales proposal"""
        proposal = {
            "title": f"Proposal for {deal_info.get('company', 'Client')}",
            "value": deal_info.get("value", 50000),
            "sections": ["Executive Summary", "Solution", "Investment", "Timeline"],
            "created": datetime.now().isoformat()
        }
        filepath = Path("proposals") / f"proposal_{datetime.now().strftime('%Y%m%d')}.json"
        filepath.parent.mkdir(exist_ok=True)
        with open(filepath, 'w') as f:
            import json
            json.dump(proposal, f, indent=2)
        return {"status": "success", "proposal": proposal, "filepath": str(filepath)}

    async def get_metrics(self) -> Dict[str, Any]:
        return {**self.metrics, "worker": self.name, "timestamp": datetime.now().isoformat()}
