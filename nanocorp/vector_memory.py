"""
Vector Memory System for NanoCorp

Semantic search over all past experiences using embeddings.
Learns from every task, decision, and outcome.
"""
import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict
import math


class SimpleEmbedder:
    """
    Simple hash-based embedder that works without API calls.
    Uses semantic hashing for approximate similarity search.
    """
    
    def __init__(self, dim: int = 384):
        self.dim = dim
        self._vocab = self._build_vocab()
    
    def _build_vocab(self) -> Dict[str, int]:
        """Build vocabulary from common words"""
        words = """
        business startup company product service customer user market value 
        growth revenue profit cost strategy goal mission vision strategy
        marketing sales content website app technology software data analysis
        research development design user experience team management leadership
        communication presentation document report plan project task
        success failure learn improve optimize automate scale
        problem solution idea innovation creativity efficiency
        quality speed reliability security privacy trust
        brand reputation awareness engagement conversion retention
        """.split()
        return {w: i for i, w in enumerate(set(words))}
    
    def embed(self, text: str) -> List[float]:
        """Create a semantic hash vector from text"""
        words = text.lower().split()
        vector = [0.0] * self.dim
        
        for i, word in enumerate(words):
            if word in self._vocab:
                idx = self._vocab[word]
                # Spread influence across multiple dimensions
                for j in range(8):
                    vidx = (idx + i + j) % self.dim
                    vector[vidx] += 1.0 / (j + 1)
        
        # Normalize
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        
        return vector
    
    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        dot = sum(x * y for x, y in zip(a, b))
        return max(0, min(1, (dot + 1) / 2))  # Normalize to 0-1


class VectorMemory:
    """
    Semantic memory system with embedding-based search.
    
    Stores experiences, learns patterns, enables recall.
    """
    
    def __init__(self, storage_path: str = None, embedder: SimpleEmbedder = None):
        self.storage_path = Path(storage_path) if storage_path else Path("~/.nanocorp/memory.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.embedder = embedder or SimpleEmbedder()
        self.entries: List[Dict] = []
        self.vectors: Dict[str, List[float]] = {}
        
        self._load()
    
    def _load(self):
        """Load memory from disk"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path) as f:
                    data = json.load(f)
                    self.entries = data.get("entries", [])
                    self.vectors = {
                        k: v for k, v in data.get("vectors", {}).items()
                    }
            except:
                self.entries = []
                self.vectors = {}
    
    def _save(self):
        """Save memory to disk"""
        with open(self.storage_path, 'w') as f:
            json.dump({
                "entries": self.entries,
                "vectors": {k: v for k, v in self.vectors.items()}
            }, f, indent=2)
    
    def store(
        self,
        content: str,
        memory_type: str = "experience",  # experience, fact, pattern, strategy, lesson
        metadata: Dict = None,
        importance: float = 0.5  # 0-1
    ) -> str:
        """Store a memory with embedding"""
        entry_id = hashlib.md5(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        # Create embedding
        vector = self.embedder.embed(content)
        self.vectors[entry_id] = vector
        
        # Store entry
        entry = {
            "id": entry_id,
            "content": content,
            "type": memory_type,
            "metadata": metadata or {},
            "importance": importance,
            "created_at": datetime.now().isoformat(),
            "access_count": 0,
            "last_accessed": None
        }
        
        self.entries.append(entry)
        self._save()
        
        return entry_id
    
    def recall(
        self,
        query: str,
        memory_type: str = None,
        limit: int = 5,
        min_similarity: float = 0.3
    ) -> List[Dict]:
        """Recall memories similar to query"""
        query_vector = self.embedder.embed(query)
        
        results = []
        for entry in self.entries:
            if memory_type and entry["type"] != memory_type:
                continue
            
            entry_vector = self.vectors.get(entry["id"])
            if not entry_vector:
                continue
            
            similarity = self.embedder.cosine_similarity(query_vector, entry_vector)
            
            if similarity >= min_similarity:
                result = entry.copy()
                result["similarity"] = similarity
                results.append(result)
        
        # Sort by similarity and importance
        results.sort(key=lambda x: (x["similarity"] * 0.7 + x["importance"] * 0.3), reverse=True)
        
        # Update access counts
        for r in results[:limit]:
            for e in self.entries:
                if e["id"] == r["id"]:
                    e["access_count"] += 1
                    e["last_accessed"] = datetime.now().isoformat()
        
        return results[:limit]
    
    def learn_from(
        self,
        experience: str,
        outcome: str,  # "success", "failure", "mixed"
        context: Dict = None
    ):
        """Learn from an experience"""
        memory_type = "lesson"
        if outcome == "success":
            memory_type = "success_pattern"
        elif outcome == "failure":
            memory_type = "failure_pattern"
        
        metadata = {
            "outcome": outcome,
            "context": context or {}
        }
        
        self.store(
            content=f"{experience} [Outcome: {outcome}]",
            memory_type=memory_type,
            metadata=metadata,
            importance=0.8 if outcome == "success" else 0.9
        )
    
    def get_patterns(self) -> Dict[str, List[Dict]]:
        """Get all learned patterns"""
        patterns = defaultdict(list)
        
        for entry in self.entries:
            if entry["type"] in ["success_pattern", "failure_pattern", "pattern"]:
                patterns[entry["type"]].append(entry)
        
        return dict(patterns)
    
    def get_insights(self) -> List[str]:
        """Generate insights from patterns"""
        patterns = self.get_patterns()
        insights = []
        
        # Analyze success patterns
        success_count = len(patterns.get("success_pattern", []))
        failure_count = len(patterns.get("failure_pattern", []))
        
        if success_count > 0:
            insights.append(f"Learned {success_count} success patterns")
        if failure_count > 0:
            insights.append(f"Learned {failure_count} failure patterns")
        
        # Most accessed memories
        accessed = sorted(self.entries, key=lambda x: x.get("access_count", 0), reverse=True)
        if accessed:
            insights.append(f"Most referenced: {accessed[0]['content'][:50]}...")
        
        return insights
    
    def stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        by_type = defaultdict(int)
        for e in self.entries:
            by_type[e["type"]] += 1
        
        return {
            "total_entries": len(self.entries),
            "by_type": dict(by_type),
            "avg_importance": sum(e["importance"] for e in self.entries) / max(1, len(self.entries))
        }


class LearningEngine:
    """
    Self-improvement engine that learns from outcomes
    and optimizes worker behavior over time.
    """
    
    def __init__(self, memory: VectorMemory = None):
        self.memory = memory or VectorMemory()
        self.success_rates: Dict[str, float] = defaultdict(lambda: 0.5)
        self.attempt_counts: Dict[str, int] = defaultdict(int)
        self.prompt_templates: Dict[str, str] = {}
    
    def record_attempt(
        self,
        worker: str,
        task_type: str,
        success: bool,
        response: str = None
    ):
        """Record a task attempt for learning"""
        self.attempt_counts[f"{worker}:{task_type}"] += 1
        
        # Update success rate (exponential moving average)
        key = f"{worker}:{task_type}"
        old_rate = self.success_rates[key]
        count = self.attempt_counts[key]
        
        if success:
            self.success_rates[key] = old_rate + (1 - old_rate) / min(count, 10)
        else:
            self.success_rates[key] = old_rate - old_rate / min(count, 10)
        
        # Store in memory
        if success:
            self.memory.learn_from(
                f"{worker} completed {task_type} successfully",
                "success",
                {"response_length": len(response) if response else 0}
            )
        else:
            self.memory.learn_from(
                f"{worker} failed at {task_type}",
                "failure"
            )
    
    def get_worker_recommendation(self, worker: str, task_type: str) -> Dict:
        """Get recommendations for a worker/task combination"""
        key = f"{worker}:{task_type}"
        success_rate = self.success_rates[key]
        attempts = self.attempt_counts[key]
        
        # Find similar successful approaches
        similar = self.memory.recall(
            f"{worker} {task_type} success",
            memory_type="success_pattern",
            limit=3
        )
        
        return {
            "worker": worker,
            "task_type": task_type,
            "success_rate": round(success_rate, 2),
            "attempts": attempts,
            "confidence": "high" if attempts > 5 else "medium" if attempts > 2 else "low",
            "similar_successes": [s["content"] for s in similar]
        }
    
    def get_optimized_prompt(
        self,
        worker: str,
        task_type: str,
        base_prompt: str
    ) -> str:
        """Optimize a prompt based on learned patterns"""
        recommendations = self.get_worker_recommendation(worker, task_type)
        
        # Add learned insights
        if recommendations["confidence"] == "high" and recommendations["success_rate"] > 0.7:
            # High confidence - add success patterns
            patterns = recommendations["similar_successes"][:1]
            if patterns:
                return f"{base_prompt}\n\n[Learned: {patterns[0]}]"
        
        return base_prompt
    
    def auto_optimize(self) -> List[str]:
        """Run auto-optimization on all workers"""
        changes = []
        
        for key, rate in self.success_rates.items():
            if self.attempt_counts[key] < 3:
                continue
            
            worker, task_type = key.split(":", 1)
            
            if rate < 0.4 and self.attempt_counts[key] > 5:
                # Poor success rate - suggest intervention
                changes.append(
                    f"{worker} on {task_type}: Low success rate ({rate:.0%}). "
                    f"Consider retraining or different approach."
                )
            elif rate > 0.8 and self.attempt_counts[key] > 5:
                # Great success rate - document what works
                changes.append(
                    f"{worker} on {task_type}: High success rate ({rate:.0%}). "
                    f"Use this approach as best practice."
                )
        
        return changes
