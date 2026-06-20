"""
Social Media Worker Agent
Specializes in social media content creation and management
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from openhands.sdk import LLM, Tool

from ..ceo_agent import WorkerAgent
from ..task_manager import Task


SOCIAL_MEDIA_SYSTEM_PROMPT = """You are SocialMedia, a specialized social media agent at NanoCorp.

Your expertise includes:
- Content strategy for all major platforms
- Platform-specific content creation
- Engagement tactics
- Community management
- Hashtag optimization
- Viral content analysis
- Social media calendars
- Brand voice consistency
- Influencer marketing
- Analytics interpretation

You create engaging content that resonates with target audiences.
"""


class SocialMediaWorker(WorkerAgent):
    """Worker agent specialized in social media"""
    
    def __init__(self, llm: LLM, workspace_path: Path):
        super().__init__(
            name="SocialMedia",
            description="Social media specialist - creates posts, manages presence, and engages audiences",
            specialties=[
                "Content Creation",
                "Platform Strategy",
                "Engagement Management",
                "Hashtag Research",
                "Content Calendars",
                "Visual Content Ideas",
                "Community Building",
                "Influencer Outreach",
                "Analytics",
                "Trend Analysis"
            ],
            llm=llm,
            workspace_path=workspace_path,
            tools=[]
        )
        self.posts_created: List[Dict[str, Any]] = []
    
    def create_social_posts(
        self,
        topic: str,
        platforms: List[str],
        num_posts: int = 5,
        brand_voice: str = "Professional and friendly"
    ) -> Dict[str, Any]:
        """Create social media posts for multiple platforms"""
        workspace = self.workspace_path / "social" / "posts"
        workspace.mkdir(parents=True, exist_ok=True)
        
        platform_formats = {
            "twitter": {"max_length": 280, "style": "Concise, punchy"},
            "linkedin": {"max_length": 3000, "style": "Professional, thought leadership"},
            "instagram": {"max_length": 2200, "style": "Visual storytelling"},
            "facebook": {"max_length": 500, "style": "Conversational, community-focused"},
            "threads": {"max_length": 500, "style": "Casual, opinionated"},
            "tiktok": {"max_length": 150, "style": "Trendy, engaging hooks"}
        }
        
        posts_content = "# Social Media Posts: " + topic + "\n\nBrand Voice: " + brand_voice + "\nGenerated: " + datetime.now().strftime('%Y-%m-%d') + "\n\n---\n\n"
        
        for platform in platforms:
            if platform in platform_formats:
                fmt = platform_formats[platform]
                posts_content += "## " + platform.upper() + "\n\n**Format**: " + fmt['style'] + "\n**Max Length**: " + str(fmt['max_length']) + " characters\n\n"
                for i in range(num_posts):
                    posts_content += "### Post " + str(i + 1) + "\n\n**Content**: [Post content for " + topic + "]\n\n**Suggested Hashtags**: #Example #" + topic.replace(' ', '') + "\n\n---\n\n"
        
        posts_file = workspace / ("posts-" + topic.lower().replace(' ', '-') + ".md")
        with open(posts_file, 'w') as f:
            f.write(posts_content)
        
        posts_info = {
            "topic": topic,
            "platforms": platforms,
            "num_posts": num_posts,
            "path": str(posts_file),
            "created_at": datetime.now().isoformat()
        }
        self.posts_created.append(posts_info)
        return posts_info
    
    def create_content_calendar(
        self,
        month: str,
        themes: List[str],
        platforms: List[str],
        posting_frequency: Dict[str, int]
    ) -> Dict[str, Any]:
        """Create a monthly content calendar"""
        workspace = self.workspace_path / "social" / "calendars"
        workspace.mkdir(parents=True, exist_ok=True)
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        calendar_content = "# Content Calendar: " + month + "\n\nGenerated: " + datetime.now().strftime('%Y-%m-%d') + "\n\n## Overview\n- **Platforms**: " + ", ".join(platforms) + "\n- **Themes**: " + ", ".join(themes) + "\n\n"
        
        for platform in platforms:
            freq = posting_frequency.get(platform, 1)
            calendar_content += "### " + platform.title() + "\n**Posts per week**: " + str(freq) + "\n\n| Day | Content Type | Theme |\n|-----|--------------|-------|\n"
            for day in days[:freq * 2 if freq > 0 else 1]:
                theme_idx = days.index(day) % len(themes)
                content_types = ["Educational", "Entertaining", "Promotional", "Engagement"]
                calendar_content += "| " + day + " | " + content_types[days.index(day) % len(content_types)] + " | " + themes[theme_idx] + " |\n"
            calendar_content += "\n"
        
        calendar_file = workspace / ("calendar-" + month.lower().replace(' ', '-') + ".md")
        with open(calendar_file, 'w') as f:
            f.write(calendar_content)
        
        calendar_info = {
            "month": month,
            "platforms": platforms,
            "themes": themes,
            "path": str(calendar_file),
            "created_at": datetime.now().isoformat()
        }
        self.posts_created.append(calendar_info)
        return calendar_info
    
    def create_thread(
        self,
        thread_topic: str,
        thread_type: str = "educational",
        num_tweets: int = 10
    ) -> Dict[str, Any]:
        """Create a Twitter/X thread"""
        workspace = self.workspace_path / "social" / "threads"
        workspace.mkdir(parents=True, exist_ok=True)
        
        thread_content = "# Twitter Thread: " + thread_topic + "\n\nType: " + thread_type + "\nTweets: " + str(num_tweets) + "\nGenerated: " + datetime.now().strftime('%Y-%m-%d') + "\n\n---\n\n"
        
        for i in range(num_tweets):
            tweet_num = i + 1
            prefix = "THREAD" if i == 0 else str(tweet_num) + "/"
            
            if i == 0:
                tweet = prefix + " " + thread_topic + "\n\nHere's what you need to know:"
            elif i == num_tweets - 1:
                tweet = str(tweet_num) + "/ That's a wrap!\n\nWhat questions do you have? Drop them below."
            else:
                tweet = str(tweet_num) + "/ [Content point " + str(i) + " about " + thread_topic + "]\n\nKey takeaway: [Brief insight]"
            
            thread_content += "### Tweet " + str(tweet_num) + "\n```\n" + tweet + "\n```\n\n"
        
        thread_file = workspace / ("thread-" + thread_topic.lower().replace(' ', '-') + ".md")
        with open(thread_file, 'w') as f:
            f.write(thread_content)
        
        thread_info = {
            "topic": thread_topic,
            "type": thread_type,
            "tweets": num_tweets,
            "path": str(thread_file),
            "created_at": datetime.now().isoformat()
        }
        self.posts_created.append(thread_info)
        return thread_info
    
    def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a social media task"""
        context = task.context
        
        if context.get("action") == "create_posts":
            result = self.create_social_posts(
                topic=context.get("topic", ""),
                platforms=context.get("platforms", ["twitter", "linkedin"]),
                num_posts=context.get("num_posts", 5),
                brand_voice=context.get("brand_voice", "Professional and friendly")
            )
            return {"success": True, "type": "social_posts", "data": result}
        
        elif context.get("action") == "create_content_calendar":
            result = self.create_content_calendar(
                month=context.get("month", ""),
                themes=context.get("themes", []),
                platforms=context.get("platforms", []),
                posting_frequency=context.get("posting_frequency", {})
            )
            return {"success": True, "type": "content_calendar", "data": result}
        
        elif context.get("action") == "create_thread":
            result = self.create_thread(
                thread_topic=context.get("thread_topic", ""),
                thread_type=context.get("thread_type", "educational"),
                num_tweets=context.get("num_tweets", 10)
            )
            return {"success": True, "type": "thread", "data": result}
        
        prompt = "Create social media content for this task:\n\nTitle: " + task.title + "\nDescription: " + task.description + "\n\nContext:\n" + json.dumps(context, indent=2) + "\n\nCreate appropriate social media content. Report what you created."
        
        response = self.conversation.send_message(prompt)
        
        return {
            "success": True,
            "response": response,
            "posts_created": self.posts_created
        }
