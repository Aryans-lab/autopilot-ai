# 🚀 NanoCorp - Autonomous AI Agent System

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Stars](https://img.shields.io/github/stars/Aryans-lab/autopilot-ai?style=social)](https://github.com/Aryans-lab/autopilot-ai/stargazers)

**Build and run your entire startup with AI agents.** NanoCorp coordinates a team of specialized agents to code, design, research, market, and scale your business.

[Live Demo](frontend/index.html) • [Quick Start](#-quick-start) • [Features](#-features)

</div>

---

## 🎨 See It In Action

**Open the Mission Control Dashboard:**

```bash
# Option 1: Direct file (works offline)
open frontend/index.html

# Option 2: Serve locally
cd frontend && python -m http.server 8080
# Then open http://localhost:8080
```

The dashboard features:
- 🌌 Animated particle system with neural network visualization
- 💻 Live terminal showing AI agent activity
- 📈 Performance charts and metrics
- 🎯 Command palette (press Ctrl+K)

---

## ⚡ Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/Aryans-lab/autopilot-ai.git
cd autopilot-ai
pip install -e .
```

### 2. Run the Demo

```python
from nanocorp.agents import AgentManager
from nanocorp.tools.registry import register_all_tools

# Initialize
register_all_tools()

# Create AI workforce
manager = AgentManager()
ceo = manager.create_workforce(
    company_name="MyStartup",
    mission="Build the next unicorn"
)

# Execute tasks
import asyncio
results = asyncio.run(manager.execute_parallel([
    {"title": "Research our competitors", "type": "research"},
    {"title": "Build landing page", "type": "coding"},
    {"title": "Create marketing plan", "type": "marketing"},
]))
```

### 3. Open the Dashboard

```bash
open frontend/index.html
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **9 AI Agents** | CEO, Coder, Designer, Researcher, Marketer, Writer, Data, DevOps |
| 🛠️ **15+ Tools** | Filesystem, code execution, web scraping, HTTP requests |
| 🧠 **Vector Memory** | Semantic search with ChromaDB embeddings |
| 🔌 **MCP Support** | Model Context Protocol integration |
| 🌐 **REST API** | FastAPI server with WebSocket support |
| ⏰ **Scheduler** | Cron-based task scheduling |
| 🪝 **Webhooks** | Event-driven automation |
| 🎨 **Mission Control** | Beautiful YC-ready dashboard |

---

## 📁 Project Structure

```
autopilot-ai/
├── frontend/
│   └── index.html          # Mission Control Dashboard
├── nanocorp/
│   ├── agents/              # AI agents (CEO + 8 workers)
│   ├── tools/              # 15+ tools
│   ├── memory/              # Vector embeddings
│   ├── mcp/                 # MCP protocol
│   ├── skills/              # Skills system
│   ├── api/                 # REST API
│   ├── sandbox/             # Code sandbox
│   └── scheduler/           # Task scheduler
├── tests/                   # pytest tests
└── README.md
```

---

## 🧪 Run Tests

```bash
pytest tests/ -v
```

---

## 🌐 REST API

```python
from nanocorp.api import NanoCorpAPI
from nanocorp.agents import AgentManager

manager = AgentManager()
manager.create_workforce("MyCorp", "Build products")
api = NanoCorpAPI(agent_manager=manager, port=8000)
api.run()
```

**Endpoints:**
- `GET /` - Health check
- `GET /agents` - List agents
- `POST /tasks` - Create task
- `GET /stats` - Stats

---

## 🔧 Configuration

```bash
# .env file
AI_PROVIDER=auto
ANTHROPIC_API_KEY=sk-...      # Optional
OPENAI_API_KEY=sk-...         # Optional
EMBEDDING_PROVIDER=sentence-transformers
TAVILY_API_KEY=tvly-...       # Optional
GITHUB_TOKEN=ghp_...          # Optional
```

---

## 📜 License

MIT License - see [LICENSE](LICENSE)

---

**Built for the future of AI-powered startups**
