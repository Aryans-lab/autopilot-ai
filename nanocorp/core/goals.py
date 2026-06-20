"""
Autonomous Goal System - Self-Directed AI Operations

NanoCorp can now set goals, create sub-goals, and autonomously work
towards achieving them with minimal human intervention.
"""
import json
import uuid
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import deque


class GoalStatus(str, Enum):
    """Goal status"""
    ACTIVE = "active"
    PURSUING = "pursuing"
    BLOCKED = "blocked"
    ACHIEVED = "achieved"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class GoalPriority(str, Enum):
    """Goal priority"""
    CRITICAL = "critical"  # Must achieve
    HIGH = "high"          # Should achieve
    MEDIUM = "medium"      # Want to achieve
    LOW = "low"           # Nice to have
    EXPLORATORY = "exploratory"  # Learn more about this


class GoalAlignment(str, Enum):
    """Goal alignment with company mission"""
    CORE = "core"          # Core to mission
    SUPPORTING = "supporting"  # Supports core goals
    ENABLING = "enabling"   # Enables other goals
    ADJACENT = "adjacent"    # Related but not critical


@dataclass
class Milestone:
    """A milestone within a goal"""
    id: str
    name: str
    description: str
    target_date: Optional[datetime] = None
    completed: bool = False
    completed_at: Optional[datetime] = None
    progress: float = 0.0  # 0.0 to 1.0


@dataclass
class Metric:
    """A metric to track goal progress"""
    name: str
    current_value: float
    target_value: float
    unit: str = ""
    trend: str = "stable"  # improving, declining, stable


@dataclass
class Goal:
    """An autonomous goal"""
    id: str
    title: str
    description: str
    
    # Hierarchy
    parent_id: Optional[str] = None
    sub_goals: List[str] = field(default_factory=list)
    
    # Classification
    priority: GoalPriority = GoalPriority.MEDIUM
    alignment: GoalAlignment = GoalAlignment.SUPPORTING
    
    # Status tracking
    status: GoalStatus = GoalStatus.ACTIVE
    progress: float = 0.0  # 0.0 to 1.0
    
    # Planning
    milestones: List[Milestone] = field(default_factory=list)
    metrics: List[Metric] = field(default_factory=list)
    
    # Execution
    tasks: List[str] = field(default_factory=list)  # Task IDs
    strategies: List[Dict[str, Any]] = field(default_factory=list)
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    target_date: Optional[datetime] = None
    achieved_at: Optional[datetime] = None
    
    # Results
    outcome: Optional[str] = None
    learnings: List[str] = field(default_factory=list)
    resources_used: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['priority'] = self.priority.value
        data['alignment'] = self.alignment.value
        data['status'] = self.status.value
        return data


class GoalTree:
    """
    Goal Tree - Hierarchical goal management
    
    Goals are organized in a tree structure:
    - Vision/Mission (top)
    - Strategic Goals
    - Tactical Goals
    - Operational Goals (bottom)
    """
    
    def __init__(self):
        self.goals: Dict[str, Goal] = {}
        self.root_goals: List[str] = []  # Top-level goals
    
    def add_goal(
        self,
        title: str,
        description: str = "",
        parent_id: Optional[str] = None,
        priority: GoalPriority = GoalPriority.MEDIUM,
        alignment: GoalAlignment = GoalAlignment.SUPPORTING,
        context: Optional[Dict[str, Any]] = None
    ) -> Goal:
        """Add a new goal"""
        goal_id = f"goal_{int(time.time())}_{len(self.goals)}"
        
        goal = Goal(
            id=goal_id,
            title=title,
            description=description,
            parent_id=parent_id,
            priority=priority,
            alignment=alignment,
            context=context or {}
        )
        
        self.goals[goal_id] = goal
        
        # Update parent or root
        if parent_id and parent_id in self.goals:
            self.goals[parent_id].sub_goals.append(goal_id)
        else:
            self.root_goals.append(goal_id)
        
        return goal
    
    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """Get a goal by ID"""
        return self.goals.get(goal_id)
    
    def get_sub_goals(self, goal_id: str) -> List[Goal]:
        """Get all sub-goals recursively"""
        goal = self.goals.get(goal_id)
        if not goal:
            return []
        
        sub_goals = []
        for sub_id in goal.sub_goals:
            sub_goal = self.goals.get(sub_id)
            if sub_goal:
                sub_goals.append(sub_goal)
                sub_goals.extend(self.get_sub_goals(sub_id))
        
        return sub_goals
    
    def calculate_progress(self, goal_id: str) -> float:
        """Calculate progress including sub-goals"""
        goal = self.goals.get(goal_id)
        if not goal:
            return 0.0
        
        if not goal.sub_goals:
            return goal.progress
        
        # Aggregate sub-goal progress
        sub_progress = []
        for sub_id in goal.sub_goals:
            sub_goal = self.goals.get(sub_id)
            if sub_goal:
                sub_progress.append(self.calculate_progress(sub_id))
        
        if not sub_progress:
            return goal.progress
        
        return sum(sub_progress) / len(sub_progress)
    
    def update_status(self, goal_id: str, status: GoalStatus):
        """Update goal status"""
        goal = self.goals.get(goal_id)
        if goal:
            goal.status = status
            goal.updated_at = datetime.now()
            
            if status == GoalStatus.PURSUING and not goal.started_at:
                goal.started_at = datetime.now()
            elif status == GoalStatus.ACHIEVED:
                goal.achieved_at = datetime.now()
    
    def add_milestone(
        self,
        goal_id: str,
        name: str,
        description: str = "",
        target_date: Optional[datetime] = None
    ) -> Optional[Milestone]:
        """Add a milestone to a goal"""
        goal = self.goals.get(goal_id)
        if not goal:
            return None
        
        milestone = Milestone(
            id=f"ms_{int(time.time())}_{len(goal.milestones)}",
            name=name,
            description=description,
            target_date=target_date
        )
        
        goal.milestones.append(milestone)
        goal.updated_at = datetime.now()
        
        return milestone
    
    def update_metric(
        self,
        goal_id: str,
        metric_name: str,
        value: float
    ) -> bool:
        """Update a metric value"""
        goal = self.goals.get(goal_id)
        if not goal:
            return False
        
        for metric in goal.metrics:
            if metric.name == metric_name:
                old_value = metric.current_value
                metric.current_value = value
                
                # Update trend
                if value > old_value:
                    metric.trend = "improving"
                elif value < old_value:
                    metric.trend = "declining"
                
                return True
        
        return False
    
    def add_learning(self, goal_id: str, learning: str):
        """Add a learning to a goal"""
        goal = self.goals.get(goal_id)
        if goal:
            goal.learnings.append(learning)
            goal.updated_at = datetime.now()
    
    def get_prioritized_goals(self) -> List[Goal]:
        """Get all active goals sorted by priority"""
        priority_order = {
            GoalPriority.CRITICAL: 0,
            GoalPriority.HIGH: 1,
            GoalPriority.MEDIUM: 2,
            GoalPriority.LOW: 3,
            GoalPriority.EXPLORATORY: 4
        }
        
        active_goals = [
            g for g in self.goals.values()
            if g.status in [GoalStatus.ACTIVE, GoalStatus.PURSUING]
        ]
        
        return sorted(active_goals, key=lambda g: priority_order.get(g.priority, 5))


class AutonomousGoalEngine:
    """
    Autonomous Goal Engine
    
    Drives NanoCorp towards goals without constant human input.
    Uses OODA loops and memory to pursue goals effectively.
    """
    
    def __init__(
        self,
        goal_tree: Optional[GoalTree] = None,
        ooda_loop: Any = None,
        memory: Any = None
    ):
        self.goal_tree = goal_tree or GoalTree()
        self.ooda = ooda_loop
        self.memory = memory
        
        # Execution state
        self.current_goal_id: Optional[str] = None
        self.current_strategy: Optional[Dict[str, Any]] = None
        self.execution_history: List[Dict[str, Any]] = []
        
        # Configuration
        self.max_parallel_goals = 3
        self.replan_interval = 300  # seconds
        self.last_replan = datetime.now()
    
    def set_goal(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        target_date: Optional[datetime] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Goal:
        """Set a new goal"""
        goal = self.goal_tree.add_goal(
            title=title,
            description=description,
            priority=GoalPriority(priority),
            context=context
        )
        
        if target_date:
            goal.target_date = target_date
        
        # Initialize metrics if context provided
        if context:
            for metric_name, metric_data in context.get("metrics", {}).items():
                goal.metrics.append(Metric(
                    name=metric_name,
                    current_value=metric_data.get("current", 0),
                    target_value=metric_data.get("target", 100),
                    unit=metric_data.get("unit", "")
                ))
        
        return goal
    
    def decompose_goal(
        self,
        goal_id: str,
        sub_goal_titles: List[str]
    ) -> List[Goal]:
        """Decompose a goal into sub-goals"""
        parent = self.goal_tree.get_goal(goal_id)
        if not parent:
            return []
        
        sub_goals = []
        for title in sub_goal_titles:
            sub_goal = self.goal_tree.add_goal(
                title=title,
                description=f"Sub-goal of: {parent.title}",
                parent_id=goal_id,
                priority=parent.priority,
                alignment=parent.alignment
            )
            sub_goals.append(sub_goal)
        
        return sub_goals
    
    def create_milestones(
        self,
        goal_id: str,
        milestones: List[Dict[str, str]]
    ) -> List[Milestone]:
        """Create milestones for a goal"""
        created = []
        
        for ms_data in milestones:
            milestone = self.goal_tree.add_milestone(
                goal_id=goal_id,
                name=ms_data["name"],
                description=ms_data.get("description", ""),
                target_date=ms_data.get("target_date")
            )
            if milestone:
                created.append(milestone)
        
        return created
    
    def pursue_goal(
        self,
        goal_id: str,
        executor: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Pursue a specific goal"""
        goal = self.goal_tree.get_goal(goal_id)
        if not goal:
            return {"error": "Goal not found"}
        
        self.current_goal_id = goal_id
        self.goal_tree.update_status(goal_id, GoalStatus.PURSUING)
        
        # Get or create strategy
        if self.memory:
            strategy = self.memory.get_best_strategy(goal.context)
            if strategy:
                self.current_strategy = {
                    "name": strategy.name,
                    "actions": strategy.actions
                }
        
        # Create tasks from strategy
        tasks = self._create_tasks_from_goal(goal)
        
        # Execute tasks
        results = []
        for task in tasks:
            if executor:
                result = executor(task)
                results.append(result)
                
                # Update progress
                goal.progress = len([r for r in results if r.get("success")]) / len(tasks)
                goal.updated_at = datetime.now()
        
        # Check if goal achieved
        if goal.progress >= 1.0:
            self.goal_tree.update_status(goal_id, GoalStatus.ACHIEVED)
            if self.memory:
                self.memory.learn_strategy(
                    name=f"Goal: {goal.title}",
                    description=goal.description,
                    conditions=list(goal.context.keys()),
                    actions=tasks,
                    success=True
                )
        
        return {
            "goal_id": goal_id,
            "progress": goal.progress,
            "status": goal.status.value,
            "tasks_executed": len(results)
        }
    
    def _create_tasks_from_goal(self, goal: Goal) -> List[Dict[str, Any]]:
        """Create tasks from goal context"""
        tasks = []
        
        # Generate tasks based on goal type/context
        goal_type = goal.context.get("type", "general")
        
        if goal_type == "website":
            tasks = [
                {"title": "Create landing page", "worker": "WebDev", "priority": 1},
                {"title": "Set up hosting", "worker": "WebDev", "priority": 2},
                {"title": "Create marketing materials", "worker": "Marketing", "priority": 3}
            ]
        elif goal_type == "marketing":
            tasks = [
                {"title": "Create marketing plan", "worker": "Marketing", "priority": 1},
                {"title": "Create social content", "worker": "SocialMedia", "priority": 2},
                {"title": "Set up email campaign", "worker": "Email", "priority": 3}
            ]
        elif goal_type == "research":
            tasks = [
                {"title": "Conduct market research", "worker": "Researcher", "priority": 1},
                {"title": "Analyze competitors", "worker": "Researcher", "priority": 2},
                {"title": "Document findings", "worker": "Document", "priority": 3}
            ]
        else:
            tasks = [{"title": f"Work on: {goal.title}", "worker": "CEO", "priority": 1}]
        
        return tasks
    
    def run_autonomous_cycle(self, executor: Optional[Callable] = None) -> Dict[str, Any]:
        """Run autonomous goal pursuit cycle"""
        # Check if replanning needed
        time_since_replan = (datetime.now() - self.last_replan).total_seconds()
        
        if time_since_replan >= self.replan_interval:
            self._replan()
            self.last_replan = datetime.now()
        
        # Get prioritized goals
        goals = self.goal_tree.get_prioritized_goals()
        
        # Pursue top goals
        results = []
        for goal in goals[:self.max_parallel_goals]:
            if goal.status == GoalStatus.ACTIVE:
                result = self.pursue_goal(goal.id, executor)
                results.append(result)
        
        # Run OODA if available
        ooda_result = None
        if self.ooda:
            context = {
                "goal_progress": {g.id: g.progress for g in goals},
                "active_goals": len([g for g in goals if g.status == GoalStatus.PURSUING])
            }
            ooda_result = self.ooda.run_cycle(context, executor)
        
        return {
            "goals_pursued": len(results),
            "total_progress": sum(g.progress for g in goals) / max(len(goals), 1),
            "ooda": ooda_result
        }
    
    def _replan(self):
        """Replan goal strategies"""
        for goal in self.goal_tree.goals.values():
            if goal.status == GoalStatus.PURSUING:
                # Check if blocked
                if self._is_goal_blocked(goal):
                    self.goal_tree.update_status(goal.id, GoalStatus.BLOCKED)
                else:
                    # Generate new strategy
                    self._generate_strategy(goal)
    
    def _is_goal_blocked(self, goal: Goal) -> bool:
        """Check if a goal is blocked"""
        # Check dependencies
        for task_id in goal.tasks:
            if task_id.startswith("blocked:"):
                return True
        
        # Check time constraints
        if goal.target_date:
            if datetime.now() > goal.target_date and goal.progress < 0.5:
                return True
        
        return False
    
    def _generate_strategy(self, goal: Goal):
        """Generate a strategy for a goal"""
        # Simple strategy generation based on goal type
        goal_type = goal.context.get("type", "general")
        
        if goal_type == "website":
            strategy = {
                "name": f"Website strategy for {goal.title}",
                "steps": [
                    {"action": "create_landing_page", "order": 1},
                    {"action": "test_website", "order": 2},
                    {"action": "deploy", "order": 3},
                    {"action": "monitor", "order": 4}
                ]
            }
        elif goal_type == "marketing":
            strategy = {
                "name": f"Marketing strategy for {goal.title}",
                "steps": [
                    {"action": "create_content", "order": 1},
                    {"action": "launch_campaign", "order": 2},
                    {"action": "track_metrics", "order": 3}
                ]
            }
        else:
            strategy = {
                "name": f"Default strategy for {goal.title}",
                "steps": [
                    {"action": "analyze", "order": 1},
                    {"action": "plan", "order": 2},
                    {"action": "execute", "order": 3}
                ]
            }
        
        goal.strategies.append(strategy)
        goal.updated_at = datetime.now()
    
    def get_goal_tree_view(self) -> Dict[str, Any]:
        """Get hierarchical view of goals"""
        view = {"roots": []}
        
        for root_id in self.goal_tree.root_goals:
            root = self.goal_tree.get_goal(root_id)
            if root:
                view["roots"].append(self._goal_to_view(root))
        
        return view
    
    def _goal_to_view(self, goal: Goal) -> Dict[str, Any]:
        """Convert goal to view format"""
        sub_goals_view = []
        for sub_id in goal.sub_goals:
            sub = self.goal_tree.get_goal(sub_id)
            if sub:
                sub_goals_view.append(self._goal_to_view(sub))
        
        return {
            "id": goal.id,
            "title": goal.title,
            "status": goal.status.value,
            "progress": goal.progress,
            "priority": goal.priority.value,
            "milestones": [
                {"name": m.name, "completed": m.completed}
                for m in goal.milestones
            ],
            "sub_goals": sub_goals_view
        }
