"""
NanoCorp Demo - Autonomous AI Startup System

This script demonstrates how to use NanoCorp to automate your startup operations.

Requirements:
    pip install openhands-sdk openhands-tools python-dotenv pydantic

Usage:
    python demo.py
    
    Or set your API key:
    export OPENAI_API_KEY="your-key-here"
    python demo.py
"""
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from nanocorp import NanoCorp, quick_start


def demo_basic_setup():
    """Demo: Basic NanoCorp setup"""
    print("\n" + "=" * 60)
    print("DEMO 1: Basic Setup")
    print("=" * 60)
    
    # Check for API key
    api_key = os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        print("⚠️  No API key found. Set LLM_API_KEY or OPENAI_API_KEY environment variable.")
        print("   Demo will show the structure but won't execute LLM calls.")
    
    # Create NanoCorp instance
    nanocorp = NanoCorp(
        api_key=api_key,
        workspace_path="./nanocorp_workspace"
    )
    
    # Set up company
    nanocorp.set_company(
        name="TechStartup AI",
        mission="Build revolutionary AI products for small businesses",
        industry="AI/SaaS",
        target_market="Small businesses and solopreneurs"
    )
    
    print(f"✅ Created NanoCorp for: {nanocorp.ceo.company_context['name']}")
    print(f"   Mission: {nanocorp.ceo.company_context['mission']}")
    print(f"   Workers: {', '.join(nanocorp.workers.keys())}")
    
    return nanocorp


def demo_website_creation(nanocorp: NanoCorp):
    """Demo: Create a landing page"""
    print("\n" + "=" * 60)
    print("DEMO 2: Create a Landing Page")
    print("=" * 60)
    
    # Create a landing page for a new product
    result = nanocorp.create_website(
        name="AI Assistant Pro",
        website_type="landing",
        product_description="The ultimate AI assistant for professionals who want to 10x their productivity",
        cta_text="Start Free Trial",
        features=[
            "Smart task management",
            "Meeting transcription",
            "Email drafting",
            "Research assistance",
            "Calendar optimization"
        ],
        brand_color="#7C3AED"
    )
    
    print(f"✅ Landing page created!")
    print(f"   Type: {result.get('type', 'N/A')}")
    print(f"   Success: {result.get('success', False)}")
    
    # Check the workspace
    workspace = Path("./nanocorp_workspace/webdev/landing_pages/ai-assistant-pro")
    if workspace.exists():
        files = list(workspace.glob("*"))
        print(f"   Files created: {[f.name for f in files]}")


def demo_marketing_campaign(nanocorp: NanoCorp):
    """Demo: Create a marketing campaign"""
    print("\n" + "=" * 60)
    print("DEMO 3: Create a Marketing Campaign")
    print("=" * 60)
    
    # Create a marketing campaign
    result = nanocorp.create_marketing_campaign(
        name="AI Assistant Pro Launch",
        campaign_type="product_launch",
        channels=["social", "email", "content"],
        target_audience="Small business owners and solopreneurs aged 30-50",
        call_to_action="Start your free trial today!",
        duration_weeks=4
    )
    
    print(f"✅ Marketing campaign created!")
    print(f"   Type: {result.get('type', 'N/A')}")
    print(f"   Success: {result.get('success', False)}")
    
    # Check the workspace
    workspace = Path("./nanocorp_workspace/marketing/campaigns")
    if workspace.exists():
        files = list(workspace.glob("*.md"))
        print(f"   Files created: {[f.name for f in files]}")


def demo_social_content(nanocorp: NanoCorp):
    """Demo: Create social media content"""
    print("\n" + "=" * 60)
    print("DEMO 4: Create Social Media Content")
    print("=" * 60)
    
    # Create social media posts
    result = nanocorp.create_social_content(
        topic="AI productivity tips for entrepreneurs",
        platforms=["twitter", "linkedin", "instagram"],
        num_posts=5,
        brand_voice="Helpful, professional, and slightly witty"
    )
    
    print(f"✅ Social content created!")
    print(f"   Type: {result.get('type', 'N/A')}")
    print(f"   Success: {result.get('success', False)}")
    
    # Check the workspace
    workspace = Path("./nanocorp_workspace/social/posts")
    if workspace.exists():
        files = list(workspace.glob("*.md"))
        print(f"   Files created: {[f.name for f in files]}")


def demo_email_campaign(nanocorp: NanoCorp):
    """Demo: Create email campaigns"""
    print("\n" + "=" * 60)
    print("DEMO 5: Create Email Campaign")
    print("=" * 60)
    
    # Create newsletter
    result = nanocorp.create_email_campaign(
        "newsletter",
        company_name="TechStartup AI",
        edition="April 2024 Newsletter",
        sections=[
            {"title": "🚀 Product Update", "content": "We're excited to announce AI Assistant Pro is now available!"},
            {"title": "📊 Tips & Tricks", "content": "5 ways to boost your productivity with AI"},
            {"title": "🎯 Upcoming Events", "content": "Join us at TechCrunch Disrupt booth #1234"}
        ],
        brand_color="#7C3AED"
    )
    
    print(f"✅ Email newsletter created!")
    print(f"   Type: {result.get('type', 'N/A')}")
    
    # Create drip sequence
    result2 = nanocorp.create_email_campaign(
        "drip",
        sequence_name="Free Trial Onboarding",
        product_name="AI Assistant Pro",
        prospect_type="New trial users",
        stages=5
    )
    
    print(f"✅ Drip sequence created!")
    print(f"   Type: {result2.get('type', 'N/A')}")


def demo_document_creation(nanocorp: NanoCorp):
    """Demo: Create business documents"""
    print("\n" + "=" * 60)
    print("DEMO 6: Create Business Documents")
    print("=" * 60)
    
    # Create a business proposal
    result = nanocorp.create_document(
        "proposal",
        client_name="Acme Corporation",
        project_name="Enterprise AI Integration",
        services=[
            "AI Consultation",
            "Custom Integration",
            "Team Training",
            "Ongoing Support"
        ],
        pricing="$50,000 - $100,000 depending on scope",
        timeline="3-6 months"
    )
    
    print(f"✅ Business proposal created!")
    print(f"   Type: {result.get('type', 'N/A')}")
    
    # Create business plan
    result2 = nanocorp.create_document(
        "plan",
        company_name="TechStartup AI",
        business_idea="AI-powered productivity tools for small businesses",
        target_market="Small businesses with 1-20 employees",
        revenue_model="Subscription-based SaaS ($29-99/month)",
        competitive_advantage="Specialized for small business needs, affordable pricing, easy to use"
    )
    
    print(f"✅ Business plan created!")
    print(f"   Type: {result2.get('type', 'N/A')}")


def demo_research(nanocorp: NanoCorp):
    """Demo: Conduct research"""
    print("\n" + "=" * 60)
    print("DEMO 7: Market Research")
    print("=" * 60)
    
    # Conduct market research
    result = nanocorp.research(
        topic="AI productivity software market",
        research_type="market",
        market_size="$50 billion by 2025",
        target_segments=[
            "Solopreneurs",
            "Small businesses (1-20 employees)",
            "Freelancers and consultants"
        ],
        key_trends=[
            "Increasing adoption of AI tools",
            "Remote work acceleration",
            "Integration with existing workflows"
        ],
        opportunities=[
            "Untapped small business segment",
            "Vertical-specific AI solutions",
            "Training and education services"
        ]
    )
    
    print(f"✅ Market research completed!")
    print(f"   Type: {result.get('type', 'N/A')}")
    
    # Competitive analysis
    result2 = nanocorp.research(
        topic="AI Assistant Pro",
        research_type="competitive",
        your_company="TechStartup AI",
        competitors=[
            {
                "name": "Competitor A",
                "strengths": "Brand recognition, large team",
                "weaknesses": "Expensive, complex",
                "market_share": "35%"
            },
            {
                "name": "Competitor B",
                "strengths": "Tech innovation",
                "weaknesses": "Limited features",
                "market_share": "20%"
            }
        ],
        market_position="Mid-market AI productivity tools for SMBs"
    )
    
    print(f"✅ Competitive analysis completed!")


def demo_networking(nanocorp: NanoCorp):
    """Demo: Create networking outreach"""
    print("\n" + "=" * 60)
    print("DEMO 8: Partnership Outreach")
    print("=" * 60)
    
    # Create partnership outreach
    result = nanocorp.network(
        "partnership",
        partner_type="Technology Partners",
        value_proposition="We help SaaS companies add AI capabilities to their products",
        collaboration_types=[
            "Integration partnerships",
            "Co-marketing campaigns",
            "Reseller agreements"
        ],
        outreach_targets=[
            "Slack",
            "Salesforce",
            "HubSpot",
            "Zendesk"
        ]
    )
    
    print(f"✅ Partnership outreach created!")
    print(f"   Type: {result.get('type', 'N/A')}")
    
    # Event networking plan
    result2 = nanocorp.network(
        "event",
        event_name="TechCrunch Disrupt 2024",
        event_type="Tech Conference",
        networking_goals=[
            "Find potential integration partners",
            "Connect with investors",
            "Meet potential enterprise customers",
            "Build industry relationships"
        ],
        target_contacts=[
            {
                "name": "Sarah Chen",
                "role": "VP of Partnerships",
                "company": "TechCorp",
                "expertise": "API integrations",
                "discussion_points": ["Partnership opportunities", "Technical requirements"]
            },
            {
                "name": "Mike Johnson",
                "role": "Angel Investor",
                "company": "Angel Ventures",
                "expertise": "SaaS investments",
                "discussion_points": ["Investment thesis alignment", "Next funding round"]
            }
        ]
    )
    
    print(f"✅ Event networking plan created!")


def demo_status_and_board(nanocorp: NanoCorp):
    """Demo: Check status and board"""
    print("\n" + "=" * 60)
    print("DEMO 9: Status and Board")
    print("=" * 60)
    
    # Get statistics
    stats = nanocorp.stats()
    print("📊 Task Statistics:")
    print(f"   Total tasks: {stats['total']}")
    print(f"   Completed: {stats['completed']}")
    print(f"   In progress: {stats['in_progress']}")
    print(f"   Pending: {stats['pending']}")
    print(f"   Failed: {stats['failed']}")
    print(f"   Completion rate: {stats['completion_rate']*100:.1f}%")
    
    # Get board view
    board = nanocorp.board()
    print("\n📋 Task Board:")
    for column, tasks in board.items():
        if tasks:
            print(f"   {column.title()}: {len(tasks)} tasks")
            for task in tasks[:3]:  # Show first 3
                print(f"      - {task['title']} ({task['priority']})")


def demo_full_workflow():
    """Demo: Full startup workflow"""
    print("\n" + "=" * 60)
    print("DEMO 10: Full Startup Workflow")
    print("=" * 60)
    
    # Check for API key
    api_key = os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
    
    # Quick start NanoCorp
    nanocorp = quick_start(
        company_name="Revolutionary AI Startup",
        mission="Disrupt the industry with AI-powered solutions",
        api_key=api_key,
        workspace_path="./nanocorp_full_demo"
    )
    
    print(f"🚀 Started: {nanocorp.ceo.company_context['name']}")
    
    # Create multiple tasks at once
    tasks = [
        ("Create landing page", nanocorp.create_website, {"name": "Product Alpha", "website_type": "landing"}),
        ("Marketing plan", nanocorp.create_marketing_campaign, {"name": "Product Launch", "channels": ["social", "email"]}),
        ("Social content", nanocorp.create_social_content, {"topic": "AI revolution", "platforms": ["twitter", "linkedin"]}),
        ("Business proposal", nanocorp.create_document, {"doc_type": "proposal", "client_name": "BigClient Inc", "project_name": "AI Integration"}),
        ("Market research", nanocorp.research, {"topic": "Enterprise AI market", "research_type": "market"}),
    ]
    
    print("\n📝 Creating multiple tasks...")
    for task_name, func, kwargs in tasks:
        try:
            result = func(**kwargs)
            print(f"   ✅ {task_name}")
        except Exception as e:
            print(f"   ❌ {task_name}: {e}")
    
    # Show final status
    stats = nanocorp.stats()
    print(f"\n📊 Final Statistics:")
    print(f"   Total created: {stats['total']}")
    print(f"   Completed: {stats['completed']}")
    
    # Save state
    nanocorp.save()
    print("\n💾 State saved to: ./nanocorp_full_demo/nanocorp_state.json")


def main():
    """Run all demos"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🤖 NanoCorp - Autonomous AI Startup System Demo            ║
║                                                               ║
║   Building the future of AI-powered business automation...    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Run individual demos
    nanocorp = demo_basic_setup()
    demo_website_creation(nanocorp)
    demo_marketing_campaign(nanocorp)
    demo_social_content(nanocorp)
    demo_email_campaign(nanocorp)
    demo_document_creation(nanocorp)
    demo_research(nanocorp)
    demo_networking(nanocorp)
    demo_status_and_board(nanocorp)
    
    # Run full workflow demo
    demo_full_workflow()
    
    print("\n" + "=" * 60)
    print("🎉 All demos completed!")
    print("=" * 60)
    print("""
Next Steps:
1. Set your LLM_API_KEY environment variable
2. Try running: python -i demo.py
3. Then use: nanocorp.chat("Help me launch a new product")
4. Explore the generated content in ./nanocorp_workspace/
    """)


if __name__ == "__main__":
    main()
