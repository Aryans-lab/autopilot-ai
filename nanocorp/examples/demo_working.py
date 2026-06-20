#!/usr/bin/env python3
"""
NanoCorp v3.0 - WORKING Demo

This demo actually uses AI to power the agents.
"""
import asyncio
import sys
import os

# Disable OpenHands telemetry FIRST
os.environ['OPENHANDS_SUPPRESS_BANNER'] = '1'
os.environ['OTEL_SDK_DISABLED'] = 'true'

# Add nanocorp to path BEFORE imports
_EXAMPLE_DIR = os.path.dirname(os.path.abspath(__file__))
_NANOCORP_DIR = os.path.dirname(os.path.dirname(_EXAMPLE_DIR))
if _NANOCORP_DIR not in sys.path:
    sys.path.insert(0, _NANOCORP_DIR)

from nanocorp.agents import AgentManager, AgentType
from nanocorp.tools.registry import register_all_tools
from nanocorp.ai import get_ai_hub


def get_result_text(result):
    """Extract readable text from task result."""
    if not result:
        return "No result"
    
    # Handle AIResponse objects
    if hasattr(result, 'content'):
        return result.content[:500]
    elif isinstance(result, dict):
        if result.get('result') and hasattr(result['result'], 'content'):
            return result['result'].content[:500]
        elif result.get('results'):
            return str(result['results'])[:500]
        elif result.get('content'):
            return str(result['content'])[:500]
        else:
            return str(result)[:500]
    else:
        return str(result)[:500]


async def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     NanoCorp - WORKING DEMO - AI-POWERED AGENTS             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Initialize AI Hub
    print("[1] Initializing AI Hub...")
    ai = get_ai_hub()
    providers = ai.list_providers()
    default = ai.get_default()
    print(f"    Available: {providers}")
    print(f"    Using: {default}")
    print()

    # Initialize tools
    print("[2] Initializing tools...")
    register_all_tools()
    print("    Tools ready!")
    print()

    # Create agent manager
    print("[3] Creating AI workforce...")
    manager = AgentManager(ai_provider=ai)
    
    # Create workforce
    ceo = manager.create_workforce(
        company_name="AIStartup",
        mission="Build amazing products with AI"
    )
    print(f"    CEO: {ceo.company_name}")
    print(f"    Mission: {ceo.mission}")
    print(f"    Workers: {len(ceo.workers)}")
    print()

    # Show available agents
    print("[4] Available Agents:")
    for worker_id, worker in ceo.workers.items():
        print(f"    - {worker.name} ({worker.type.value})")
    print()

    # Test 1: CEO thinks with AI
    print("[5] CEO Thinking with AI")
    print("-" * 50)
    response = await ceo.think("What are the 3 most important steps to launch a startup?")
    content = response.content if hasattr(response, 'content') else str(response)
    print(f"Response: {content[:300]}...")
    print()

    # Test 2: Execute a task
    print("[6] Executing Task with AI")
    print("-" * 50)
    
    task = {
        "id": "task_1",
        "title": "Write a haiku about AI",
        "type": "writing",
        "description": "Write a haiku about artificial intelligence"
    }
    
    print(f"Task: {task['title']}")
    result = await manager.execute_task(task)
    
    result_text = get_result_text(result)
    print(f"Result: {result_text}")
    print()

    # Test 3: CEO Strategic Planning
    print("[7] CEO Strategic Planning")
    print("-" * 50)
    plan = await ceo.plan_startup(
        company_name="AIStartup",
        idea="An AI-powered code review tool",
        target_market="Development teams"
    )
    print(f"Plan created:")
    print(f"    Company: {plan['company']}")
    print(f"    Goals: {plan['goals']}")
    print(f"    Tasks: {plan['tasks']}")
    print()

    # List tasks
    print("[8] Current Tasks:")
    for t in ceo.tasks[:5]:
        print(f"    [{t['status']}] {t['title']}")
    print()

    print("=" * 60)
    print("DEMO COMPLETE!")
    print("=" * 60)
    print()
    print("Your AI workforce is working!")
    print()
    print("Next steps:")
    print("1. Add API keys for real AI:")
    print("   export ANTHROPIC_API_KEY=sk-...")
    print("   export OPENAI_API_KEY=sk-...")
    print("2. Connect the frontend: nanocorp/api/")
    print()

    return {"success": True}


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result.get("success") else 1)
