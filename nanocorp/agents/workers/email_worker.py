"""
Email Worker Agent
Specializes in email campaigns, newsletters, and outreach
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from openhands.sdk import LLM, Tool

from ..ceo_agent import WorkerAgent
from ..task_manager import Task


EMAIL_SYSTEM_PROMPT = """You are Email, a specialized email marketing agent at NanoCorp.

Your expertise includes:
- Email campaign strategy
- Newsletter creation
- Cold email outreach
- Email sequence design
- A/B testing for emails
- Subject line optimization
- Email deliverability
- Personalization strategies
- Drip campaign automation
- Follow-up sequences

You create compelling emails that get opened and drive action.
"""


class EmailWorker(WorkerAgent):
    """Worker agent specialized in email marketing"""
    
    def __init__(self, llm: LLM, workspace_path: Path):
        super().__init__(
            name="Email",
            description="Email marketing specialist - creates email campaigns, newsletters, and outreach sequences",
            specialties=[
                "Email Campaigns",
                "Newsletter Creation",
                "Cold Outreach",
                "Drip Sequences",
                "Follow-up Emails",
                "Personalization",
                "A/B Testing",
                "Subject Line Writing",
                "Email Automation",
                "Deliverability Optimization"
            ],
            llm=llm,
            workspace_path=workspace_path,
            tools=[]  # Will use default tools
        )
        self.emails_created: List[Dict[str, Any]] = []
    
    def create_newsletter(
        self,
        company_name: str,
        edition: str,
        sections: List[Dict[str, str]],
        brand_color: str = "#2563EB"
    ) -> Dict[str, Any]:
        """Create a newsletter email"""
        workspace = self.workspace_path / "email" / "newsletters"
        workspace.mkdir(parents=True, exist_ok=True)
        
        sections_html = "\n".join(
            f'''
            <tr>
                <td style="padding: 20px; border-bottom: 1px solid #eee;">
                    <h3 style="color: {brand_color}; margin-bottom: 10px;">{sec.get('title', '')}</h3>
                    <p>{sec.get('content', '')}</p>
                </td>
            </tr>'''
            for sec in sections
        )
        
        email_html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{edition} - {company_name} Newsletter</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4;">
        <tr>
            <td align="center" style="padding: 40px 10px;">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, {brand_color} 0%, #1e40af 100%); padding: 30px; text-align: center;">
                            <h1 style="color: white; margin: 0; font-size: 24px;">{company_name}</h1>
                            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0;">{edition}</p>
                        </td>
                    </tr>
                    <!-- Content -->
                    <tr>
                        <td style="padding: 0;">
                            <table width="100%" cellpadding="0" cellspacing="0">
                                {sections_html}
                            </table>
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666;">
                            <p style="margin: 0;">© 2024 {company_name}. All rights reserved.</p>
                            <p style="margin: 10px 0 0;"><a href="#" style="color: {brand_color};">Unsubscribe</a> | <a href="#" style="color: {brand_color};">View in browser</a></p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
'''
        
        email_file = workspace / f"newsletter-{edition.lower().replace(' ', '-')}.html"
        with open(email_file, 'w') as f:
            f.write(email_html)
        
        email_info = {
            "type": "newsletter",
            "edition": edition,
            "company": company_name,
            "path": str(email_file),
            "created_at": datetime.now().isoformat(),
            "sections_count": len(sections)
        }
        self.emails_created.append(email_info)
        
        return email_info
    
    def create_cold_email(
        self,
        prospect_name: str,
        prospect_company: str,
        sender_name: str,
        product_value_prop: str,
        email_type: str = "initial"
    ) -> Dict[str, Any]:
        """Create a cold outreach email"""
        workspace = self.workspace_path / "email" / "outreach"
        workspace.mkdir(parents=True, exist_ok=True)
        
        templates = {
            "initial": f"""Subject: Quick question about {prospect_company}

Hi {prospect_name},

I noticed {prospect_company} and thought there might be an opportunity to help.

{product_value_prop}

Would you be open to a quick 15-minute call this week?

Best,
{sender_name}""",
            "follow_up": f"""Subject: Re: Quick question about {prospect_company}

Hi {prospect_name},

Just following up on my previous email. I'd love to show you how we can help {prospect_company} achieve better results.

Would you have 15 minutes this week for a quick chat?

Best,
{sender_name}""",
            "breakup": f"""Subject: Last note - {prospect_company}

Hi {prospect_name},

I haven't heard back from you, so I'll close the loop here. If you ever want to explore how we can help {prospect_company}, feel free to reach out.

Wishing you success,
{sender_name}"""
        }
        
        email_content = templates.get(email_type, templates["initial"])
        
        email_file = workspace / f"cold-email-{prospect_name.lower().replace(' ', '-')}-{email_type}.txt"
        with open(email_file, 'w') as f:
            f.write(email_content)
        
        email_info = {
            "type": "cold_email",
            "prospect": prospect_name,
            "company": prospect_company,
            "email_type": email_type,
            "path": str(email_file),
            "created_at": datetime.now().isoformat()
        }
        self.emails_created.append(email_info)
        
        return email_info
    
    def create_drip_sequence(
        self,
        sequence_name: str,
        product_name: str,
        prospect_type: str,
        stages: int = 5
    ) -> Dict[str, Any]:
        """Create a drip email sequence"""
        workspace = self.workspace_path / "email" / "sequences"
        workspace.mkdir(parents=True, exist_ok=True)
        
        sequence_content = f"""# Drip Sequence: {sequence_name}

Product: {product_name}
Target: {prospect_type}
Total Emails: {stages}

## Email Sequence Overview

"""
        
        for i in range(1, stages + 1):
            delay = (i - 1) * 3  # 3 days between emails
            sequence_content += f"""### Email {i} (Day {delay + 1})
---
**Subject**: [Personalized based on trigger]

**Timing**: Day {delay + 1}

"""
            
            if i == 1:
                sequence_content += f"""**Trigger**: When {prospect_type} signs up/downloads content
**Purpose**: Welcome and deliver value

**Content**:
- Personal greeting
- Quick intro to {product_name}
- Valuable tip related to their signup
- Soft CTA to reply or visit website
"""
            elif i == stages:
                sequence_content += f"""**Trigger**: After {prospect_type} completes previous emails
**Purpose**: Final conversion push

**Content**:
- Recap of {product_name} benefits
- Social proof/testimonial
- Clear CTA with urgency
- What they'll miss if they don't act
"""
            else:
                sequence_content += f"""**Trigger**: Day {delay + 1} after start
**Purpose**: Nurture and educate

**Content**:
- Value-focused content
- Address common objections
- Building trust
- CTA to learn more or reply
"""
            sequence_content += "\n"
        
        sequence_file = workspace / f"sequence-{sequence_name.lower().replace(' ', '-')}.md"
        with open(sequence_file, 'w') as f:
            f.write(sequence_content)
        
        sequence_info = {
            "name": sequence_name,
            "product": product_name,
            "prospect_type": prospect_type,
            "stages": stages,
            "path": str(sequence_file),
            "created_at": datetime.now().isoformat()
        }
        self.emails_created.append(sequence_info)
        
        return sequence_info
    
    def create_promotional_email(
        self,
        product_name: str,
        offer_details: str,
        discount_code: str,
        expiry_date: str,
        brand_color: str = "#2563EB"
    ) -> Dict[str, Any]:
        """Create a promotional/sales email"""
        workspace = self.workspace_path / "email" / "promotional"
        workspace.mkdir(parents=True, exist_ok=True)
        
        email_html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Special Offer - {product_name}</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
            <td align="center" style="padding: 40px 10px;">
                <table width="600" cellpadding="0" cellspacing="0" style="background: white; border-radius: 8px;">
                    <tr>
                        <td style="background: {brand_color}; padding: 40px; text-align: center;">
                            <h1 style="color: white; margin: 0; font-size: 28px;">🎉 Special Offer!</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 40px; text-align: center;">
                            <h2 style="color: #333; margin: 0 0 20px;">{product_name}</h2>
                            <p style="font-size: 18px; color: #666; line-height: 1.6;">{offer_details}</p>
                            <div style="background: #f8f9fa; padding: 20px; margin: 30px 0; border-radius: 8px;">
                                <p style="margin: 0; color: #888; font-size: 14px;">Use code:</p>
                                <p style="margin: 10px 0 0; font-size: 24px; font-weight: bold; color: {brand_color};">{discount_code}</p>
                            </div>
                            <p style="color: #e74c3c; font-weight: bold;">⏰ Offer expires: {expiry_date}</p>
                            <a href="#" style="display: inline-block; background: {brand_color}; color: white; padding: 15px 40px; text-decoration: none; border-radius: 50px; font-weight: bold; margin-top: 20px;">Claim Your Offer</a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
'''
        
        email_file = workspace / f"promo-{product_name.lower().replace(' ', '-')}.html"
        with open(email_file, 'w') as f:
            f.write(email_html)
        
        email_info = {
            "type": "promotional",
            "product": product_name,
            "discount_code": discount_code,
            "expiry": expiry_date,
            "path": str(email_file),
            "created_at": datetime.now().isoformat()
        }
        self.emails_created.append(email_info)
        
        return email_info
    
    def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute an email task"""
        context = task.context
        
        if context.get("action") == "create_newsletter":
            result = self.create_newsletter(
                company_name=context.get("company_name", "Company"),
                edition=context.get("edition", "Monthly Update"),
                sections=context.get("sections", []),
                brand_color=context.get("brand_color", "#2563EB")
            )
            return {"success": True, "type": "newsletter", "data": result}
        
        elif context.get("action") == "create_cold_email":
            result = self.create_cold_email(
                prospect_name=context.get("prospect_name", ""),
                prospect_company=context.get("prospect_company", ""),
                sender_name=context.get("sender_name", ""),
                product_value_prop=context.get("product_value_prop", ""),
                email_type=context.get("email_type", "initial")
            )
            return {"success": True, "type": "cold_email", "data": result}
        
        elif context.get("action") == "create_drip_sequence":
            result = self.create_drip_sequence(
                sequence_name=context.get("sequence_name", ""),
                product_name=context.get("product_name", ""),
                prospect_type=context.get("prospect_type", ""),
                stages=context.get("stages", 5)
            )
            return {"success": True, "type": "drip_sequence", "data": result}
        
        elif context.get("action") == "create_promotional_email":
            result = self.create_promotional_email(
                product_name=context.get("product_name", ""),
                offer_details=context.get("offer_details", ""),
                discount_code=context.get("discount_code", ""),
                expiry_date=context.get("expiry_date", ""),
                brand_color=context.get("brand_color", "#2563EB")
            )
            return {"success": True, "type": "promotional", "data": result}
        
        prompt = f"""Create an email solution for this task:

Title: {task.title}
Description: {task.description}

Context:
{json.dumps(context, indent=2)}

Create the appropriate email content. Report what you created.
"""
        
        response = self.conversation.send_message(prompt)
        
        return {
            "success": True,
            "response": response,
            "emails_created": self.emails_created
        }
