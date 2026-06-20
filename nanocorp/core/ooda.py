"""
OODA Loop Engine - Observe-Orient-Decide-Act Decision Making System

The OODA loop is a decision-making process that enables rapid, effective responses
to changing conditions. NanoCorp uses this for strategic decision making.
"""
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import deque


class OODAPhase(str, Enum):
    """OODA Loop phases"""
    OBSERVE = "observe"
    ORIENT = "orient" 
    DECIDE = "decide"
    ACT = "act"
    ASSESS = "assess"


class ThreatLevel(str, Enum):
    """Threat/opportunity assessment levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


@dataclass
class SensorData:
    """Data collected from sensors/environment"""
    source: str
    data_type: str
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0


@dataclass
class SituationalAssessment:
    """Current situation assessment"""
    phase: OODAPhase
    observations: List[Dict[str, Any]]
    analysis: Dict[str, Any]
    threats: List[Dict[str, Any]]
    opportunities: List[Dict[str, Any]]
    recommendations: List[str]
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Decision:
    """A decision made during the OODA loop"""
    id: str
    phase: OODAPhase
    situation_summary: str
    options: List[Dict[str, Any]]
    selected_option: Dict[str, Any]
    rationale: str
    risk_level: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Action:
    """An action to be executed"""
    id: str
    decision_id: str
    action_type: str
    parameters: Dict[str, Any]
    priority: int = 5
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Outcome:
    """Result of an action"""
    action_id: str
    success: bool
    output: Any
    duration: float
    lessons: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class OODALoop:
    """
    OODA Loop Engine for rapid decision making
    
    The loop continuously:
    - OBSERVE: Gather data from environment
    - ORIENT: Analyze and understand situation
    - DECIDE: Select best course of action
    - ACT: Execute the decision
    - ASSESS: Evaluate results and iterate
    """
    
    def __init__(
        self,
        llm: Any = None,
        memory: Any = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.llm = llm
        self.memory = memory
        self.config = config or {}
        self.loop_id = str(uuid.uuid4())[:8]
        
        # State tracking
        self.current_phase = OODAPhase.OBSERVE
        self.loop_count = 0
        self.last_loop_time: Optional[datetime] = None
        
        # Data stores
        self.sensor_data: deque = deque(maxlen=1000)
        self.situations: List[SituationalAssessment] = []
        self.decisions: List[Decision] = []
        self.actions: List[Action] = []
        self.outcomes: List[Outcome] = []
        
        # Performance metrics
        self.metrics = {
            "total_loops": 0,
            "decisions_made": 0,
            "actions_executed": 0,
            "success_rate": 0.0,
            "threats_identified": 0,
            "opportunities_identified": 0
        }
        
        # Configuration
        self.confidence_threshold = self.config.get("confidence_threshold", 0.6)
    
    def observe(self, context: Dict[str, Any]) -> List[SensorData]:
        """OBSERVE: Gather data from all sources"""
        observations = []
        
        # Task status
        if "task_status" in context:
            observations.append(SensorData(
                source="task_manager",
                data_type="task_status",
                content=context["task_status"],
                confidence=0.95
            ))
        
        # Worker status
        if "worker_status" in context:
            observations.append(SensorData(
                source="worker_pool",
                data_type="worker_status",
                content=context["worker_status"],
                confidence=0.9
            ))
        
        # Market data
        if "market_data" in context:
            observations.append(SensorData(
                source="market",
                data_type="market_intelligence",
                content=context["market_data"],
                confidence=0.8
            ))
        
        # User feedback
        if "user_feedback" in context:
            observations.append(SensorData(
                source="user",
                data_type="feedback",
                content=context["user_feedback"],
                confidence=0.95
            ))
        
        # Results
        if "results" in context:
            observations.append(SensorData(
                source="execution",
                data_type="outcome",
                content=context["results"],
                confidence=0.9
            ))
        
        for obs in observations:
            self.sensor_data.append(obs)
        
        self.metrics["total_loops"] += 1
        return observations
    
    def orient(self, observations: List[SensorData]) -> SituationalAssessment:
        """ORIENT: Analyze data and understand situation"""
        self.current_phase = OODAPhase.ORIENT
        
        # Analyze
        analysis = self._analyze_observations(observations)
        threats = self._identify_threats(analysis, observations)
        opportunities = self._identify_opportunities(analysis, observations)
        recommendations = self._generate_recommendations(threats, opportunities)
        confidence = self._calculate_confidence(observations)
        
        assessment = SituationalAssessment(
            phase=OODAPhase.ORIENT,
            observations=[{"source": o.source, "type": o.data_type} for o in observations],
            analysis=analysis,
            threats=threats,
            opportunities=opportunities,
            recommendations=recommendations,
            confidence=confidence
        )
        
        self.situations.append(assessment)
        self.metrics["threats_identified"] += len(threats)
        self.metrics["opportunities_identified"] += len(opportunities)
        
        return assessment
    
    def decide(
        self,
        situation: SituationalAssessment,
        available_actions: Optional[List[Dict[str, Any]]] = None
    ) -> Decision:
        """DECIDE: Select best course of action"""
        self.current_phase = OODAPhase.DECIDE
        
        # Generate options
        if available_actions is None:
            options = self._generate_options(situation)
        else:
            options = available_actions
        
        # Score options
        scored_options = []
        for option in options:
            score = self._score_option(option, situation)
            scored_options.append({**option, "score": score})
        
        scored_options.sort(key=lambda x: x["score"], reverse=True)
        
        # Select best
        best_option = scored_options[0] if scored_options else {
            "action": "continue_operations",
            "parameters": {},
            "rationale": "No urgent action required"
        }
        
        decision = Decision(
            id=f"dec_{int(time.time())}_{len(self.decisions)}",
            phase=OODAPhase.DECIDE,
            situation_summary=f"{len(situation.threats)} threats, {len(situation.opportunities)} opportunities",
            options=scored_options[:5],  # Top 5 options
            selected_option=best_option,
            rationale=best_option.get("rationale", "Best scored option"),
            risk_level=self._assess_risk_level(best_option)
        )
        
        self.decisions.append(decision)
        self.metrics["decisions_made"] += 1
        
        return decision
    
    def act(
        self,
        decision: Decision,
        executor: Optional[Callable] = None
    ) -> List[Action]:
        """ACT: Execute decided actions"""
        self.current_phase = OODAPhase.ACT
        
        actions = []
        action = Action(
            id=f"act_{int(time.time())}_{len(self.actions)}",
            decision_id=decision.id,
            action_type=decision.selected_option.get("action", "unknown"),
            parameters=decision.selected_option.get("parameters", {}),
            priority=decision.selected_option.get("priority", 5)
        )
        
        actions.append(action)
        self.actions.append(action)
        
        if executor and action.status == "pending":
            try:
                action.status = "in_progress"
                result = executor(action)
                action.result = result
                action.status = "completed"
            except Exception as e:
                action.status = f"failed: {str(e)}"
                action.result = {"error": str(e)}
        
        self.metrics["actions_executed"] += 1
        return actions
    
    def assess(self, actions: List[Action], context: Dict[str, Any]) -> List[Outcome]:
        """ASSESS: Evaluate outcomes"""
        self.current_phase = OODAPhase.ASSESS
        
        outcomes = []
        for action in actions:
            success = action.status == "completed"
            lessons = self._extract_lessons(action, context)
            
            outcome = Outcome(
                action_id=action.id,
                success=success,
                output=action.result,
                duration=0.0,
                lessons=lessons
            )
            outcomes.append(outcome)
            self.outcomes.append(outcome)
        
        # Update success rate
        if self.outcomes:
            successes = sum(1 for o in self.outcomes if o.success)
            self.metrics["success_rate"] = successes / len(self.outcomes)
        
        return outcomes
    
    def run_cycle(
        self,
        context: Dict[str, Any],
        executor: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Run complete OODA cycle"""
        start_time = time.time()
        self.loop_count += 1
        
        observations = self.observe(context)
        situation = self.orient(observations)
        
        if situation.confidence >= self.confidence_threshold:
            decision = self.decide(situation)
            actions = self.act(decision, executor)
            outcomes = self.assess(actions, context)
        else:
            decision = None
            actions = []
            outcomes = []
        
        self.last_loop_time = datetime.now()
        
        return {
            "loop_id": self.loop_id,
            "loop_count": self.loop_count,
            "phase": self.current_phase.value,
            "observations_collected": len(observations),
            "confidence": situation.confidence,
            "threats": len(situation.threats),
            "opportunities": len(situation.opportunities),
            "decision": decision.selected_option.get("action") if decision else None,
            "actions_executed": len(actions),
            "success_rate": self.metrics["success_rate"]
        }
    
    # --- Helper Methods ---
    
    def _analyze_observations(self, observations: List[SensorData]) -> Dict[str, Any]:
        """Analyze collected observations"""
        return {
            "patterns": ["backlog_observed" if any("pending" in str(o.content) for o in observations) else None],
            "trends": [],
            "anomalies": ["failures_detected" if any("failed" in str(o.content) for o in observations) else None],
            "correlations": []
        }
    
    def _identify_threats(self, analysis: Dict, observations: List[SensorData]) -> List[Dict]:
        """Identify threats"""
        threats = []
        if "failures_detected" in analysis.get("anomalies", []):
            threats.append({
                "type": "execution_failure",
                "level": ThreatLevel.MEDIUM.value,
                "description": "Task execution failures detected"
            })
        return threats
    
    def _identify_opportunities(self, analysis: Dict, observations: List[SensorData]) -> List[Dict]:
        """Identify opportunities"""
        opportunities = []
        if "backlog_observed" in analysis.get("patterns", []):
            opportunities.append({
                "type": "parallel_execution",
                "level": ThreatLevel.HIGH.value,
                "description": "Opportunity for parallel task execution"
            })
        return opportunities
    
    def _generate_recommendations(self, threats: List, opportunities: List) -> List[str]:
        """Generate recommendations"""
        recs = []
        for t in threats:
            if t.get("level") in [ThreatLevel.CRITICAL.value, ThreatLevel.HIGH.value]:
                recs.append(f"URGENT: Address {t['type']}")
        for o in opportunities:
            if o.get("level") in [ThreatLevel.HIGH.value, ThreatLevel.MEDIUM.value]:
                recs.append(f"ACTION: {o['description']}")
        return recs or ["Continue current operations"]
    
    def _calculate_confidence(self, observations: List[SensorData]) -> float:
        """Calculate confidence"""
        if not observations:
            return 0.0
        return min(1.0, sum(o.confidence for o in observations) / len(observations) + 0.1)
    
    def _generate_options(self, situation: SituationalAssessment) -> List[Dict]:
        """Generate decision options"""
        options = []
        if situation.threats:
            options.append({
                "action": "mitigate_threats",
                "parameters": {"threats": situation.threats},
                "priority": 1,
                "rationale": "Address identified threats"
            })
        if situation.opportunities:
            options.append({
                "action": "seize_opportunity",
                "parameters": {"opportunities": situation.opportunities},
                "priority": 2,
                "rationale": "Capitalize on opportunities"
            })
        options.append({
            "action": "continue_operations",
            "parameters": {},
            "priority": 10,
            "rationale": "No urgent action required"
        })
        return options
    
    def _score_option(self, option: Dict, situation: SituationalAssessment) -> float:
        """Score an option"""
        score = (10 - option.get("priority", 5)) * 10
        if option["action"] == "mitigate_threats":
            score += len(situation.threats) * 20
        if option["action"] == "seize_opportunity":
            score += len(situation.opportunities) * 15
        return score
    
    def _assess_risk_level(self, option: Dict) -> str:
        """Assess risk level"""
        priority = option.get("priority", 5)
        if priority <= 2:
            return "high"
        elif priority <= 5:
            return "medium"
        return "low"
    
    def _extract_lessons(self, action: Action, context: Dict) -> List[str]:
        """Extract lessons"""
        if action.status == "completed":
            return [f"{action.action_type} succeeded"]
        elif "failed" in action.status:
            return [f"{action.action_type} failed: {action.status}"]
        return []
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get OODA loop metrics"""
        return {
            **self.metrics,
            "current_phase": self.current_phase.value,
            "loop_count": self.loop_count,
            "decisions": len(self.decisions),
            "actions": len(self.actions)
        }
