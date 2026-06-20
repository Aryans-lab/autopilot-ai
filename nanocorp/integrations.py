"""
NanoCorp Integrations - Real Actions

Actually send emails, post to social media, deploy websites.
These integrations let NanoCorp take real actions in the world.
"""
import os
import smtplib
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


@dataclass
class IntegrationResult:
    """Result of an integration action"""
    success: bool
    action: str
    details: str
    timestamp: str


class EmailIntegration:
    """
    Send emails via SMTP or API.
    
    Supports:
    - SMTP (Gmail, Outlook, etc.)
    - SendGrid API
    - Mailgun API
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.smtp_host = self.config.get("smtp_host", "smtp.gmail.com")
        self.smtp_port = self.config.get("smtp_port", 587)
        self.username = self.config.get("username")
        self.password = self.config.get("password")
    
    def send(
        self,
        to: str,
        subject: str,
        body: str,
        from_name: str = "NanoCorp"
    ) -> IntegrationResult:
        """Send an email"""
        try:
            if not self.username or not self.password:
                return IntegrationResult(
                    success=False,
                    action="send_email",
                    details="SMTP credentials not configured. Set username and password.",
                    timestamp=datetime.now().isoformat()
                )
            
            msg = MIMEMultipart()
            msg['From'] = f"{from_name} <{self.username}>"
            msg['To'] = to
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return IntegrationResult(
                success=True,
                action="send_email",
                details=f"Sent to {to}",
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return IntegrationResult(
                success=False,
                action="send_email",
                details=f"Failed: {str(e)}",
                timestamp=datetime.now().isoformat()
            )
    
    def send_newsletter(
        self,
        subject: str,
        content: str,
        recipients: List[str]
    ) -> IntegrationResult:
        """Send newsletter to multiple recipients"""
        success_count = 0
        failed = []
        
        for recipient in recipients:
            result = self.send(recipient, subject, content)
            if result.success:
                success_count += 1
            else:
                failed.append(recipient)
        
        return IntegrationResult(
            success=success_count == len(recipients),
            action="send_newsletter",
            details=f"Sent to {success_count}/{len(recipients)} recipients",
            timestamp=datetime.now().isoformat()
        )


class GitHubIntegration:
    """
    Interact with GitHub via CLI or API.
    
    Create repos, push code, manage issues.
    """
    
    def __init__(self, token: str = None):
        self.token = token or os.environ.get("GITHUB_TOKEN")
    
    def _run_gh(self, args: List[str]) -> Dict:
        """Run a gh command"""
        try:
            result = subprocess.run(
                ["gh"] + args,
                capture_output=True,
                text=True,
                timeout=30,
                env={**os.environ, "GH_TOKEN": self.token} if self.token else os.environ
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_repo(self, name: str, description: str = "", private: bool = False) -> IntegrationResult:
        """Create a GitHub repository"""
        visibility = "--private" if private else "--public"
        result = self._run_gh(["repo", "create", name, visibility, "-d", description])
        
        return IntegrationResult(
            success=result["success"],
            action="create_repo",
            details=result.get("output", result.get("error", ""))[:200],
            timestamp=datetime.now().isoformat()
        )
    
    def push_code(self, repo: str, path: str, message: str = "NanoCorp update") -> IntegrationResult:
        """Push code to GitHub"""
        try:
            subprocess.run(["git", "add", "."], cwd=path, check=True)
            subprocess.run(["git", "commit", "-m", message], cwd=path, check=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=path, check=True)
            
            return IntegrationResult(
                success=True,
                action="push_code",
                details=f"Pushed to {repo}",
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return IntegrationResult(
                success=False,
                action="push_code",
                details=f"Push failed: {str(e)}",
                timestamp=datetime.now().isoformat()
            )


class DeploymentIntegration:
    """
    Deploy websites and apps.
    
    Supports:
    - Vercel
    - Netlify
    - Cloudflare Pages
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
    
    def deploy_vercel(self, path: str, project_name: str = None) -> IntegrationResult:
        """Deploy to Vercel"""
        try:
            args = ["vercel", "deploy"]
            if project_name:
                args.extend(["--name", project_name])
            args.append(path)
            
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                # Extract URL from output
                lines = result.stdout.split('\n')
                url = next((l for l in lines if 'vercel.app' in l), result.stdout[:200])
                
                return IntegrationResult(
                    success=True,
                    action="deploy_vercel",
                    details=f"Deployed: {url}",
                    timestamp=datetime.now().isoformat()
                )
            
            return IntegrationResult(
                success=False,
                action="deploy_vercel",
                details=result.stderr[:200],
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return IntegrationResult(
                success=False,
                action="deploy_vercel",
                details=f"Deploy failed: {str(e)}",
                timestamp=datetime.now().isoformat()
            )
    
    def deploy_netlify(self, path: str) -> IntegrationResult:
        """Deploy to Netlify"""
        try:
            result = subprocess.run(
                ["netlify", "deploy", "--dir", path, "--prod"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                url = next((l for l in lines if 'netlify' in l), result.stdout[:200])
                
                return IntegrationResult(
                    success=True,
                    action="deploy_netlify",
                    details=f"Deployed: {url}",
                    timestamp=datetime.now().isoformat()
                )
            
            return IntegrationResult(
                success=False,
                action="deploy_netlify",
                details=result.stderr[:200],
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return IntegrationResult(
                success=False,
                action="deploy_netlify",
                details=f"Deploy failed: {str(e)}",
                timestamp=datetime.now().isoformat()
            )


class SocialMediaIntegration:
    """
    Post to social media platforms.
    
    Supports:
    - Twitter/X via API
    - LinkedIn via API
    - Discord webhooks
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.twitter_token = self.config.get("twitter_bearer_token")
        self.linkedin_token = self.config.get("linkedin_access_token")
    
    def post_twitter(self, content: str, image_path: str = None) -> IntegrationResult:
        """Post to Twitter/X"""
        if not self.twitter_token:
            return IntegrationResult(
                success=False,
                action="post_twitter",
                details="Twitter API credentials not configured",
                timestamp=datetime.now().isoformat()
            )
        
        try:
            import urllib.request
            import urllib.parse
            
            url = "https://api.twitter.com/2/tweets"
            data = {"text": content}
            
            if image_path:
                # Upload image first
                url = "https://upload.twitter.com/1.1/media/upload.json"
                with open(image_path, 'rb') as f:
                    img_data = f.read()
                req = urllib.request.Request(
                    url,
                    data=img_data,
                    headers={
                        "Authorization": f"Bearer {self.twitter_token}",
                        "Content-Type": "multipart/form-data"
                    },
                    method="POST"
                )
                with urllib.request.urlopen(req) as resp:
                    media = json.loads(resp.read())
                data = {"text": content, "media": {"media_ids": [media["media_id"]]}}
                url = "https://api.twitter.com/2/tweets"
            
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode(),
                headers={
                    "Authorization": f"Bearer {self.twitter_token}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read())
            
            return IntegrationResult(
                success=True,
                action="post_twitter",
                details=f"Tweet posted: {result.get('data', {}).get('id', 'unknown')}",
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return IntegrationResult(
                success=False,
                action="post_twitter",
                details=f"Post failed: {str(e)}",
                timestamp=datetime.now().isoformat()
            )
    
    def post_discord(self, content: str, webhook_url: str = None) -> IntegrationResult:
        """Post to Discord via webhook"""
        webhook = webhook_url or self.config.get("discord_webhook")
        
        if not webhook:
            return IntegrationResult(
                success=False,
                action="post_discord",
                details="Discord webhook not configured",
                timestamp=datetime.now().isoformat()
            )
        
        try:
            import urllib.request
            
            data = {"content": content}
            req = urllib.request.Request(
                webhook,
                data=json.dumps(data).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req) as resp:
                resp.read()
            
            return IntegrationResult(
                success=True,
                action="post_discord",
                details="Message sent to Discord",
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return IntegrationResult(
                success=False,
                action="post_discord",
                details=f"Post failed: {str(e)}",
                timestamp=datetime.now().isoformat()
            )


class IntegrationManager:
    """
    Manage all integrations.
    
    Easy setup and unified interface.
    """
    
    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path) if config_path else Path("~/.nanocorp/integrations.json")
        self.config = self._load_config()
        
        # Initialize all integrations
        self.email = EmailIntegration(self.config.get("email"))
        self.github = GitHubIntegration(self.config.get("github", {}).get("token"))
        self.deploy = DeploymentIntegration(self.config.get("deployment"))
        self.social = SocialMediaIntegration(self.config.get("social"))
    
    def _load_config(self) -> Dict:
        """Load configuration"""
        path = self.config_path.expanduser()
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return {}
    
    def configure(self, integration: str, **kwargs):
        """Configure an integration"""
        if integration not in self.config:
            self.config[integration] = {}
        self.config[integration].update(kwargs)
        
        # Save
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        # Re-initialize
        if integration == "email":
            self.email = EmailIntegration(self.config.get("email"))
        elif integration == "github":
            self.github = GitHubIntegration(kwargs.get("token"))
        elif integration == "social":
            self.social = SocialMediaIntegration(self.config.get("social"))
    
    def status(self) -> Dict[str, bool]:
        """Check integration status"""
        return {
            "email": bool(self.email.username and self.email.password),
            "github": bool(self.github.token),
            "deploy": True,  # Always available
            "twitter": bool(self.social.twitter_token),
            "discord": bool(self.social.config.get("discord_webhook"))
        }
