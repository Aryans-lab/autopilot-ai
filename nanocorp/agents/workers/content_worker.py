"""
Content Worker Agent
Specializes in blog posts, copywriting, and content creation
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from openhands.sdk import LLM, Tool



from ..ceo_agent import WorkerAgent
from ..task_manager import Task


CONTENT_SYSTEM_PROMPT = """You are Content, a specialized content creation agent at NanoCorp.

Your expertise includes:
- Blog post writing
- Article creation
- Copywriting
- SEO content optimization
- Landing page copy
- Product descriptions
- Email copy
- Social media captions
- Whitepapers
- Case studies

You create compelling, well-structured content that engages audiences and drives action.
"""


class ContentWorker(WorkerAgent):
    """Worker agent specialized in content creation"""
    
    def __init__(self, llm: LLM, workspace_path: Path):
        super().__init__(
            name="Content",
            description="Content creation specialist - writes blog posts, articles, copy, and marketing content",
            specialties=[
                "Blog Posts",
                "Articles",
                "Copywriting",
                "SEO Content",
                "Landing Page Copy",
                "Product Descriptions",
                "Email Copy",
                "Social Captions",
                "Whitepapers",
                "Case Studies"
            ],
            llm=llm,
            workspace_path=workspace_path,
            tools=[]
        )
        self.contents_created: List[Dict[str, Any]] = []
    
    def create_blog_post(
        self,
        title: str,
        target_audience: str,
        main_points: List[str],
        tone: str = "professional",
        include_seo: bool = True
    ) -> Dict[str, Any]:
        """Create a blog post"""
        workspace = self.workspace_path / "content" / "blog"
        workspace.mkdir(parents=True, exist_ok=True)
        
        slug = title.lower().replace(' ', '-').replace('[^a-z0-9]', '')
        meta_description = f"Learn about {title} in this comprehensive guide for {target_audience}."
        
        main_points_html = "\n\n".join(
            f"## {point}\n\n[Expand on {point.lower()} with valuable insights and practical tips]"
            for point in main_points
        )
        
        main_points_text = "\n\n".join(
            f"### {point}\n\n[Expand on {point.lower()} with valuable insights and practical tips]"
            for point in main_points
        )
        
        if include_seo:
            content = f"""---
title: "{title}"
date: {datetime.now().strftime('%Y-%m-%d')}
description: "{meta_description}"
slug: {slug}
author: NanoCorp
tags: [Industry, Technology, Guide]
---

# {title}

*Published on {datetime.now().strftime('%B %d, %Y')}*

## Introduction

Welcome to our guide on **{title}**. In this comprehensive article, we'll explore everything {target_audience} need to know about this important topic.

{''.join(f'- Understanding the fundamentals\n' for _ in range(3))}

---

{main_points_text}

---

## Conclusion

{title} is an essential topic for {target_audience}. By implementing the strategies discussed in this article, you can achieve better results and stay ahead of the competition.

### Key Takeaways

{chr(10).join(f'- [Takeaway about {point.lower()}]' for point in main_points[:3])}

### Next Steps

1. Review the key points covered
2. Implement one strategy this week
3. Track your progress and adjust as needed

---

*Have questions about {title}? Leave a comment below!*

## SEO Metadata

- **Title**: {title} - The Complete Guide
- **Meta Description**: {meta_description}
- **Focus Keyword**: {title.split()[0]}
- **URL Slug**: /{slug}
- **Word Count**: ~1200 words
- **Reading Time**: ~6 minutes
"""
        else:
            content = f"""# {title}

*Published on {datetime.now().strftime('%B %d, %Y')}*

## Introduction

{''.join(f'{target_audience} need to understand how ' for _ in range(1))} {title}. In this article, we'll cover the essential aspects you need to know.

{main_points_text}

## Conclusion

By understanding {title}, you can make better decisions and achieve your goals more effectively.
"""
        
        content_file = workspace / f"{slug}.md"
        with open(content_file, 'w') as f:
            f.write(content)
        
        content_info = {
            "type": "blog_post",
            "title": title,
            "slug": slug,
            "path": str(content_file),
            "created_at": datetime.now().isoformat(),
            "has_seo": include_seo,
            "target_audience": target_audience
        }
        self.contents_created.append(content_info)
        
        return content_info
    
    def create_landing_page_copy(
        self,
        product_name: str,
        headline: str,
        subheadline: str,
        key_benefits: List[str],
        social_proof: str,
        cta_text: str
    ) -> Dict[str, Any]:
        """Create landing page copy"""
        workspace = self.workspace_path / "content" / "copy"
        workspace.mkdir(parents=True, exist_ok=True)
        
        benefits_html = "\n".join(
            f'<li><strong>{benefit}</strong></li>'
            for benefit in key_benefits
        )
        
        copy_content = f"""# Landing Page Copy: {product_name}

**Headline:** {headline}
**Subheadline:** {subheadline}

---

## Hero Section

**Headline:**
{headline}

**Subheadline:**
{subheadline}

**CTA Button:**
{cta_text}

**Supporting Text:**
[Join thousands of satisfied customers who have transformed their business with {product_name}.]

---

## Problem Section

**Section Headline:**
The Challenge You Face

**Content:**
[Talk about the pain points and challenges your audience faces. Make them feel understood.]

- [Pain point 1 that keeps them up at night]
- [Pain point 2 that prevents them from achieving goals]
- [Pain point 3 that frustrates them daily]

---

## Solution Section

**Section Headline:**
Introducing {product_name}

**Content:**
[{product_name}] solves these challenges with a powerful, easy-to-use solution designed specifically for you.

**Key Benefits:**

{chr(10).join(f'1. {benefit}' for benefit in key_benefits)}

---

## How It Works Section

**Section Headline:**
How {product_name} Works

**Step 1:** [Simple first step]
**Step 2:** [Easy second step]
**Step 3:** [Effortless third step]

---

## Social Proof Section

**Testimonial:**
"{social_proof}"

— [Customer Name], [Job Title] at [Company]

**Stats:**
- [X]+ Happy customers
- [X]% Success rate
- [X] Time saved on average

---

## Final CTA Section

**Headline:**
Ready to Get Started?

**Subheadline:**
Join thousands of others who have already transformed their [outcome].

**Primary CTA:**
{cta_text}

**Secondary CTA:**
Learn More

**Guarantee:**
[30-day money-back guarantee / No risk trial / Satisfaction guaranteed]

---

## Footer Copy

**About:**
[{product_name}] is dedicated to helping [target audience] achieve [desired outcome].

**Contact:**
Questions? We're here to help! [email@example.com]
"""
        
        copy_file = workspace / f"landing-copy-{product_name.lower().replace(' ', '-')}.md"
        with open(copy_file, 'w') as f:
            f.write(copy_content)
        
        content_info = {
            "type": "landing_page_copy",
            "product": product_name,
            "headline": headline,
            "path": str(copy_file),
            "created_at": datetime.now().isoformat()
        }
        self.contents_created.append(content_info)
        
        return content_info
    
    def create_product_description(
        self,
        product_name: str,
        product_type: str,
        features: List[str],
        target_customer: str,
        price_tier: str = "standard"
    ) -> Dict[str, Any]:
        """Create product descriptions"""
        workspace = self.workspace_path / "content" / "products"
        workspace.mkdir(parents=True, exist_ok=True)
        
        features_text = "\n".join(
            f"- **{feat}**: [Description of how this feature benefits the customer]"
            for feat in features
        )
        
        desc_content = f"""# Product Description: {product_name}

**Type:** {product_type}
**Target Customer:** {target_customer}
**Price Tier:** {price_tier}

---

## Short Description (50-100 words)

Introducing {product_name}, the {product_type} that [primary benefit]. Designed specifically for {target_customer}, it [key differentiator]. Get started today and experience [key outcome].

---

## Full Description

### Overview

{product_name} is a {product_type} designed to help {target_customer} achieve [desired outcome]. With cutting-edge features and an intuitive design, it's never been easier to [primary benefit].

### Key Features

{features_text}

### Who It's For

{product_name} is perfect for {target_customer} who want to:
- [Benefit 1]
- [Benefit 2]
- [Benefit 3]

### Specifications

- **Category:** {product_type}
- **Price Tier:** {price_tier}
- **Compatibility:** [Platform/Requirements]
- **Support:** [Support level]

### Why Choose {product_name}?

Unlike other {product_type}s, {product_name} is built with you in mind. We focus on delivering [key differentiator] so you can achieve [outcome] without the complexity.

---

## Variations

### Basic Tier
[Entry-level description]

### Pro Tier  
[Professional description with enhanced features]

### Enterprise Tier
[Enterprise description with full capabilities]
"""
        
        desc_file = workspace / f"product-desc-{product_name.lower().replace(' ', '-')}.md"
        with open(desc_file, 'w') as f:
            f.write(desc_content)
        
        content_info = {
            "type": "product_description",
            "product": product_name,
            "product_type": product_type,
            "path": str(desc_file),
            "created_at": datetime.now().isoformat()
        }
        self.contents_created.append(content_info)
        
        return content_info
    
    def create_case_study(
        self,
        client_name: str,
        industry: str,
        challenge: str,
        solution: str,
        results: List[Dict[str, str]],
        testimonial: str
    ) -> Dict[str, Any]:
        """Create a case study"""
        workspace = self.workspace_path / "content" / "case_studies"
        workspace.mkdir(parents=True, exist_ok=True)
        
        results_table = "\n".join(
            f"| {r.get('metric', '')} | {r.get('before', '')} | {r.get('after', '')} |"
            for r in results
        )
        
        case_study_content = f"""# Case Study: {client_name}

**Industry:** {industry}
**Client:** {client_name}
**Date:** {datetime.now().strftime('%B %Y')}

---

## Executive Summary

{client_name}, a leading company in the {industry} industry, partnered with us to overcome [challenge overview]. Through our collaborative solution, they achieved remarkable results including [key outcome].

---

## The Challenge

{challenge}

{client_name} faced several obstacles:
- [Obstacle 1]
- [Obstacle 2]
- [Obstacle 3]

These challenges were impacting their ability to [business goal].

---

## Our Solution

{solution}

### Approach

1. **Discovery:** [What we did first]
2. **Planning:** [How we structured the solution]
3. **Implementation:** [How we executed]
4. **Optimization:** [How we refined]

### Key Components

- **Component 1:** [Description]
- **Component 2:** [Description]
- **Component 3:** [Description]

---

## Results

### Key Metrics

| Metric | Before | After |
|--------|--------|-------|
{results_table}

### Total Impact

{chr(10).join(f'- {r.get("metric", "")}: {r.get("after", "")} (from {r.get("before", "")})' for r in results)}

---

## What They Said

> "{testimonial}"

— [Name], [Title], {client_name}

---

## Looking Forward

{client_name} continues to see growth and success. They are now exploring [future plans] with plans to [next steps].

### Next Steps for {client_name}
- [Future initiative 1]
- [Future initiative 2]

---

## Can We Help You Too?

If you're facing similar challenges, we'd love to chat about how we can help.

**Contact us:** [email@example.com]

---

*This case study was prepared by NanoCorp. Results may vary based on specific circumstances.*
"""
        
        case_file = workspace / f"case-study-{client_name.lower().replace(' ', '-')}.md"
        with open(case_file, 'w') as f:
            f.write(case_study_content)
        
        content_info = {
            "type": "case_study",
            "client": client_name,
            "industry": industry,
            "path": str(case_file),
            "created_at": datetime.now().isoformat()
        }
        self.contents_created.append(content_info)
        
        return content_info
    
    def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a content task"""
        context = task.context
        
        if context.get("action") == "create_blog_post":
            result = self.create_blog_post(
                title=context.get("title", ""),
                target_audience=context.get("target_audience", ""),
                main_points=context.get("main_points", []),
                tone=context.get("tone", "professional"),
                include_seo=context.get("include_seo", True)
            )
            return {"success": True, "type": "blog_post", "data": result}
        
        elif context.get("action") == "create_landing_page_copy":
            result = self.create_landing_page_copy(
                product_name=context.get("product_name", ""),
                headline=context.get("headline", ""),
                subheadline=context.get("subheadline", ""),
                key_benefits=context.get("key_benefits", []),
                social_proof=context.get("social_proof", ""),
                cta_text=context.get("cta_text", "Get Started")
            )
            return {"success": True, "type": "landing_page_copy", "data": result}
        
        elif context.get("action") == "create_product_description":
            result = self.create_product_description(
                product_name=context.get("product_name", ""),
                product_type=context.get("product_type", ""),
                features=context.get("features", []),
                target_customer=context.get("target_customer", ""),
                price_tier=context.get("price_tier", "standard")
            )
            return {"success": True, "type": "product_description", "data": result}
        
        elif context.get("action") == "create_case_study":
            result = self.create_case_study(
                client_name=context.get("client_name", ""),
                industry=context.get("industry", ""),
                challenge=context.get("challenge", ""),
                solution=context.get("solution", ""),
                results=context.get("results", []),
                testimonial=context.get("testimonial", "")
            )
            return {"success": True, "type": "case_study", "data": result}
        
        prompt = f"""Create content for this task:

Title: {task.title}
Description: {task.description}

Context:
{json.dumps(context, indent=2)}

Create appropriate content. Report what you created.
"""
        
        response = self.conversation.send_message(prompt)
        
        return {
            "success": True,
            "response": response,
            "contents_created": self.contents_created
        }
