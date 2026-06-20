# 🚀 NanoCorp - Autonomous AI Agent System

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Stars](https://img.shields.io/github/stars/Aryans-lab/autopilot-ai?style=social)](https://github.com/Aryans-lab/autopilot-ai/stargazers)

**Build and run your entire business with AI agents.** NanoCorp is an autonomous AI operating system that coordinates a team of specialized agents.

[Getting Started](#-getting-started) • [Features](#-features) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

## ✨ Features

- 🤖 **9 AI Agents** - CEO, Coder, Designer, Researcher, Marketer, Writer, Data, DevOps
- 🛠️ **15+ Tools** - Filesystem, Code, Web, Search
- 🧠 **Vector Memory** - Semantic search with real embeddings
- 🔌 **MCP Support** - Model Context Protocol integration
- 🌐 **REST API** - FastAPI-powered API server
- ⏰ **Scheduler** - Cron-based task scheduling
- 🪝 **Webhooks** - Event-driven automation

## 📦 Quick Install

```bash
git clone https://github.com/Aryans-lab/autopilot-ai.git
cd autopilot-ai
pip install -e .
```

## 🚀 Getting Started

```python
from nanocorp.agents import AgentManager, AgentType
from nanocorp.tools.registry import register_all_tools

# Initialize
register_all_tools()
manager = AgentManager()

# Create workforce
ceo = manager.create_workforce(
    company_name="MyCorp",
    mission="Build amazing products"
)

# Run demo
import asyncio
results = asyncio.run(manager.execute_parallel([
    {"title": "Research AI trends", "type": "research"},
    {"title": "Build landing page", "type": "coding"},
]))
```

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│  API Server │ CLI │ Webhooks        │
├─────────────────────────────────────┤
│  Skills: Tavily, GitHub, Slack      │
├─────────────────────────────────────┤
│  Tools: Files │ Code │ Web          │
├─────────────────────────────────────┤
│  MCP Client                         │
├─────────────────────────────────────┤
│  CEO │ Coder │ Designer │ ...       │
├─────────────────────────────────────┤
│  Memory: Vector + ChromaDB           │
└─────────────────────────────────────┘
```

## 📂 Project Structure

```
nanocorp/
├── agents/          # AI agents (CEO, Workers)
├── tools/           # 15+ tools
├── memory/           # Vector embeddings
├── mcp/             # MCP protocol
├── skills/           # Skills system
├── api/              # REST API
├── sandbox/          # Code sandbox
└── scheduler/        # Task scheduler
```

## 🧪 Testing

```bash
pytest tests/ -v
```

## 📄 License

MIT License - see [LICENSE](LICENSE)
