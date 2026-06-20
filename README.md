# 🚀 NanoCorp v3.0 - The Ultimate Autonomous AI Agent System

<p align="center">
  <img src="https://img.shields.io/badge/Version-3.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.10+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-purple.svg" alt="License">
  <img src="https://img.shields.io/badge/AI%20Agents-8+-orange.svg" alt="Agents">
</p>

> **Build and run your entire business with AI agents.** NanoCorp is an autonomous AI operating system that coordinates a team of specialized agents to execute tasks, build products, and scale your business.

## ✨ Features

### 🤖 AI Agent Workforce
- **CEO Agent** - Strategic planning, task decomposition, and coordination
- **8 Specialized Workers** - Coder, Designer, Researcher, Marketer, Writer, Data, DevOps

### 🛠️ Unified Tool System (15+ tools)
- **Filesystem** - Read, write, edit, search files
- **Code** - Bash, git, Python exec, linting, testing
- **Web** - HTTP, scraping, search

### 🧠 Memory & Learning
- **Vector Embeddings** - Semantic search with ChromaDB
- **Memory Types** - Episodic, semantic, procedural
- **Learning Engine** - Improves from experiences

### 🔌 Integrations
- **MCP (Model Context Protocol)** - Connect to any MCP server
- **Skills** - Tavily, GitHub, Slack, Linear
- **API Server** - REST API with FastAPI
- **Webhooks** - Event-driven automation

## 📦 Installation

```bash
# Clone the repo
git clone https://github.com/Aryans-lab/autopilot-ai.git
cd autopilot-ai

# Install dependencies
pip install -e .

# Or with all features
pip install -e ".[all]"
```

## 🚀 Quick Start

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

# Execute tasks
import asyncio
results = asyncio.run(manager.execute_parallel([
    {"title": "Research AI trends", "type": "research"},
    {"title": "Build landing page", "type": "coding"},
    {"title": "Create marketing plan", "type": "marketing"}
]))
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│            CLI │ REST API │ WebSocket │ Demo                │
├─────────────────────────────────────────────────────────────┤
│                      SKILL LAYER                             │
│         Tavily │ GitHub │ Slack │ Linear │ Notion          │
├─────────────────────────────────────────────────────────────┤
│                      TOOL LAYER                              │
│    Files │ Code │ Web │ Data │ Git │ API │ Sandbox         │
├─────────────────────────────────────────────────────────────┤
│                      MCP LAYER                               │
│            MCP Client │ MCP Servers │ Bridge                │
├─────────────────────────────────────────────────────────────┤
│                   AGENT LAYER                               │
│      CEO │ Coder │ Designer │ Researcher │ DevOps           │
├─────────────────────────────────────────────────────────────┤
│                   ORCHESTRATION                             │
│         Task Manager │ Goal Engine │ Scheduler              │
├─────────────────────────────────────────────────────────────┤
│                    MEMORY LAYER                             │
│     Vector DB │ ChromaDB │ Semantic Search │ Insights       │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
autopilot-ai/
├── nanocorp/
│   ├── __init__.py          # Main package
│   ├── agents/              # Agent system
│   │   ├── base.py         # BaseAgent
│   │   ├── ceo.py          # CEOAgent
│   │   ├── worker.py       # Worker agents
│   │   └── manager.py      # AgentManager
│   ├── tools/              # Tool system
│   │   ├── base.py         # Tool interface
│   │   ├── filesystem.py   # File tools
│   │   ├── code.py         # Code tools
│   │   ├── web.py          # Web tools
│   │   └── registry.py     # Tool registry
│   ├── memory/             # Memory system
│   │   └── core.py         # AgentMemory
│   ├── mcp/                # MCP (Model Context Protocol)
│   │   └── client.py       # MCP client
│   ├── skills/             # Skills
│   ├── config/             # Configuration
│   ├── logging/            # Logging
│   ├── sandbox/            # Code sandbox
│   ├── scheduler/           # Task scheduler
│   ├── api/                # REST API
│   ├── webhooks.py         # Webhook system
│   └── examples/           # Examples
├── tests/                  # Test suite
├── docs/                   # Documentation
└── pyproject.toml          # Package config
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_tools.py -v

# With coverage
pytest tests/ --cov=nanocorp --cov-report=html
```

## 🔧 Configuration

Create a `.env` file:

```bash
# AI Provider
AI_PROVIDER=auto
AI_MODEL=sonnet

# Free Mode (no API key)
FREE_MODE=true

# Memory
EMBEDDING_PROVIDER=sentence-transformers
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Skills
TAVILY_API_KEY=your_key

# GitHub
GITHUB_TOKEN=your_token
```

## 🌐 API Server

```python
from nanocorp.api import NanoCorpAPI
from nanocorp.agents import AgentManager

# Create API
manager = AgentManager()
manager.create_workforce()
api = NanoCorpAPI(agent_manager=manager)

# Run server
api.run()  # Starts on http://localhost:8000
```

## 📚 Documentation

- [Architecture](./docs/architecture.md)
- [Agent System](./docs/agents.md)
- [Tool System](./docs/tools.md)
- [Memory System](./docs/memory.md)
- [API Reference](./docs/api.md)

## 🎯 Use Cases

- **Startup Automation** - Build and launch products
- **Research** - Web scraping and analysis
- **Development** - Code generation and testing
- **Marketing** - Content creation and campaigns
- **Operations** - Task automation and scheduling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a PR

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

<p align="center">
  <strong>Built with ❤️ by AI agents for AI agents</strong>
</p>
