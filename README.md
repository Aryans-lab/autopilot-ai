# NanoCorp - Autonomous AI Agent System

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)

**Build and run your entire startup with AI agents.** NanoCorp coordinates a team of specialized agents to code, design, research, market, and scale your business.

</div>

---

## Quick Start

### 1. Clone & Run Demo

```bash
git clone https://github.com/Aryans-lab/autopilot-ai.git
cd autopilot-ai

# Run the working demo
python nanocorp/examples/demo_working.py
```

### 2. Start the API Server

```bash
# In one terminal
python -m nanocorp.api.server

# Then open in browser:
# - API docs: http://localhost:8000/docs
# - Dashboard: frontend/demo.html
```

### 3. Add API Keys (Optional)

```bash
export ANTHROPIC_API_KEY=sk-...    # For Claude
export OPENAI_API_KEY=sk-...       # For GPT-4
```

---

## Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Agents** | CEO + 5 workers (Coder, Designer, Researcher, Marketer, Writer) |
| 🧠 **Real AI** | Connects to Claude, GPT-4, Ollama, or simulates |
| 🌐 **REST API** | FastAPI server with all endpoints |
| 📊 **Dashboard** | Web UI to control your AI workforce |
| 🛠️ **Tools** | Filesystem, code execution, web search |
| 📝 **Memory** | Vector embeddings for context |

---

## Project Structure

```
autopilot-ai/
├── frontend/
│   ├── index.html      # Premium dashboard (visual demo)
│   └── demo.html       # Working dashboard (connects to API)
├── nanocorp/
│   ├── agents/         # CEO and worker agents
│   ├── ai/            # AI providers (Claude, GPT, Ollama)
│   ├── api/           # FastAPI REST server
│   ├── tools/         # Filesystem, web, code tools
│   └── examples/      # Demo scripts
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| POST | `/workforce` | Create workforce |
| GET | `/agents` | List all agents |
| POST | `/tasks` | Execute a task |
| GET | `/stats` | Get statistics |

---

## Demo Output

```
╔══════════════════════════════════════════════════════════════╗
║     NanoCorp - WORKING DEMO - AI-POWERED AGENTS             ║
╚══════════════════════════════════════════════════════════════╝

[1] AI Hub initialized (simulation mode)
[2] Tools ready
[3] Workforce created: AIStartup
[4] 5 workers active

[5] CEO Thinking with AI...
Response: [SIMULATED AI] Prompt: What are the 3 most important...

[6] Task executed successfully
[7] Strategic plan created (3 goals, 9 tasks)

DEMO COMPLETE!
```

---

## License

MIT - See [LICENSE](LICENSE)
