# NanoCorp - Autonomous AI Startup System v2.1

**State-of-the-art AI business operating system. No API key needed!**

## 🚀 What's New in v2.1

| Feature | Description |
|---------|-------------|
| **Vector Memory** | Semantic search over all past work |
| **Self-Improvement** | Learns from success/failure, auto-optimizes |
| **Real Integrations** | Send emails, deploy sites, post to social |
| **Agent Spawning** | Dynamic team assembly for parallel work |
| **Docker Ready** | One-click deployment anywhere |

## Quick Start

```python
from nanocorp import NanoCorpFull, quick_start_full

# Full system - all features!
nano = quick_start_full("My Startup", "Build amazing products")

# Create tasks
nano.create_website("My Product", "landing")
nano.create_campaign("Launch", channels=["social"])

# Run with learning
nano.run_with_learning()

# Or use FREE mode (lighter)
from nanocorp import NanoCorpFree, quick_start
nano = quick_start("My Startup", "Mission")
nano.run()
```

## AI Providers (No API Key!)

| Provider | Cost | Setup |
|----------|------|-------|
| **Claude ACP** | FREE (Anthropic) | `npx -y @agentclientprotocol/claude-agent-acp` |
| **Codex ACP** | ChatGPT Plus | `npx -y @zed-industries/codex-acp` |
| **Ollama** | FREE (local) | `curl -fsSL https://ollama.com/install.sh \| sh` |

## Key Features

### 📚 Vector Memory
```python
nano.remember("Users prefer simple onboarding", importance=0.9)
similar = nano.recall("onboarding")  # Semantic search
```

### 🧠 Self-Improvement
```python
nano.learn_from("Video landing pages convert 3x better", success=True)
insights = nano.auto_improve()
```

### 📧 Real Integrations
```python
# Configure once
nano.integrations.configure("email", username="...", password="...")

# Actually send emails!
nano.send_email("user@example.com", "Subject", "<h1>Hello!</h1>")

# Deploy websites!
nano.deploy_website("./landing-page", platform="vercel")

# Post to Twitter!
nano.post_twitter("We just launched! 🚀 #startup")
```

### 🤖 Agent Spawning
```python
# Spawn a specialist for a task
nano.spawn_agent("coder", "Build a checkout flow")

# Or assemble a whole team
team = nano.assemble_team(["coder", "designer", "marketer"])
```

### 🐳 Docker Deployment
```bash
docker-compose up -d
# Runs with Ollama for completely free AI!
```

## Architecture

```
NanoCorp Full
├── Vector Memory      # Semantic search & learning
├── Learning Engine    # Auto-improvement
├── Integration Manager # Real actions
├── Agent Spawner     # Dynamic teams
├── 8 Worker Agents   # Specialized execution
└── Docker Ready      # Deploy anywhere
```

## Installation

```bash
pip install nanocorp
```

## License

MIT
