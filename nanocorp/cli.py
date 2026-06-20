#!/usr/bin/env python3
"""
NanoCorp CLI - Command Line Interface for NanoCorp

Usage:
    python cli.py init                    # Initialize a new project
    python cli.py status                  # Show current status
    python cli.py board                   # Show task board
    python cli.py run                     # Execute pending tasks
    python cli.py create <task>          # Create a task
    python cli.py chat <message>          # Chat with CEO
    python cli.py interactive             # Start interactive mode
"""
import os
import sys
import argparse
from pathlib import Path

# Add package to path
sys.path.insert(0, str(Path(__file__).parent))

from nanocorp import NanoCorp, quick_start, config


def init_workspace(name: str, mission: str):
    """Initialize a new NanoCorp workspace"""
    workspace = Path(f"./{name.replace(' ', '_').lower()}_workspace")
    workspace.mkdir(exist_ok=True)
    
    nanocorp = quick_start(
        company_name=name,
        mission=mission,
        workspace_path=str(workspace)
    )
    
    print(f"✅ Created NanoCorp workspace: {workspace}")
    print(f"   Company: {name}")
    print(f"   Mission: {mission}")
    print(f"\nGet started:")
    print(f"   cd {workspace}")
    print(f"   python -c \"from nanocorp import NanoCorp; n = NanoCorp(); n.start()\"")
    
    return nanocorp


def main():
    parser = argparse.ArgumentParser(
        description="NanoCorp - Autonomous AI Startup System"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # init command
    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument("--name", "-n", default="My Startup", help="Company name")
    init_parser.add_argument("--mission", "-m", default="Building the future", help="Mission statement")
    
    # status command
    subparsers.add_parser("status", help="Show current status")
    
    # board command
    subparsers.add_parser("board", help="Show task board")
    
    # stats command
    subparsers.add_parser("stats", help="Show statistics")
    
    # run command
    run_parser = subparsers.add_parser("run", help="Execute pending tasks")
    run_parser.add_argument("--max", "-m", type=int, default=None, help="Max tasks to run")
    
    # create command
    create_parser = subparsers.add_parser("create", help="Create a task")
    create_parser.add_argument("task", help="Task description")
    create_parser.add_argument("--worker", "-w", help="Worker to assign")
    create_parser.add_argument("--priority", "-p", default="medium", choices=["critical", "high", "medium", "low"])
    
    # chat command
    chat_parser = subparsers.add_parser("chat", help="Chat with CEO")
    chat_parser.add_argument("message", help="Message to CEO")
    
    # interactive command
    subparsers.add_parser("interactive", help="Start interactive mode")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Load existing workspace or create new one
    workspace = Path("./nanocorp_workspace")
    
    if args.command == "init":
        init_workspace(args.name, args.mission)
        return
    
    # Load existing workspace
    if workspace.exists():
        nanocorp = NanoCorp(workspace_path=str(workspace))
    else:
        print("❌ No workspace found. Run 'nanocorp init' first.")
        return
    
    # Execute command
    if args.command == "status":
        status = nanocorp.status()
        import json
        print(json.dumps(status, indent=2))
    
    elif args.command == "board":
        board = nanocorp.board()
        import json
        print(json.dumps(board, indent=2))
    
    elif args.command == "stats":
        stats = nanocorp.stats()
        import json
        print(json.dumps(stats, indent=2))
    
    elif args.command == "run":
        results = nanocorp.run(max_tasks=args.max)
        print(f"✅ Executed {len(results)} tasks")
    
    elif args.command == "create":
        task = nanocorp.assign(args.task, worker=args.worker, priority=args.priority)
        print(f"✅ Created task: {task.title} (ID: {task.id})")
    
    elif args.command == "chat":
        response = nanocorp.chat(args.message)
        print(f"\nCEO: {response}")
    
    elif args.command == "interactive":
        nanocorp.start()


if __name__ == "__main__":
    main()
