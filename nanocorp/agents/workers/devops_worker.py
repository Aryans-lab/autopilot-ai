"""DevOpsWorker 2.0 - Elite Infrastructure & Deployment Automation"""

import os
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path
import yaml

from .base import BaseWorker


class DevOpsWorker(BaseWorker):
    """Elite DevOps Engineer for infrastructure automation"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "DevOpsWorker"
        self.version = "2.0"
        self.specialties = ["CI/CD", "Docker", "Kubernetes", "AWS", "Terraform", "Monitoring"]
        
        self.metrics = {
            "deployments": 0, "pipelines_created": 0, "containers_built": 0,
            "infrastructure_changes": 0, "success_rate": 100.0
        }
        
        self.system_prompt = "You are a world-class DevOps Engineer with expertise in CI/CD, containers, cloud deployment, and IaC."

    async def create_github_actions_pipeline(self, repo_name: str, pipeline_type: str = "full") -> Dict[str, Any]:
        """Create GitHub Actions CI/CD pipeline"""
        workflows_dir = Path(f"{repo_name}/.github/workflows")
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        ci_workflow = {
            "name": "CI/CD Pipeline",
            "on": {"push": {"branches": ["main"]}, "pull_request": {"branches": ["main"]}},
            "jobs": {
                "test": {"runs-on": "ubuntu-latest", "steps": [
                    {"uses": "actions/checkout@v3"},
                    {"name": "Run tests", "run": "pytest"}
                ]},
                "build": {"needs": "test", "runs-on": "ubuntu-latest", "steps": [
                    {"uses": "actions/checkout@v3"},
                    {"name": "Build Docker", "run": "docker build -t app:latest ."}
                ]}
            }
        }
        
        with open(workflows_dir / "ci-cd.yml", 'w') as f:
            yaml.dump(ci_workflow, f)
        
        self.metrics["pipelines_created"] += 1
        return {"status": "success", "path": str(workflows_dir), "message": "CI/CD pipeline created"}

    async def create_docker_setup(self, app_name: str, port: int = 8000) -> Dict[str, Any]:
        """Create Docker configuration"""
        app_path = Path(app_name)
        
        dockerfile = f"""FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE {port}
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{port}"]
"""
        with open(app_path / "Dockerfile", 'w') as f:
            f.write(dockerfile)
        
        compose = {
            "version": "3.8",
            "services": {
                "app": {"build": ".", "ports": [f"{port}:{port}"]},
                "db": {"image": "postgres:15", "environment": {"POSTGRES_PASSWORD": "pass"}}
            }
        }
        with open(app_path / "docker-compose.yml", 'w') as f:
            yaml.dump(compose, f)
        
        self.metrics["containers_built"] += 1
        return {"status": "success", "files": ["Dockerfile", "docker-compose.yml"]}

    async def get_metrics(self) -> Dict[str, Any]:
        return {**self.metrics, "worker": self.name, "timestamp": datetime.now().isoformat()}
