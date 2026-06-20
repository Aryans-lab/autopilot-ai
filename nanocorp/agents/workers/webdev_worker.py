"""
WebDev Worker Agent
Specializes in website creation, landing pages, and web applications
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from openhands.sdk import LLM, Tool

from ..ceo_agent import WorkerAgent
from ..task_manager import Task


WEBDEV_SYSTEM_PROMPT = """You are WebDev, a specialized web development agent at NanoCorp.

Your expertise includes:
- Building responsive websites and landing pages
- Creating web applications with modern frameworks
- HTML, CSS, JavaScript, React, Vue, and more
- Website deployment and hosting
- Performance optimization
- SEO-friendly development
- Creating demo/mockup websites for products and services

When creating websites:
1. Design for the target audience and purpose
2. Ensure mobile responsiveness
3. Optimize for performance and SEO
4. Use modern, clean design principles
5. Include proper accessibility features

You create production-ready code that can be deployed immediately.
"""


class WebDevWorker(WorkerAgent):
    """Worker agent specialized in web development"""
    
    def __init__(self, llm: LLM, workspace_path: Path):
        super().__init__(
            name="WebDev",
            description="Web development specialist - creates websites, landing pages, and web applications",
            specialties=[
                "Landing Pages",
                "Business Websites",
                "Portfolio Sites",
                "Product Demos",
                "Web Applications",
                "HTML/CSS/JS",
                "React/Vue Development",
                "Website Deployment",
                "Performance Optimization",
                "SEO Implementation"
            ],
            llm=llm,
            workspace_path=workspace_path,
            tools=[]  # Will use default tools
        )
        self.projects_created: List[Dict[str, Any]] = []
    
    def create_landing_page(
        self,
        product_name: str,
        product_description: str,
        cta_text: str = "Get Started",
        features: List[str] = None,
        brand_color: str = "#2563EB"
    ) -> Dict[str, Any]:
        """Create a landing page for a product or service"""
        workspace = self.workspace_path / "webdev" / "landing_pages"
        workspace.mkdir(parents=True, exist_ok=True)
        
        project_name = product_name.lower().replace(" ", "-")
        project_dir = workspace / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        
        features_html = ""
        if features:
            features_html = "\n".join(
                f'<li class="feature-item">✨ {feat}</li>'
                for feat in features
            )
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{product_name} - {product_description[:50]}...</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .hero {{
            background: linear-gradient(135deg, {brand_color} 0%, #1e40af 100%);
            color: white;
            padding: 80px 20px;
            text-align: center;
        }}
        .hero h1 {{
            font-size: 3rem;
            margin-bottom: 20px;
        }}
        .hero p {{
            font-size: 1.25rem;
            max-width: 600px;
            margin: 0 auto 30px;
        }}
        .cta-button {{
            display: inline-block;
            background: white;
            color: {brand_color};
            padding: 15px 40px;
            border-radius: 50px;
            text-decoration: none;
            font-weight: bold;
            font-size: 1.1rem;
            transition: transform 0.2s;
        }}
        .cta-button:hover {{
            transform: scale(1.05);
        }}
        .features {{
            padding: 60px 20px;
            max-width: 800px;
            margin: 0 auto;
        }}
        .features h2 {{
            text-align: center;
            margin-bottom: 40px;
            font-size: 2rem;
        }}
        .features ul {{
            list-style: none;
        }}
        .feature-item {{
            padding: 20px;
            margin-bottom: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            font-size: 1.1rem;
        }}
        .footer {{
            text-align: center;
            padding: 30px;
            background: #333;
            color: white;
        }}
    </style>
</head>
<body>
    <section class="hero">
        <h1>{product_name}</h1>
        <p>{product_description}</p>
        <a href="#" class="cta-button">{cta_text}</a>
    </section>
    
    <section class="features">
        <h2>Key Features</h2>
        <ul>
            {features_html}
        </ul>
    </section>
    
    <footer class="footer">
        <p>&copy; 2024 {product_name}. All rights reserved.</p>
    </footer>
</body>
</html>
'''
        
        html_file = project_dir / "index.html"
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        project_info = {
            "name": product_name,
            "type": "landing_page",
            "path": str(html_file),
            "created_at": datetime.now().isoformat(),
            "features": features or []
        }
        self.projects_created.append(project_info)
        
        return project_info
    
    def create_business_website(
        self,
        company_name: str,
        industry: str,
        services: List[str],
        contact_email: str,
        brand_color: str = "#2563EB"
    ) -> Dict[str, Any]:
        """Create a complete business website"""
        workspace = self.workspace_path / "webdev" / "business_sites"
        workspace.mkdir(parents=True, exist_ok=True)
        
        project_name = company_name.lower().replace(" ", "-")
        project_dir = workspace / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        
        services_html = "\n".join(
            f'''<div class="service-card">
                <h3>{svc}</h3>
                <p>Professional {svc.lower()} services tailored to your needs.</p>
            </div>'''
            for svc in services
        )
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company_name} - {industry} Solutions</title>
    <meta name="description" content="{company_name} provides professional {industry} services.">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
        }}
        nav {{
            background: {brand_color};
            padding: 15px 20px;
            position: sticky;
            top: 0;
        }}
        nav ul {{
            list-style: none;
            display: flex;
            justify-content: center;
            gap: 30px;
        }}
        nav a {{
            color: white;
            text-decoration: none;
            font-weight: 500;
        }}
        .hero {{
            background: linear-gradient(135deg, {brand_color} 0%, #1e40af 100%);
            color: white;
            padding: 100px 20px;
            text-align: center;
        }}
        .hero h1 {{
            font-size: 3rem;
            margin-bottom: 15px;
        }}
        .services {{
            padding: 60px 20px;
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
        }}
        .service-card {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .service-card h3 {{
            color: {brand_color};
            margin-bottom: 10px;
        }}
        .contact {{
            background: #333;
            color: white;
            padding: 60px 20px;
            text-align: center;
        }}
        footer {{
            background: #222;
            color: #888;
            text-align: center;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <nav>
        <ul>
            <li><a href="#home">Home</a></li>
            <li><a href="#services">Services</a></li>
            <li><a href="#contact">Contact</a></li>
        </ul>
    </nav>
    
    <section id="home" class="hero">
        <h1>{company_name}</h1>
        <p>Professional {industry} Solutions</p>
    </section>
    
    <section id="services" class="services">
        {services_html}
    </section>
    
    <section id="contact" class="contact">
        <h2>Get In Touch</h2>
        <p style="margin: 20px 0;">Email us at: <a href="mailto:{contact_email}" style="color: #60a5fa;">{contact_email}</a></p>
    </section>
    
    <footer>
        <p>&copy; 2024 {company_name}. All rights reserved.</p>
    </footer>
</body>
</html>
'''
        
        html_file = project_dir / "index.html"
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        project_info = {
            "name": company_name,
            "type": "business_website",
            "path": str(html_file),
            "created_at": datetime.now().isoformat(),
            "services": services
        }
        self.projects_created.append(project_info)
        
        return project_info
    
    def create_portfolio_site(
        self,
        owner_name: str,
        profession: str,
        projects: List[Dict[str, str]],
        brand_color: str = "#2563EB"
    ) -> Dict[str, Any]:
        """Create a portfolio website"""
        workspace = self.workspace_path / "webdev" / "portfolios"
        workspace.mkdir(parents=True, exist_ok=True)
        
        project_name = owner_name.lower().replace(" ", "-")
        project_dir = workspace / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        
        projects_html = "\n".join(
            f'''<div class="project-card">
                <h3>{p.get("title", "Project")}</h3>
                <p>{p.get("description", "")}</p>
                <a href="{p.get("link", "#")}" target="_blank">View Project →</a>
            </div>'''
            for p in projects
        )
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{owner_name} - {profession}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
        }}
        .hero {{
            background: linear-gradient(135deg, {brand_color} 0%, #1e40af 100%);
            color: white;
            padding: 100px 20px;
            text-align: center;
        }}
        .hero h1 {{ font-size: 3rem; margin-bottom: 10px; }}
        .hero p {{ font-size: 1.2rem; opacity: 0.9; }}
        .projects {{
            padding: 60px 20px;
            max-width: 1000px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 30px;
        }}
        .project-card {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .project-card h3 {{ color: {brand_color}; margin-bottom: 10px; }}
        .project-card a {{
            display: inline-block;
            margin-top: 15px;
            color: {brand_color};
            text-decoration: none;
            font-weight: 500;
        }}
        footer {{
            text-align: center;
            padding: 30px;
            background: #333;
            color: white;
        }}
    </style>
</head>
<body>
    <section class="hero">
        <h1>{owner_name}</h1>
        <p>{profession}</p>
    </section>
    
    <section class="projects">
        {projects_html}
    </section>
    
    <footer>
        <p>&copy; 2024 {owner_name}. All rights reserved.</p>
    </footer>
</body>
</html>
'''
        
        html_file = project_dir / "index.html"
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        project_info = {
            "name": owner_name,
            "type": "portfolio",
            "path": str(html_file),
            "created_at": datetime.now().isoformat(),
            "project_count": len(projects)
        }
        self.projects_created.append(project_info)
        
        return project_info
    
    def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a web development task"""
        context = task.context
        
        if context.get("action") == "create_landing_page":
            result = self.create_landing_page(
                product_name=context.get("product_name", "New Product"),
                product_description=context.get("product_description", ""),
                cta_text=context.get("cta_text", "Get Started"),
                features=context.get("features", []),
                brand_color=context.get("brand_color", "#2563EB")
            )
            return {"success": True, "type": "landing_page", "data": result}
        
        elif context.get("action") == "create_business_website":
            result = self.create_business_website(
                company_name=context.get("company_name", "New Company"),
                industry=context.get("industry", "Technology"),
                services=context.get("services", []),
                contact_email=context.get("contact_email", ""),
                brand_color=context.get("brand_color", "#2563EB")
            )
            return {"success": True, "type": "business_website", "data": result}
        
        elif context.get("action") == "create_portfolio":
            result = self.create_portfolio_site(
                owner_name=context.get("owner_name", "John Doe"),
                profession=context.get("profession", "Developer"),
                projects=context.get("projects", []),
                brand_color=context.get("brand_color", "#2563EB")
            )
            return {"success": True, "type": "portfolio", "data": result}
        
        prompt = f"""Create a web development solution for this task:

Title: {task.title}
Description: {task.description}

Context:
{json.dumps(context, indent=2)}

Create the appropriate HTML file(s) in the workspace. Report what you created.
"""
        
        response = self.conversation.send_message(prompt)
        
        return {
            "success": True,
            "response": response,
            "projects_created": self.projects_created
        }
