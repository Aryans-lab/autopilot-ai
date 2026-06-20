"""
Agent Memory - Persistent Learning and Knowledge System

NanoCorp's memory system allows agents to learn from experiences,
remember successful strategies, and improve over time.
"""
import json
import hashlib
import time
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
from pathlib import Path
import re


@dataclass
class MemoryEntry:
    """A single memory entry"""
    id: str
    content: str
    memory_type: str  # 'experience', 'strategy', 'lesson', 'fact', 'pattern'
    source: str  # 'execution', 'user', 'analysis', 'external'
    importance: float  # 0.0 to 1.0
    tags: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    success: Optional[bool] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    decay_score: float = 1.0  # For memory consolidation


@dataclass
class LearnedPattern:
    """A learned pattern or association"""
    pattern: str
    outcome: str
    frequency: int
    success_rate: float
    context: Dict[str, Any]
    first_seen: datetime
    last_seen: datetime


@dataclass
class Strategy:
    """A successful strategy or approach"""
    id: str
    name: str
    description: str
    conditions: List[str]  # When this strategy works
    actions: List[Dict[str, Any]]
    success_count: int
    failure_count: int
    success_rate: float
    avg_duration: float
    created_at: datetime
    last_used: datetime


@dataclass
class Insight:
    """A deep insight derived from patterns"""
    id: str
    content: str
    confidence: float
    evidence: List[str]
    implications: List[str]
    created_at: datetime
    validated: bool = False


class AgentMemory:
    """
    Agent Memory System for persistent learning
    
    Features:
    - Episodic memory: Experience recording
    - Semantic memory: Facts and knowledge
    - Procedural memory: Skills and strategies
    - Memory consolidation: Pattern detection
    - Contextual recall: Relevant memory retrieval
    """
    
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        max_entries: int = 10000,
        decay_rate: float = 0.01
    ):
        self.storage_path = storage_path
        
        # Memory stores
        self.episodic: Dict[str, MemoryEntry] = {}  # Experiences
        self.semantic: Dict[str, MemoryEntry] = {}    # Facts
        self.procedural: Dict[str, Strategy] = {}    # Strategies
        self.patterns: Dict[str, LearnedPattern] = {} # Patterns
        self.insights: Dict[str, Insight] = {}        # Insights
        
        # Indices for fast retrieval
        self._by_type: Dict[str, Set[str]] = defaultdict(set)
        self._by_tag: Dict[str, Set[str]] = defaultdict(set)
        self._by_source: Dict[str, Set[str]] = defaultdict(set)
        self._recent: deque = deque(maxlen=1000)
        
        # Configuration
        self.max_entries = max_entries
        self.decay_rate = decay_rate
        
        # Load existing memories
        if storage_path and storage_path.exists():
            self._load()
    
    # --- Memory Operations ---
    
    def remember(
        self,
        content: str,
        memory_type: str,
        source: str = "execution",
        importance: float = 0.5,
        tags: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        success: Optional[bool] = None
    ) -> MemoryEntry:
        """Store a new memory"""
        entry = MemoryEntry(
            id=f"mem_{int(time.time())}_{len(self.episodic) + len(self.semantic)}",
            content=content,
            memory_type=memory_type,
            source=source,
            importance=importance,
            tags=tags or [],
            context=context or {},
            success=success
        )
        
        # Store in appropriate memory
        if memory_type in ['experience', 'lesson']:
            self.episodic[entry.id] = entry
        else:
            self.semantic[entry.id] = entry
        
        # Update indices
        self._by_type[memory_type].add(entry.id)
        for tag in entry.tags:
            self._by_tag[tag].add(entry.id)
        self._by_source[source].add(entry.id)
        self._recent.append(entry.id)
        
        # Consolidate if needed
        if len(self.episodic) + len(self.semantic) > self.max_entries:
            self._consolidate()
        
        self._save()
        return entry
    
    def recall(
        self,
        query: str,
        memory_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10,
        recency_weight: float = 0.3,
        relevance_weight: float = 0.5,
        importance_weight: float = 0.2
    ) -> List[MemoryEntry]:
        """Recall relevant memories"""
        candidates = set()
        
        # Filter by type
        if memory_types:
            for mt in memory_types:
                candidates.update(self._by_type.get(mt, set()))
        else:
            candidates.update(self._by_type.get('experience', set()))
            candidates.update(self._by_type.get('lesson', set()))
            candidates.update(self._by_type.get('strategy', set()))
        
        # Filter by tags
        if tags:
            tagged = set()
            for tag in tags:
                tagged.update(self._by_tag.get(tag, set()))
            candidates.intersection_update(tagged)
        
        # Score candidates
        scored = []
        query_hash = hashlib.md5(query.lower().encode()).hexdigest()
        
        for mem_id in candidates:
            entry = self.episodic.get(mem_id) or self.semantic.get(mem_id)
            if not entry:
                continue
            
            # Relevance: keyword overlap
            query_words = set(query.lower().split())
            content_words = set(entry.content.lower().split())
            relevance = len(query_words & content_words) / max(len(query_words), 1)
            
            # Recency
            age = (datetime.now() - entry.last_accessed).total_seconds()
            recency = max(0, 1 - age / (86400 * 7))  # Decay over a week
            
            # Importance
            importance = entry.importance * entry.decay_score
            
            # Combined score
            score = (
                relevance * relevance_weight +
                recency * recency_weight +
                importance * importance_weight
            )
            
            scored.append((score, entry))
        
        # Sort and return top results
        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored[:limit]]
    
    def add_learning(
        self,
        lessons: List[str],
        context: Optional[Dict[str, Any]] = None
    ):
        """Add lessons learned from experiences"""
        success = context.get("success", True) if context else True
        
        for lesson in lessons:
            self.remember(
                content=lesson,
                memory_type="lesson",
                source="execution",
                importance=0.7 if success else 0.9,
                context=context,
                success=success
            )
    
    # --- Strategy Management ---
    
    def learn_strategy(
        self,
        name: str,
        description: str,
        conditions: List[str],
        actions: List[Dict[str, Any]],
        success: bool,
        duration: float = 0.0
    ):
        """Learn a new strategy or update existing one"""
        # Check if strategy exists
        existing = None
        for sid, strat in self.procedural.items():
            if strat.name == name:
                existing = strat
                break
        
        if existing:
            # Update existing strategy
            if success:
                existing.success_count += 1
            else:
                existing.failure_count += 1
            existing.success_rate = existing.success_count / (
                existing.success_count + existing.failure_count
            )
            existing.avg_duration = (
                (existing.avg_duration * (existing.success_count + existing.failure_count - 1) + duration) /
                (existing.success_count + existing.failure_count)
            )
            existing.last_used = datetime.now()
        else:
            # Create new strategy
            strategy = Strategy(
                id=f"strat_{int(time.time())}_{len(self.procedural)}",
                name=name,
                description=description,
                conditions=conditions,
                actions=actions,
                success_count=1 if success else 0,
                failure_count=0 if success else 1,
                success_rate=1.0 if success else 0.0,
                avg_duration=duration,
                created_at=datetime.now(),
                last_used=datetime.now()
            )
            self.procedural[strategy.id] = strategy
        
        self._save()
    
    def get_best_strategy(
        self,
        context: Dict[str, Any],
        min_success_rate: float = 0.5
    ) -> Optional[Strategy]:
        """Get the best strategy for current context"""
        candidates = []
        
        for strategy in self.procedural.values():
            if strategy.success_rate < min_success_rate:
                continue
            
            # Check if conditions match
            context_str = json.dumps(context).lower()
            matches = sum(1 for cond in strategy.conditions if cond.lower() in context_str)
            
            if matches > 0:
                candidates.append((matches * strategy.success_rate, strategy))
        
        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            return candidates[0][1]
        
        return None
    
    # --- Pattern Detection ---
    
    def detect_pattern(
        self,
        antecedent: str,
        consequent: str,
        context: Dict[str, Any],
        success: bool
    ):
        """Detect and record patterns"""
        pattern_key = f"{antecedent} -> {consequent}"
        
        if pattern_key in self.patterns:
            pattern = self.patterns[pattern_key]
            pattern.frequency += 1
            pattern.last_seen = datetime.now()
            
            # Update success rate
            if success:
                old_total = pattern.frequency - 1
                pattern.success_rate = (pattern.success_rate * old_total + 1) / pattern.frequency
        else:
            self.patterns[pattern_key] = LearnedPattern(
                pattern=pattern_key,
                outcome=consequent,
                frequency=1,
                success_rate=1.0 if success else 0.0,
                context=context,
                first_seen=datetime.now(),
                last_seen=datetime.now()
            )
        
        # Generate insight if pattern is strong
        pattern = self.patterns[pattern_key]
        if pattern.frequency >= 5 and pattern.success_rate >= 0.8:
            self._generate_insight(pattern)
        
        self._save()
    
    def _generate_insight(self, pattern: LearnedPattern):
        """Generate insight from strong pattern"""
        # Check if we already have this insight
        insight_key = hashlib.md5(pattern.pattern.encode()).hexdigest()
        
        if insight_key in self.insights:
            return
        
        insight = Insight(
            id=f"insight_{int(time.time())}_{len(self.insights)}",
            content=f"Pattern detected: {pattern.pattern} with {pattern.success_rate:.0%} success rate",
            confidence=min(1.0, pattern.frequency / 10 + pattern.success_rate),
            evidence=[f"Seen {pattern.frequency} times"],
            implications=["Apply this pattern in similar contexts", "Monitor for variations"],
            created_at=datetime.now(),
            validated=False
        )
        
        self.insights[insight.id] = insight
    
    # --- Memory Consolidation ---
    
    def _consolidate(self):
        """Consolidate memories, removing weak ones"""
        all_memories = list(self.episodic.values()) + list(self.semantic.values())
        
        # Calculate retention scores
        for mem in all_memories:
            age = (datetime.now() - mem.created_at).total_seconds()
            mem.decay_score = max(0.1, 1 - age * self.decay_rate / 86400)
        
        # Sort by retention score
        all_memories.sort(
            key=lambda m: m.importance * m.decay_score * (1 + m.access_count * 0.1)
        )
        
        # Remove bottom 20%
        to_remove = len(all_memories) // 5
        for mem in all_memories[:to_remove]:
            if mem.id in self.episodic:
                del self.episodic[mem.id]
            elif mem.id in self.semantic:
                del self.semantic[mem.id]
    
    # --- Persistence ---
    
    def _save(self):
        """Save memories to disk"""
        if not self.storage_path:
            return
        
        data = {
            "episodic": {k: asdict(v) for k, v in self.episodic.items()},
            "semantic": {k: asdict(v) for k, v in self.semantic.items()},
            "procedural": {k: asdict(v) for k, v in self.procedural.items()},
            "patterns": {k: asdict(v) for k, v in self.patterns.items()},
            "insights": {k: asdict(v) for k, v in self.insights.items()},
            "saved_at": datetime.now().isoformat()
        }
        
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _load(self):
        """Load memories from disk"""
        if not self.storage_path or not self.storage_path.exists():
            return
        
        with open(self.storage_path, 'r') as f:
            data = json.load(f)
        
        # Restore memories
        for k, v in data.get("episodic", {}).items():
            self.episodic[k] = MemoryEntry(**v)
        for k, v in data.get("semantic", {}).items():
            self.semantic[k] = MemoryEntry(**v)
        for k, v in data.get("procedural", {}).items():
            self.procedural[k] = Strategy(**v)
        for k, v in data.get("patterns", {}).items():
            self.patterns[k] = LearnedPattern(**v)
        for k, v in data.get("insights", {}).items():
            self.insights[k] = Insight(**v)
        
        # Rebuild indices
        for mem_id, mem in {**self.episodic, **self.semantic}.items():
            self._by_type[mem.memory_type].add(mem_id)
            for tag in mem.tags:
                self._by_tag[tag].add(mem_id)
            self._by_source[mem.source].add(mem_id)
    
    # --- Query Interface ---
    
    def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search memories with filters"""
        memories = self.recall(query, limit=20)
        
        results = []
        for mem in memories:
            if filters:
                if "memory_type" in filters and mem.memory_type != filters["memory_type"]:
                    continue
                if "min_importance" in filters and mem.importance < filters["min_importance"]:
                    continue
                if "source" in filters and mem.source != filters["source"]:
                    continue
            
            results.append({
                "id": mem.id,
                "content": mem.content,
                "type": mem.memory_type,
                "importance": mem.importance,
                "tags": mem.tags,
                "success": mem.success,
                "created_at": mem.created_at.isoformat()
            })
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics"""
        all_memories = list(self.episodic.values()) + list(self.semantic.values())
        
        return {
            "total_memories": len(all_memories),
            "episodic": len(self.episodic),
            "semantic": len(self.semantic),
            "strategies": len(self.procedural),
            "patterns": len(self.patterns),
            "insights": len(self.insights),
            "avg_importance": sum(m.importance for m in all_memories) / max(len(all_memories), 1),
            "avg_success_rate": sum(
                s.success_rate for s in self.procedural.values()
            ) / max(len(self.procedural), 1) if self.procedural else 0.0
        }
