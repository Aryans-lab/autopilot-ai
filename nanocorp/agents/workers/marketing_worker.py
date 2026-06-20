"""
Marketing Worker Agent
Specializes in marketing strategies, campaigns, and advertising
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from openhands.sdk import LLM, Tool

from ..ceo_agent import WorkerAgent
from ..task_manager import Task


MARKETING_SYSTEM_PROMPT = """You are Marketing, a specialized marketing agent at NanoCorp.

Your expertise includes:
- Marketing strategy development
- Campaign planning and execution
- Content marketing
- Social media marketing
- Email marketing
- Advertising (Google Ads, Facebook Ads, etc.)
- SEO and content optimization
- Market analysis and positioning
- Brand development
- Conversion optimization

You create comprehensive marketing plans that drive results.
"""


class MarketingWorker(WorkerAgent):
    """Worker agent specialized in marketing"""
    
    def __init__(self, llm: LLM, workspace_path: Path):
        super().__init__(
            name="Marketing",
            description="Marketing specialist - creates marketing strategies, campaigns, and advertising",
            specialties=[
                "Marketing Strategy",
                "Campaign Planning",
                "Content Marketing",
                "Social Media Marketing",
                "Email Marketing",
                "Advertising",
                "SEO Optimization",
                "Brand Development",
                "Market Analysis",
                "Conversion Optimization"
            ],
            llm=llm,
            workspace_path=workspace_path,
            tools=[]  # Will use default tools
        )
        self.campaigns_created: List[Dict[str, Any]] = []
    
    def create_marketing_plan(
        self,
        product_name: str,
        target_audience: str,
        goals: List[str],
        budget_tier: str = "medium"
    ) -> Dict[str, Any]:
        """Create a comprehensive marketing plan"""
        workspace = self.workspace_path / "marketing" / "plans"
        workspace.mkdir(parents=True, exist_ok=True)
        
        budget_options = {
            "low": {"monthly": "$500-1000", "focus": "Organic and social media"},
            "medium": {"monthly": "$1000-5000", "focus": "Mix of organic and paid"},
            "high": {"monthly": "$5000+", "focus": "Full-funnel paid acquisition"}
        }
        budget_info = budget_options.get(budget_tier, budget_options["medium"])
        
        plan_content = f"""# Marketing Plan: {product_name}

## Executive Summary
This marketing plan outlines a comprehensive strategy to promote {product_name} to {target_audience}.

## Budget
- Monthly Budget: {budget_info['monthly']}
- Focus: {budget_info['focus']}

## Target Audience
{target_audience}

## Goals
{chr(10).join(f"- {goal}" for goal in goals)}

## Marketing Channels

### 1. Content Marketing
- Blog posts (2-4 per week)
- Educational content addressing pain points
- Case studies and testimonials
- Video content for YouTube/TikTok

### 2. Social Media Marketing
- LinkedIn: Professional content, industry insights
- Twitter/X: Engagement, trending topics
- Instagram: Visual content, behind-the-scenes
- TikTok: Short-form viral content

### 3. Email Marketing
- Weekly newsletter
- Drip campaigns for new subscribers
- Promotional emails (2-3 per month)
- Personalized outreach sequences

### 4. Paid Advertising
- Google Ads: Search campaigns targeting key terms
- Facebook/Instagram Ads: Retargeting and lookalike audiences
- LinkedIn Ads: B2B targeting

### 5. SEO
- On-page optimization
- Backlink building strategy
- Local SEO if applicable
- Technical SEO audit

## Timeline
- Month 1-2: Foundation and content creation
- Month 3-4: Launch campaigns and optimize
- Month 5-6: Scale successful channels

## KPIs
- Website traffic growth
- Lead generation
- Conversion rates
- Social engagement metrics
- Email open and click rates
- ROI by channel

## Implementation

### Week 1-2: Setup
- [ ] Finalize brand messaging
- [ ] Set up analytics (Google Analytics, social insights)
- [ ] Create content calendar
- [ ] Design email templates

### Week 3-4: Content Production
- [ ] Create 8-10 blog posts
- [ ] Design social media graphics
- [ ] Record and edit videos
- [ ] Set up advertising accounts

### Week 5-8: Launch
- [ ] Publish content on schedule
- [ ] Launch email campaigns
- [ ] Start paid advertising
- [ ] Monitor and optimize
"""
        
        plan_file = workspace / f"{product_name.lower().replace(' ', '-')}-marketing-plan.md"
        with open(plan_file, 'w') as f:
            f.write(plan_content)
        
        campaign_info = {
            "name": product_name,
            "type": "marketing_plan",
            "path": str(plan_file),
            "created_at": datetime.now().isoformat(),
            "budget_tier": budget_tier,
            "target_audience": target_audience
        }
        self.campaigns_created.append(campaign_info)
        
        return campaign_info
    
    def create_campaign(
        self,
        campaign_name: str,
        campaign_type: str,
        channels: List[str],
        target_audience: str,
        call_to_action: str,
        duration_weeks: int = 4
    ) -> Dict[str, Any]:
        """Create a specific marketing campaign"""
        workspace = self.workspace_path / "marketing" / "campaigns"
        workspace.mkdir(parents=True, exist_ok=True)
        
        channel_tactics = {
            "social": "- Daily posts across platforms\n- Engagement campaigns\n- Influencer partnerships\n- Community management",
            "email": "- Welcome sequence\n- Educational series\n- Promotional offers\n- Re-engagement campaigns",
            "content": "- Blog posts\n- Video content\n- Infographics\n- Podcasts",
            "ads": "- A/B testing creative\n- Audience segmentation\n- Retargeting sequences\n- Budget optimization",
            "seo": "- Keyword optimization\n- Content updates\n- Link building\n- Technical improvements"
        }
        
        tactics = "\n".join(channel_tactics.get(ch, "- Standard tactics") for ch in channels)
        
        campaign_content = f"""# Campaign: {campaign_name}

## Overview
- **Type**: {campaign_type}
- **Duration**: {duration_weeks} weeks
- **Target Audience**: {target_audience}

## Call to Action
{call_to_action}

## Channel Strategy

{chr(10).join(f"### {ch.upper()}" + ("\n" + channel_tactics.get(ch, "")) for ch in channels)}

## Weekly Schedule

### Week 1: Launch
- Campaign kickoff
- Initial content distribution
- Set up tracking

### Week 2: Engagement
- Amplify top-performing content
- Community engagement
- First performance review

### Week 3: Optimization
- Adjust based on metrics
- Scale successful tactics
- A/B testing

### Week 4: Wrap-up
- Final push
- Analysis and reporting
- Recommendations for next campaign

## Budget Allocation
{chr(10).join(f"- {ch}: ~{100//len(channels)}%" for ch in channels)}

## Success Metrics
- Reach and impressions
- Engagement rate
- Click-through rate
- Conversions
- Cost per acquisition
- Return on ad spend (ROAS)
"""
        
        campaign_file = workspace / f"{campaign_name.lower().replace(' ', '-')}-campaign.md"
        with open(campaign_file, 'w') as f:
            f.write(campaign_content)
        
        campaign_info = {
            "name": campaign_name,
            "type": campaign_type,
            "channels": channels,
            "path": str(campaign_file),
            "created_at": datetime.now().isoformat(),
            "duration_weeks": duration_weeks
        }
        self.campaigns_created.append(campaign_info)
        
        return campaign_info
    
    def create_ad_variants(
        self,
        product_name: str,
        product_description: str,
        ad_platforms: List[str] = None
    ) -> Dict[str, Any]:
        """Create ad copy variants for different platforms"""
        if ad_platforms is None:
            ad_platforms = ["google", "facebook", "linkedin", "twitter"]
        
        workspace = self.workspace_path / "marketing" / "ads"
        workspace.mkdir(parents=True, exist_ok=True)
        
        ad_templates = {
            "google": {
                "headlines": [
                    f"Transform Your Business with {product_name}",
                    f"{product_name} - The Smart Solution",
                    f"Get Started with {product_name} Today"
                ],
                "descriptions": [
                    product_description,
                    f"Discover how {product_name} can help you achieve more.",
                    "Join thousands of satisfied customers."
                ]
            },
            "facebook": {
                "primary": f"✨ {product_name}\n\n{product_description}\n\nLearn more →",
                "secondary": f"Discover {product_name} - The solution you've been looking for. Click to learn more!"
            },
            "linkedin": {
                "headline": f"Introducing {product_name}",
                "body": f"We're excited to announce {product_name}.\n\n{product_description}\n\n{product_name} helps professionals like you achieve better results.\n\nLearn more and connect with us."
            },
            "twitter": {
                "tweet": f"🧵 {product_name} is here! {product_description[:100]}... #{product_name.replace(' ', '')} #innovation",
                "thread": f"1/ We're thrilled to introduce {product_name}!\n\n{product_description}\n\n2/ What makes us different:\n\n[Your unique value props]\n\n3/ Ready to get started? Link in bio! 🔗"
            }
        }
        
        ads_content = f"""# Ad Variants: {product_name}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

{chr(10).join(f"## {platform.upper()}\n" + json.dumps(templates, indent=2) + "\n" for platform, templates in ad_templates.items() if platform in ad_platforms)}

## Best Practices
- A/B test multiple headlines
- Use high-quality visuals
- Include clear CTAs
- Match ad copy to landing page
"""
        
        ads_file = workspace / f"{product_name.lower().replace(' ', '-')}-ads.md"
        with open(ads_file, 'w') as f:
            f.write(ads_content)
        
        ads_info = {
            "name": product_name,
            "platforms": ad_platforms,
            "path": str(ads_file),
            "created_at": datetime.now().isoformat()
        }
        self.campaigns_created.append(ads_info)
        
        return ads_info
    
    def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a marketing task"""
        context = task.context
        
        if context.get("action") == "create_marketing_plan":
            result = self.create_marketing_plan(
                product_name=context.get("product_name", "New Product"),
                target_audience=context.get("target_audience", ""),
                goals=context.get("goals", []),
                budget_tier=context.get("budget_tier", "medium")
            )
            return {"success": True, "type": "marketing_plan", "data": result}
        
        elif context.get("action") == "create_campaign":
            result = self.create_campaign(
                campaign_name=context.get("campaign_name", ""),
                campaign_type=context.get("campaign_type", "awareness"),
                channels=context.get("channels", ["social", "email"]),
                target_audience=context.get("target_audience", ""),
                call_to_action=context.get("call_to_action", "Get Started"),
                duration_weeks=context.get("duration_weeks", 4)
            )
            return {"success": True, "type": "campaign", "data": result}
        
        elif context.get("action") == "create_ad_variants":
            result = self.create_ad_variants(
                product_name=context.get("product_name", ""),
                product_description=context.get("product_description", ""),
                ad_platforms=context.get("ad_platforms")
            )
            return {"success": True, "type": "ad_variants", "data": result}
        
        prompt = f"""Create a marketing solution for this task:

Title: {task.title}
Description: {task.description}

Context:
{json.dumps(context, indent=2)}

Create the appropriate marketing materials and strategies. Report what you created.
"""
        
        response = self.conversation.send_message(prompt)
        
        return {
            "success": True,
            "response": response,
            "campaigns_created": self.campaigns_created
        }
