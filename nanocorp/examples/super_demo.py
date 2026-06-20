"""
SuperNanoCorp Demo - v2.0 Advanced Features

Demonstrates the advanced capabilities of SuperNanoCorp v2.0 including:
- OODA Loop decision making
- Autonomous goal pursuit
- Parallel execution
- Memory and learning
"""

from nanocorp import SuperNanoCorp, SystemStatus


def demo_basic():
    """Basic SuperNanoCorp usage"""
    print("=" * 60)
    print("SUPERNANOCORP v2.0 DEMO - Basic Usage")
    print("=" * 60)
    
    # Create instance (without API key for testing)
    nano = SuperNanoCorp(
        workspace_path="./demo_workspace",
        enable_ooda=True,
        enable_memory=True,
        enable_goals=True,
        enable_parallel=True
    )
    
    # Set mission
    nano.set_mission(
        mission="Build an AI-powered SaaS product",
        vision="Revolutionize how businesses automate their workflows",
        values=["innovation", "excellence", "customer-focus"]
    )
    
    # Remember some information
    nano.remember(
        content="Target market: Small to medium businesses",
        memory_type="fact",
        importance=0.8,
        tags=["market", "target"]
    )
    
    # Recall memories
    memories = nano.recall("market")
    print(f"\nRecalled {len(memories)} memories about 'market'")
    
    # Set goals
    goal1 = nano.set_goal(
        title="Launch MVP in 30 days",
        description="Build and launch minimum viable product",
        priority="critical",
        metrics={
            "features": {"current": 0, "target": 10},
            "users": {"current": 0, "target": 100}
        }
    )
    
    # Decompose goal
    sub_goals = nano.decompose_goal(goal1.id, [
        "Design product architecture",
        "Build core features",
        "Create landing page",
        "Set up marketing",
        "Launch beta program"
    ])
    
    print(f"\nCreated goal with {len(sub_goals)} sub-goals")
    
    # Create tasks
    task1 = nano.create_task(
        title="Create landing page",
        description="Build a high-converting landing page",
        priority="high",
        category="web_dev",
        worker="WebDev"
    )
    
    task2 = nano.create_task(
        title="Write blog post",
        description="Write content about our product launch",
        priority="medium",
        category="content",
        worker="Content"
    )
    
    print(f"\nCreated {len(nano.task_manager.tasks)} tasks")
    
    # Get status
    status = nano.get_status()
    print(f"\nSystem Status:")
    print(f"  - Memory entries: {status.memory_entries}")
    print(f"  - Active goals: {status.active_goals}")
    print(f"  - Pending tasks: {status.pending_tasks}")
    
    return nano


def demo_ooda():
    """Demonstrate OODA Loop"""
    print("\n" + "=" * 60)
    print("OODA LOOP DEMO")
    print("=" * 60)
    
    nano = SuperNanoCorp(
        workspace_path="./ooda_demo",
        enable_ooda=True,
        enable_memory=False,
        enable_goals=False,
        enable_parallel=False
    )
    
    # Run OODA cycles
    for i in range(3):
        context = {
            "task_status": {
                "pending": 5 - i,
                "completed": i,
                "failed": 0
            },
            "worker_status": {
                "CEO": i,
                "WebDev": 2 * i
            }
        }
        
        result = nano.run_ooda_cycle(context)
        
        print(f"\nCycle {i + 1}:")
        print(f"  - Observations: {result['observations_collected']}")
        print(f"  - Confidence: {result['confidence']:.2f}")
        print(f"  - Threats: {result['threats']}")
        print(f"  - Opportunities: {result['opportunities']}")
        print(f"  - Decision: {result['decision']}")
    
    # Get OODA metrics
    ooda_metrics = nano.ooda.get_metrics()
    print(f"\nOODA Metrics:")
    print(f"  - Total loops: {ooda_metrics['total_loops']}")
    print(f"  - Decisions: {ooda_metrics['decisions_made']}")
    print(f"  - Success rate: {ooda_metrics['success_rate']:.1%}")


def demo_parallel():
    """Demonstrate parallel execution"""
    print("\n" + "=" * 60)
    print("PARALLEL EXECUTION DEMO")
    print("=" * 60)
    
    nano = SuperNanoCorp(
        workspace_path="./parallel_demo",
        enable_ooda=False,
        enable_memory=False,
        enable_goals=False,
        enable_parallel=True
    )
    
    # Create many tasks
    tasks = []
    for i in range(20):
        tasks.append({
            "title": f"Task {i + 1}",
            "worker": ["WebDev", "Marketing", "Content"][i % 3],
            "params": {"index": i},
            "priority": (i % 5) + 1
        })
    
    print(f"\nSubmitting {len(tasks)} tasks...")
    
    # Submit batch
    task_ids = nano.submit_batch(tasks)
    print(f"Submitted {len(task_ids)} tasks")
    
    # Execute (would run in parallel with real workers)
    results = nano.execute_parallel(max_concurrent=10)
    print(f"Executed {len(results)} tasks")


def demo_autonomous():
    """Demonstrate autonomous mode"""
    print("\n" + "=" * 60)
    print("AUTONOMOUS MODE DEMO")
    print("=" * 60)
    
    nano = SuperNanoCorp(
        workspace_path="./autonomous_demo",
        enable_ooda=True,
        enable_memory=True,
        enable_goals=True,
        enable_parallel=True,
        max_workers=10
    )
    
    # Set mission
    nano.set_mission(
        mission="Build and scale a profitable AI startup",
        vision="Make AI accessible to everyone"
    )
    
    # Set strategic goals
    goal = nano.set_goal(
        title="Build an AI-powered SaaS product",
        description="Create a minimum viable product and launch",
        priority="critical"
    )
    
    # Add sub-goals
    nano.decompose_goal(goal.id, [
        "Market research and validation",
        "Product development",
        "Marketing and launch",
        "Customer acquisition"
    ])
    
    # Set metrics
    goal.metrics = [
        {"name": "revenue", "current": 0, "target": 100000, "unit": "$"},
        {"name": "users", "current": 0, "target": 1000, "unit": ""}
    ]
    
    print(f"\nSuperNanoCorp is ready for autonomous operation!")
    print(f"Goal: {goal.title}")
    print(f"\nTo run in autopilot mode:")
    print("  nano.autopilot(duration_seconds=60)")
    print("\nOr run specific operations:")
    print("  nano.create_website('My Product', 'landing')")
    print("  nano.create_campaign('Product Launch', ['social', 'email'])")
    print("  nano.research('AI market trends', 'market')")
    
    # Get dashboard
    dashboard = nano.dashboard()
    print(f"\nDashboard preview:")
    print(f"  - Goals: {dashboard['status']['active_goals']} active")
    print(f"  - Tasks: {dashboard['status']['pending_tasks']} pending")
    print(f"  - Memory: {dashboard['status']['memory_entries']} entries")


def demo_memory():
    """Demonstrate memory system"""
    print("\n" + "=" * 60)
    print("MEMORY & LEARNING DEMO")
    print("=" * 60)
    
    nano = SuperNanoCorp(
        workspace_path="./memory_demo",
        enable_ooda=False,
        enable_memory=True,
        enable_goals=False,
        enable_parallel=False
    )
    
    # Learn from experiences
    nano.learn_from(
        experience="Blog posts with images get 2x more engagement",
        success=True,
        context={"content_type": "blog", "has_images": True}
    )
    
    nano.learn_from(
        experience="Landing pages with clear CTA convert better",
        success=True,
        context={"page_type": "landing", "has_cta": True}
    )
    
    nano.learn_from(
        experience="Cold emails with personalization get better response",
        success=True,
        context={"email_type": "cold", "personalized": True}
    )
    
    # Learn a strategy
    nano.memory.learn_strategy(
        name="Content marketing funnel",
        description="Attract users with blog content, convert with landing pages",
        conditions=["content_marketing", "conversion"],
        actions=[
            {"step": 1, "action": "create_blog_content"},
            {"step": 2, "action": "promote_on_social"},
            {"step": 3, "action": "capture_leads"},
            {"step": 4, "action": "convert_with_landing_page"}
        ],
        success=True,
        duration=30.0
    )
    
    # Recall learnings
    learnings = nano.recall("engagement")
    print(f"\nRecalled {len(learnings)} memories about 'engagement'")
    
    # Get insights
    insights = nano.get_insights()
    print(f"Generated {len(insights)} insights")
    
    # Get memory stats
    stats = nano.memory.get_statistics()
    print(f"\nMemory Statistics:")
    print(f"  - Total memories: {stats['total_memories']}")
    print(f"  - Strategies learned: {stats['strategies']}")
    print(f"  - Patterns detected: {stats['patterns']}")
    print(f"  - Average success rate: {stats['avg_success_rate']:.1%}")


def demo_goal_tree():
    """Demonstrate hierarchical goal tree"""
    print("\n" + "=" * 60)
    print("GOAL TREE DEMO")
    print("=" * 60)
    
    nano = SuperNanoCorp(
        workspace_path="./goals_demo",
        enable_ooda=False,
        enable_memory=False,
        enable_goals=True,
        enable_parallel=False
    )
    
    # Create strategic goal
    vision = nano.set_goal(
        title="Become a market leader in AI automation",
        description="Long-term vision for market leadership",
        priority="high"
    )
    
    # Create supporting goals
    goal1 = nano.set_goal(
        title="Build innovative products",
        description="Create products that differentiate us",
        priority="critical"
    )
    
    goal2 = nano.set_goal(
        title="Achieve product-market fit",
        description="Find and serve our ideal customers",
        priority="critical"
    )
    
    goal3 = nano.set_goal(
        title="Scale revenue to $10M ARR",
        description="Grow recurring revenue",
        priority="high"
    )
    
    # Decompose one goal
    sub_goals = nano.decompose_goal(goal2.id, [
        "Identify ideal customer profile",
        "Conduct customer interviews",
        "Validate pricing model",
        "Launch beta program"
    ])
    
    print(f"\nCreated goal tree:")
    print(f"  - Vision: {vision.title}")
    print(f"  - Strategic goals: 3")
    print(f"  - Operational goals: {len(sub_goals)}")
    
    # Get tree view
    tree = nano.get_goal_tree()
    print(f"\nGoal hierarchy:")
    for root in tree.get("roots", []):
        print(f"  - {root['title']} ({root['progress']:.0%})")
        for sub in root.get("sub_goals", []):
            print(f"    - {sub['title']} ({sub['progress']:.0%})")


def demo_metrics():
    """Demonstrate metrics and dashboard"""
    print("\n" + "=" * 60)
    print("METRICS & DASHBOARD DEMO")
    print("=" * 60)
    
    nano = SuperNanoCorp(
        workspace_path="./metrics_demo",
        enable_ooda=True,
        enable_memory=True,
        enable_goals=True,
        enable_parallel=True
    )
    
    # Set up some data
    nano.set_mission("Build a successful startup")
    
    for i in range(3):
        nano.set_goal(
            title=f"Goal {i + 1}",
            priority=["critical", "high", "medium"][i]
        )
    
    nano.remember("Important market insight", "fact", importance=0.9)
    nano.remember("Successful strategy learned", "strategy", importance=0.8)
    
    # Get comprehensive metrics
    metrics = nano.get_metrics()
    
    print("\nSystem Metrics:")
    for section, data in metrics.items():
        print(f"\n  {section.upper()}:")
        if isinstance(data, dict):
            for key, value in list(data.items())[:5]:
                print(f"    - {key}: {value}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("WELCOME TO SUPERNANOCORP v2.0")
    print("=" * 60)
    print("\nThis demo showcases the advanced capabilities of")
    print("SuperNanoCorp - the autonomous AI business system.\n")
    
    # Run demos
    demo_basic()
    demo_ooda()
    demo_parallel()
    demo_memory()
    demo_goal_tree()
    demo_metrics()
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("\nTo run SuperNanoCorp:")
    print("""
    from nanocorp import SuperNanoCorp
    
    nano = SuperNanoCorp(
        api_key="your-api-key",
        workspace_path="./my_workspace"
    )
    
    nano.set_mission("Your company mission")
    nano.set_goal("Your primary goal", priority="critical")
    
    # Run in autopilot mode
    nano.autopilot(duration_seconds=3600)
    
    # Or run specific tasks
    nano.create_website("My Product", "landing")
    nano.create_campaign("Product Launch")
    """)
