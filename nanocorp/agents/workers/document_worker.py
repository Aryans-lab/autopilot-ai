"""
Document Worker Agent
Specializes in creating business documents, reports, and proposals
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from openhands.sdk import LLM, Tool



from ..ceo_agent import WorkerAgent
from ..task_manager import Task


DOCUMENT_SYSTEM_PROMPT = """You are Document, a specialized document creation agent at NanoCorp.

Your expertise includes:
- Business proposals
- Reports and whitepapers
- Company documentation
- Project plans
- Meeting notes
- Process documentation
- Presentations
- Press releases
- Terms of service and policies
- User guides

You create professional, well-structured documents that are ready to use.
"""


class DocumentWorker(WorkerAgent):
    """Worker agent specialized in document creation"""
    
    def __init__(self, llm: LLM, workspace_path: Path):
        super().__init__(
            name="Document",
            description="Document creation specialist - creates business docs, reports, proposals, and more",
            specialties=[
                "Business Proposals",
                "Reports",
                "Whitepapers",
                "Business Plans",
                "Meeting Notes",
                "Process Documentation",
                "Press Releases",
                "Policies",
                "User Guides",
                "Presentations"
            ],
            llm=llm,
            workspace_path=workspace_path,
            tools=[]
        )
        self.documents_created: List[Dict[str, Any]] = []
    
    def create_business_proposal(
        self,
        client_name: str,
        project_name: str,
        services: List[str],
        pricing: str,
        timeline: str
    ) -> Dict[str, Any]:
        """Create a business proposal document"""
        workspace = self.workspace_path / "documents" / "proposals"
        workspace.mkdir(parents=True, exist_ok=True)
        
        proposal_content = f"""# Business Proposal

**Prepared for:** {client_name}
**Project:** {project_name}
**Date:** {datetime.now().strftime('%B %d, %Y')}

---

## Executive Summary

This proposal outlines our approach to {project_name} for {client_name}. We are excited about this opportunity and confident in our ability to deliver exceptional results.

## Understanding Your Needs

We understand that {client_name} is seeking professional services for {project_name}. Our team has carefully analyzed your requirements and developed a comprehensive solution.

## Proposed Services

{chr(10).join(f"- **{svc}**: Professional {svc.lower()} services tailored to your specific needs" for svc in services)}

## Investment

{pricing}

## Timeline

{timeline}

## Why Choose Us

✓ **Experience**: Extensive track record in delivering similar projects
✓ **Quality**: Commitment to excellence in every deliverable
✓ **Communication**: Regular updates and transparent processes
✓ **Support**: Ongoing assistance even after project completion

## Next Steps

1. Review this proposal
2. Schedule a call to discuss any questions
3. Provide approval to begin work
4. We commence immediately upon agreement

---

**Prepared by:** NanoCorp
**Contact:** info@nanocorp.io
"""
        
        proposal_file = workspace / f"proposal-{project_name.lower().replace(' ', '-')}.md"
        with open(proposal_file, 'w') as f:
            f.write(proposal_content)
        
        doc_info = {
            "type": "business_proposal",
            "client": client_name,
            "project": project_name,
            "path": str(proposal_file),
            "created_at": datetime.now().isoformat()
        }
        self.documents_created.append(doc_info)
        
        return doc_info
    
    def create_meeting_notes(
        self,
        meeting_title: str,
        date: str,
        attendees: List[str],
        agenda: List[str],
        discussion_points: List[str],
        action_items: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Create meeting notes document"""
        workspace = self.workspace_path / "documents" / "meetings"
        workspace.mkdir(parents=True, exist_ok=True)
        
        action_items_text = "\n".join(
            f"- [ ] **{item.get('task', 'Task')}** - {item.get('assignee', 'Unassigned')} - Due: {item.get('due', 'TBD')}"
            for item in action_items
        )
        
        notes_content = f"""# Meeting Notes

**Title:** {meeting_title}
**Date:** {date}
**Attendees:** {', '.join(attendees)}

---

## Agenda

{chr(10).join(f"{i+1}. {item}" for i, item in enumerate(agenda))}

## Discussion Summary

{chr(10).join(f"- {point}" for point in discussion_points)}

## Action Items

{action_items_text if action_items_text else "No action items identified."}

## Next Meeting

**Date:** TBD
**Topics:** TBD

---

*Notes taken by: NanoCorp AI*
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        
        notes_file = workspace / f"meeting-{meeting_title.lower().replace(' ', '-')}-{date}.md"
        with open(notes_file, 'w') as f:
            f.write(notes_content)
        
        doc_info = {
            "type": "meeting_notes",
            "title": meeting_title,
            "date": date,
            "path": str(notes_file),
            "created_at": datetime.now().isoformat(),
            "action_items_count": len(action_items)
        }
        self.documents_created.append(doc_info)
        
        return doc_info
    
    def create_business_plan(
        self,
        company_name: str,
        business_idea: str,
        target_market: str,
        revenue_model: str,
        competitive_advantage: str
    ) -> Dict[str, Any]:
        """Create a comprehensive business plan"""
        workspace = self.workspace_path / "documents" / "business_plans"
        workspace.mkdir(parents=True, exist_ok=True)
        
        plan_content = f"""# Business Plan: {company_name}

**Version:** 1.0
**Date:** {datetime.now().strftime('%B %Y')}
**Prepared by:** {company_name} Team

---

## 1. Executive Summary

{company_name} is a pioneering venture focused on {business_idea}. Our mission is to transform the industry through innovation and exceptional value delivery.

### Key Highlights
- **Founded:** {datetime.now().strftime('%Y')}
- **Headquarters:** [Your Location]
- **Industry:** [Your Industry]
- **Stage:** [Seed/Series A/etc.]

---

## 2. Problem Statement

[Describe the problem you're solving]

### Pain Points
- [Pain point 1]
- [Pain point 2]
- [Pain point 3]

---

## 3. Solution

{business_idea}

### Product/Service Offering
- **Primary Product:** [Description]
- **Secondary Products:** [List]
- **Future Roadmap:** [Vision]

---

## 4. Target Market

**Primary Market:** {target_market}

### Market Size
- **TAM:** $XX Billion
- **SAM:** $X Billion
- **SOM:** $XXX Million

### Customer Segments
- [Segment 1]
- [Segment 2]
- [Segment 3]

---

## 5. Business Model

**Revenue Model:** {revenue_model}

### Revenue Streams
- [Stream 1]
- [Stream 2]

### Pricing Strategy
[Your pricing approach]

---

## 6. Competitive Landscape

**Competitive Advantage:** {competitive_advantage}

### Direct Competitors
| Competitor | Strengths | Weaknesses |
|------------|-----------|------------|
| [Name] | [X] | [Y] |
| [Name] | [X] | [Y] |

### Our Moat
- [Advantage 1]
- [Advantage 2]
- [Advantage 3]

---

## 7. Go-to-Market Strategy

### Phase 1: Launch (Months 1-3)
- [X]
- [Y]

### Phase 2: Growth (Months 4-6)
- [X]
- [Y]

### Phase 3: Scale (Months 7-12)
- [X]
- [Y]

---

## 8. Team

| Role | Name | Background |
|------|------|------------|
| CEO | [Name] | [Background] |
| CTO | [Name] | [Background] |
| [Role] | [Name] | [Background] |

---

## 9. Financial Projections

### Year 1
- **Revenue:** $[Amount]
- **Expenses:** $[Amount]
- **Net Income:** $[Amount]

### Year 2
- **Revenue:** $[Amount]
- **Growth:** XX%

### Year 3
- **Revenue:** $[Amount]
- **Growth:** XX%

---

## 10. Funding Requirements

**Amount Sought:** $[Amount]
**Use of Funds:**
- Product Development: XX%
- Marketing: XX%
- Operations: XX%
- Team: XX%

---

## 11. Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [Risk 1] | [H/M/L] | [H/M/L] | [Strategy] |

---

## 12. Milestones

- [ ] Q1: [Milestone]
- [ ] Q2: [Milestone]
- [ ] Q3: [Milestone]
- [ ] Q4: [Milestone]

---

*This business plan is confidential and intended solely for the use of the individual or entity to which it is addressed.*
"""
        
        plan_file = workspace / f"business-plan-{company_name.lower().replace(' ', '-')}.md"
        with open(plan_file, 'w') as f:
            f.write(plan_content)
        
        doc_info = {
            "type": "business_plan",
            "company": company_name,
            "path": str(plan_file),
            "created_at": datetime.now().isoformat()
        }
        self.documents_created.append(doc_info)
        
        return doc_info
    
    def create_press_release(
        self,
        company_name: str,
        headline: str,
        subheadline: str,
        story_body: str,
        quote: str,
        contact_info: str
    ) -> Dict[str, Any]:
        """Create a press release document"""
        workspace = self.workspace_path / "documents" / "press_releases"
        workspace.mkdir(parents=True, exist_ok=True)
        
        release_content = f"""FOR IMMEDIATE RELEASE

{headline}

{subheadline}

---

{company_name} today announced [major news/milestone/launch]. This [strategic move/exciting development/significant achievement] marks [important context].

"{quote}"

— [Name], [Title], {company_name}

{story_body}

About {company_name}
{company_name} is [brief company description]. Founded in {datetime.now().strftime('%Y')}, the company is dedicated to [mission/purpose].

### Media Contact
{contact_info}

###
"""
        
        release_file = workspace / f"press-release-{headline.lower().replace(' ', '-')[:30]}.md"
        with open(release_file, 'w') as f:
            f.write(release_content)
        
        doc_info = {
            "type": "press_release",
            "company": company_name,
            "headline": headline,
            "path": str(release_file),
            "created_at": datetime.now().isoformat()
        }
        self.documents_created.append(doc_info)
        
        return doc_info
    
    def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a document task"""
        context = task.context
        
        if context.get("action") == "create_proposal":
            result = self.create_business_proposal(
                client_name=context.get("client_name", ""),
                project_name=context.get("project_name", ""),
                services=context.get("services", []),
                pricing=context.get("pricing", ""),
                timeline=context.get("timeline", "")
            )
            return {"success": True, "type": "proposal", "data": result}
        
        elif context.get("action") == "create_meeting_notes":
            result = self.create_meeting_notes(
                meeting_title=context.get("meeting_title", ""),
                date=context.get("date", datetime.now().strftime('%Y-%m-%d')),
                attendees=context.get("attendees", []),
                agenda=context.get("agenda", []),
                discussion_points=context.get("discussion_points", []),
                action_items=context.get("action_items", [])
            )
            return {"success": True, "type": "meeting_notes", "data": result}
        
        elif context.get("action") == "create_business_plan":
            result = self.create_business_plan(
                company_name=context.get("company_name", ""),
                business_idea=context.get("business_idea", ""),
                target_market=context.get("target_market", ""),
                revenue_model=context.get("revenue_model", ""),
                competitive_advantage=context.get("competitive_advantage", "")
            )
            return {"success": True, "type": "business_plan", "data": result}
        
        elif context.get("action") == "create_press_release":
            result = self.create_press_release(
                company_name=context.get("company_name", ""),
                headline=context.get("headline", ""),
                subheadline=context.get("subheadline", ""),
                story_body=context.get("story_body", ""),
                quote=context.get("quote", ""),
                contact_info=context.get("contact_info", "")
            )
            return {"success": True, "type": "press_release", "data": result}
        
        prompt = f"""Create a document for this task:

Title: {task.title}
Description: {task.description}

Context:
{json.dumps(context, indent=2)}

Create the appropriate document. Report what you created.
"""
        
        response = self.conversation.send_message(prompt)
        
        return {
            "success": True,
            "response": response,
            "documents_created": self.documents_created
        }
