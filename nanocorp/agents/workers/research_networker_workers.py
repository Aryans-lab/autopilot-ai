"""
Researcher and Networker Worker Agents
Specializes in market research, competitive analysis, and networking
"""
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from openhands.sdk import LLM, Tool

from ..ceo_agent import WorkerAgent
from ..task_manager import Task


RESEARCHER_SYSTEM_PROMPT = """You are Researcher, a specialized research agent at NanoCorp.

Your expertise includes:
- Market research and analysis
- Competitive intelligence
- Industry trends analysis
- Data gathering and synthesis
- SWOT analysis
- Customer research
- Product research

You deliver actionable insights based on thorough research.
"""


class ResearcherWorker(WorkerAgent):
    """Worker agent specialized in research"""
    
    def __init__(self, llm: LLM, workspace_path: Path):
        super().__init__(
            name="Researcher",
            description="Research specialist - conducts market research, competitive analysis, and data gathering",
            specialties=[
                "Market Research",
                "Competitive Analysis",
                "Industry Trends",
                "SWOT Analysis",
                "Customer Research",
                "Product Research",
            ],
            llm=llm,
            workspace_path=workspace_path,
            tools=[]
        )
        self.research_reports: List[Dict[str, Any]] = []
    
    def create_market_research(
        self,
        market_name: str,
        market_size: str,
        target_segments: List[str],
        key_trends: List[str],
        opportunities: List[str]
    ) -> Dict[str, Any]:
        """Create a market research report"""
        workspace = self.workspace_path / "research" / "market"
        workspace.mkdir(parents=True, exist_ok=True)
        
        segments_text = "\n".join("- **" + seg + "**" for seg in target_segments)
        trends_text = "\n".join(str(i+1) + ". **" + trend + "**" for i, trend in enumerate(key_trends))
        opps_text = "\n".join("- **" + opp + "**" for opp in opportunities)
        
        report_content = (
            "# Market Research Report: " + market_name + "\n\n" +
            "**Report Date:** " + datetime.now().strftime('%B %d, %Y') + "\n" +
            "**Prepared by:** NanoCorp Research Team\n\n" +
            "---\n\n## Executive Summary\n\n" +
            "This report provides a comprehensive analysis of the " + market_name + " market.\n\n" +
            "## Market Overview\n\n### Market Size\n" + market_size + "\n\n" +
            "### Target Customer Segments\n" + segments_text + "\n\n" +
            "## Key Trends\n\n" + trends_text + "\n\n" +
            "## Opportunities\n\n" + opps_text + "\n\n" +
            "## Recommendations\n\n" +
            "1. Focus on underserved segments\n" +
            "2. Invest in differentiation\n" +
            "3. Build strategic partnerships\n" +
            "4. Monitor trends\n"
        )
        
        report_file = workspace / ("market-research-" + market_name.lower().replace(' ', '-') + ".md")
        with open(report_file, 'w') as f:
            f.write(report_content)
        
        report_info = {
            "type": "market_research",
            "market": market_name,
            "path": str(report_file),
            "created_at": datetime.now().isoformat()
        }
        self.research_reports.append(report_info)
        return report_info
    
    def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a research task"""
        context = task.context
        
        if context.get("action") == "market_research":
            result = self.create_market_research(
                market_name=context.get("market_name", ""),
                market_size=context.get("market_size", ""),
                target_segments=context.get("target_segments", []),
                key_trends=context.get("key_trends", []),
                opportunities=context.get("opportunities", [])
            )
            return {"success": True, "type": "market_research", "data": result}
        
        prompt = "Conduct research for this task:\n\nTitle: " + task.title + "\nDescription: " + task.description
        response = self.conversation.send_message(prompt)
        return {"success": True, "response": response, "research_reports": self.research_reports}


NETWORKER_SYSTEM_PROMPT = """You are Networker, a specialized networking agent at NanoCorp.

Your expertise includes:
- Partnership outreach
- Influencer identification
- B2B networking strategies
- Event planning and follow-up
- Professional relationship building
- Cold outreach messaging
- Collaboration proposals

You build valuable professional relationships that drive business growth.
"""


class NetworkerWorker(WorkerAgent):
    """Worker agent specialized in networking and outreach"""
    
    def __init__(self, llm: LLM, workspace_path: Path):
        super().__init__(
            name="Networker",
            description="Networking specialist - builds partnerships, manages outreach, and creates opportunities",
            specialties=[
                "Partnership Development",
                "Influencer Outreach",
                "B2B Networking",
                "Event Networking",
                "Cold Outreach",
                "Collaboration Proposals",
            ],
            llm=llm,
            workspace_path=workspace_path,
            tools=[]
        )
        self.outreach_campaigns: List[Dict[str, Any]] = []
    
    def create_partnership_outreach(
        self,
        partner_type: str,
        value_proposition: str,
        collaboration_types: List[str],
        outreach_targets: List[str]
    ) -> Dict[str, Any]:
        """Create partnership outreach campaign"""
        workspace = self.workspace_path / "networking" / "partnerships"
        workspace.mkdir(parents=True, exist_ok=True)
        
        collab_text = "\n".join("- " + c for c in collaboration_types)
        targets_text = "\n".join("- " + t for t in outreach_targets)
        
        # Build outreach messages
        outreach_messages = []
        for target in outreach_targets:
            msg = (
                "### Outreach to: " + target + "\n\n" +
                "Hi [Name],\n\n" +
                "I hope this message finds you well. I'm reaching out from NanoCorp to explore a potential partnership.\n\n" +
                "**What we do:** " + value_proposition + "\n\n" +
                "**Potential collaboration areas:**\n" + collab_text + "\n\n" +
                "Would you have 20 minutes available this week?\n\n" +
                "Best regards,\n[Your Name]\nNanoCorp\n\n---\n"
            )
            outreach_messages.append(msg)
        
        outreach_section = "\n\n".join(outreach_messages)
        
        campaign_content = (
            "# Partnership Outreach Campaign\n\n" +
            "**Partner Type:** " + partner_type + "\n" +
            "**Created:** " + datetime.now().strftime('%Y-%m-%d') + "\n\n" +
            "## Value Proposition\n" + value_proposition + "\n\n" +
            "## Collaboration Types\n" + collab_text + "\n\n" +
            "## Outreach Targets\n" + targets_text + "\n\n" +
            "---\n\n" + outreach_section + "\n\n" +
            "## Follow-up Strategy\n\n" +
            "1. **Day 3:** Follow-up email if no response\n" +
            "2. **Day 7:** Second follow-up with additional value\n" +
            "3. **Day 14:** Final outreach attempt\n"
        )
        
        campaign_file = workspace / ("partnership-outreach-" + partner_type.lower().replace(' ', '-') + ".md")
        with open(campaign_file, 'w') as f:
            f.write(campaign_content)
        
        campaign_info = {
            "type": "partnership_outreach",
            "partner_type": partner_type,
            "targets_count": len(outreach_targets),
            "path": str(campaign_file),
            "created_at": datetime.now().isoformat()
        }
        self.outreach_campaigns.append(campaign_info)
        return campaign_info
    
    def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a networking task"""
        context = task.context
        
        if context.get("action") == "partnership_outreach":
            result = self.create_partnership_outreach(
                partner_type=context.get("partner_type", ""),
                value_proposition=context.get("value_proposition", ""),
                collaboration_types=context.get("collaboration_types", []),
                outreach_targets=context.get("outreach_targets", [])
            )
            return {"success": True, "type": "partnership_outreach", "data": result}
        
        prompt = "Create networking content for this task:\n\nTitle: " + task.title + "\nDescription: " + task.description
        response = self.conversation.send_message(prompt)
        return {"success": True, "response": response, "outreach_campaigns": self.outreach_campaigns}
