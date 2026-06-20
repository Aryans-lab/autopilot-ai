#!/usr/bin/env python3
"""
NanoCorp v3.0 - Demo Script

Demonstrates the full agent workforce in action.
"""
import asyncio
import sys
sys.path.insert(0, '.')

from nanocorp.agents import AgentManager, AgentType
from nanocorp.tools.registry import register_all_tools, get_registry
from nanocorp.memory import AgentMemory
from nanocorp.logging import setup_logging, logger


async def main():
    """Run the demo."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗            ║
║     ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝            ║
║     ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗            ║
║     ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║            ║
║     ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║            ║
║     ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝ v3.0     ║
║                                                              ║
║     The Ultimate Autonomous AI Agent System                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Setup logging
    setup_logging(level="INFO")
    
    # Initialize tools
    logger.info("Initializing tools...")
    register_all_tools()
    tools = get_registry()
    logger.info(f"Registered {len(tools.list_all())} tools")
    
    # Initialize memory
    logger.info("Initializing memory...")
    memory = AgentMemory(persist_dir="./.demo_memory")
    logger.info(f"Memory initialized with {memory.stats()['total_memories']} entries")
    
    # Create agent manager
    logger.info("Creating workforce...")
    manager = AgentManager(memory=memory)
    
    # Create workforce
    ceo = manager.create_workforce(
        company_name="DemoCorp",
        mission="Build amazing AI products",
        worker_types=[
            AgentType.CODER,
            AgentType.DESIGNER,
            AgentType.RESEARCHER,
            AgentType.MARKETER,
            AgentType.WRITER
        ]
    )
    
    # Show workforce
    logger.info("=" * 50)
    logger.info("WORKFORCE CREATED")
    logger.info("=" * 50)
    
    for agent_id, agent in manager.agents.items():
        logger.info(f"  • {agent.name} ({agent.type.value})")
        logger.info(f"    Tools: {len(agent.list_available_tools())}")
    
    # Create and execute tasks
    logger.info("")
    logger.info("=" * 50)
    logger.info("EXECUTING TASKS")
    logger.info("=" * 50)
    
    tasks = [
        {
            "id": "task_1",
            "title": "Research AI coding assistants",
            "type": "research",
            "description": "Find information about AI coding assistants like GitHub Copilot"
        },
        {
            "id": "task_2", 
            "title": "Create landing page design",
            "type": "design",
            "description": "Design a modern landing page for an AI product"
        },
        {
            "id": "task_3",
            "title": "Write product description",
            "type": "writing",
            "description": "Write compelling product description for an AI tool"
        },
        {
            "id": "task_4",
            "title": "Plan marketing campaign",
            "type": "marketing",
            "description": "Create a go-to-market plan for a new AI product"
        }
    ]
    
    # Execute tasks in parallel
    results = await manager.execute_parallel(tasks)
    
    logger.info("")
    logger.info("=" * 50)
    logger.info("RESULTS")
    logger.info("=" * 50)
    
    for i, result in enumerate(results):
        status = "✓" if result.get("success") else "✗"
        task_title = tasks[i]["title"]
        logger.info(f"{status} {task_title}")
        if not result.get("success"):
            logger.error(f"  Error: {result.get('error')}")
    
    # Show dashboard
    logger.info("")
    logger.info("=" * 50)
    logger.info("WORKFORCE DASHBOARD")
    logger.info("=" * 50)
    
    dashboard = manager.get_dashboard()
    stats = dashboard["stats"]
    
    logger.info(f"  Total Agents: {stats['total_agents']}")
    logger.info(f"  Active: {stats['active_agents']}")
    logger.info(f"  Tasks Completed: {stats['tasks_completed']}")
    logger.info(f"  Uptime: {stats['uptime']}")
    
    # Show memory
    logger.info("")
    logger.info("=" * 50)
    logger.info("MEMORY")
    logger.info("=" * 50)
    
    mem_stats = memory.stats()
    logger.info(f"  Total Memories: {mem_stats['total_memories']}")
    logger.info(f"  By Type: {mem_stats['by_type']}")
    
    # Recall test
    memories = memory.recall("AI products", limit=3)
    if memories:
        logger.info("")
        logger.info("  Recent AI-related memories:")
        for entry, score in memories:
            logger.info(f"    • {entry.content[:50]}... (relevance: {score:.2f})")
    
    logger.info("")
    logger.info("=" * 50)
    logger.info("DEMO COMPLETE!")
    logger.info("=" * 50)
    
    return {
        "success": True,
        "tasks_executed": len(tasks),
        "results": results,
        "stats": stats
    }


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result.get("success") else 1)
