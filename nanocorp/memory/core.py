"""
NanoCorp v3.0 - Unified Memory System

Real vector embeddings with ChromaDB for semantic search.
Consolidates episodic, semantic, and procedural memory.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import hashlib

from pydantic import BaseModel, Field

# Optional imports with fallbacks
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


# ===========================================
# MEMORY ENTRY
# ===========================================

class MemoryType(str):
    """Memory types."""
    EPISODIC = "episodic"      # Experiences and events
    SEMANTIC = "semantic"      # Facts and knowledge
    PROCEDURAL = "procedural"  # Skills and processes
    INSIGHT = "insight"        # Generated insights


@dataclass
class MemoryEntry:
    """A single memory entry."""
    id: str
    content: str
    memory_type: str = MemoryType.EPISODIC
    
    # Metadata
    importance: float = 0.5     # 0-1 importance
    access_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_accessed: Optional[str] = None
    
    # Semantic data
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Relationships
    tags: List[str] = field(default_factory=list)
    related_ids: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type,
            "importance": self.importance,
            "access_count": self.access_count,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "tags": self.tags,
            "related_ids": self.related_ids,
            "metadata": self.metadata
        }


# ===========================================
# EMBEDDINGS
# ===========================================

class Embedder:
    """
    Text embeddings using sentence-transformers or fallback.
    
    Provides semantic similarity search.
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        provider: str = "sentence-transformers"
    ):
        self.model_name = model_name
        self.provider = provider
        self._model = None
        self._embedding_cache: Dict[str, List[float]] = {}
    
    def load(self):
        """Load the embedding model."""
        if self.provider == "sentence-transformers" and SENTENCE_TRANSFORMERS_AVAILABLE:
            self._model = SentenceTransformer(self.model_name)
            return True
        return False
    
    def embed(self, text: str, use_cache: bool = True) -> List[float]:
        """
        Create embedding for text.
        
        Args:
            text: Text to embed
            use_cache: Use cached embeddings
        
        Returns:
            Embedding vector
        """
        # Check cache
        if use_cache and text in self._embedding_cache:
            return self._embedding_cache[text]
        
        # Use loaded model
        if self._model:
            embedding = self._model.encode(text).tolist()
            self._embedding_cache[text] = embedding
            return embedding
        
        # Fallback: simple hash-based (not semantic but works)
        return self._fallback_embed(text)
    
    def _fallback_embed(self, text: str) -> List[float]:
        """Fallback embedding using word frequencies."""
        words = text.lower().split()
        vector = [0.0] * 384  # Default dimension
        
        for i, word in enumerate(words[:384]):
            vector[i % 384] += hash(word) % 100 / 100.0
        
        # Normalize
        norm = sum(v * v for v in vector) ** 0.5
        if norm > 0:
            vector = [v / norm for v in vector]
        
        return vector
    
    @staticmethod
    def cosine_similarity(a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a * norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


# ===========================================
# VECTOR STORE
# ===========================================

class VectorStore:
    """
    Vector storage using ChromaDB or in-memory fallback.
    """
    
    def __init__(self, persist_dir: Optional[Path] = None):
        self.persist_dir = persist_dir
        self._client = None
        self._collection = None
    
    def initialize(self, collection_name: str = "nanocorp_memory"):
        """Initialize the vector store."""
        if CHROMADB_AVAILABLE:
            settings = ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
            
            if self.persist_dir:
                self.persist_dir.mkdir(parents=True, exist_ok=True)
                self._client = chromadb.PersistentClient(
                    path=str(self.persist_dir),
                    settings=settings
                )
            else:
                self._client = chromadb.Client(settings=settings)
            
            self._collection = self._client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "NanoCorp memory store"}
            )
            return True
        
        # In-memory fallback
        self._entries: Dict[str, Dict] = {}
        return False
    
    def add(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[Dict]] = None
    ):
        """Add entries to the store."""
        if self._collection:
            self._collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas or [{}] * len(ids)
            )
        else:
            # In-memory fallback
            for i, id in enumerate(ids):
                self._entries[id] = {
                    "embedding": embeddings[i],
                    "document": documents[i],
                    "metadata": metadatas[i] if metadatas else {}
                }
    
    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict:
        """Query the vector store."""
        if self._collection:
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where
            )
            return {
                "ids": results["ids"][0] if results["ids"] else [],
                "distances": results["distances"][0] if results.get("distances") else [],
                "documents": results["documents"][0] if results.get("documents") else [],
                "metadatas": results["metadatas"][0] if results.get("metadatas") else []
            }
        
        # In-memory fallback: simple similarity search
        results = []
        for id, entry in self._entries.items():
            sim = Embedder.cosine_similarity(query_embedding, entry["embedding"])
            results.append((id, sim, entry))
        
        results.sort(key=lambda x: x[1], reverse=True)
        results = results[:n_results]
        
        return {
            "ids": [r[0] for r in results],
            "distances": [1 - r[1] for r in results],
            "documents": [r[2]["document"] for r in results],
            "metadatas": [r[2]["metadata"] for r in results]
        }
    
    def delete(self, ids: List[str]):
        """Delete entries."""
        if self._collection:
            self._collection.delete(ids=ids)
        else:
            for id in ids:
                self._entries.pop(id, None)
    
    def reset(self):
        """Reset the store."""
        if self._collection:
            self._collection.delete(where={})
        else:
            self._entries.clear()


# ===========================================
# UNIFIED MEMORY
# ===========================================

class AgentMemory:
    """
    Unified memory system with semantic search.
    
    Combines episodic, semantic, and procedural memory
    with real vector embeddings.
    """
    
    def __init__(
        self,
        persist_dir: Optional[str] = None,
        embedding_model: str = "all-MiniLM-L6-v2",
        max_entries: int = 10000,
        similarity_threshold: float = 0.3
    ):
        # Storage paths
        self.persist_dir = Path(persist_dir) if persist_dir else Path("./.memory")
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.max_entries = max_entries
        self.similarity_threshold = similarity_threshold
        
        # Initialize components
        self.embedder = Embedder(model_name=embedding_model)
        self.embedder.load()
        
        self.store = VectorStore(persist_dir=self.persist_dir / "chromadb")
        self.store.initialize()
        
        # In-memory index for metadata
        self._index: Dict[str, MemoryEntry] = {}
        self._type_index: Dict[str, List[str]] = defaultdict(list)
        self._tag_index: Dict[str, List[str]] = defaultdict(list)
        
        # Load persisted index
        self._load_index()
    
    def _load_index(self):
        """Load memory index from disk."""
        index_file = self.persist_dir / "index.json"
        if index_file.exists():
            try:
                with open(index_file) as f:
                    data = json.load(f)
                    
                for entry_data in data.get("entries", []):
                    entry = MemoryEntry(**entry_data)
                    self._index[entry.id] = entry
                    self._type_index[entry.memory_type].append(entry.id)
                    for tag in entry.tags:
                        self._tag_index[tag].append(entry.id)
                    
                    # Add to vector store
                    if entry.embedding:
                        self.store.add(
                            ids=[entry.id],
                            embeddings=[entry.embedding],
                            documents=[entry.content],
                            metadatas=[entry.metadata]
                        )
            except Exception as e:
                print(f"Failed to load memory index: {e}")
    
    def _save_index(self):
        """Save memory index to disk."""
        index_file = self.persist_dir / "index.json"
        
        data = {
            "entries": [e.to_dict() for e in self._index.values()],
            "stats": self.stats()
        }
        
        with open(index_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def remember(
        self,
        content: str,
        memory_type: str = MemoryType.EPISODIC,
        importance: float = 0.5,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        related_to: Optional[List[str]] = None
    ) -> str:
        """
        Store a memory.
        
        Args:
            content: Memory content
            memory_type: Type of memory
            importance: Importance 0-1
            tags: Tags for organization
            metadata: Additional metadata
            related_to: Related memory IDs
        
        Returns:
            Memory ID
        """
        # Create ID
        mem_id = hashlib.md5(f"{content}{time.time()}".encode()).hexdigest()[:12]
        
        # Create embedding
        embedding = self.embedder.embed(content)
        
        # Create entry
        entry = MemoryEntry(
            id=mem_id,
            content=content,
            memory_type=memory_type,
            importance=importance,
            embedding=embedding,
            tags=tags or [],
            related_ids=related_to or [],
            metadata=metadata or {}
        )
        
        # Store
        self._index[mem_id] = entry
        self._type_index[memory_type].append(mem_id)
        for tag in entry.tags:
            self._tag_index[tag].append(mem_id)
        
        # Add to vector store
        self.store.add(
            ids=[mem_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[{
                "memory_type": memory_type,
                "importance": importance,
                "tags": ",".join(entry.tags)
            }]
        )
        
        # Enforce limit
        if len(self._index) > self.max_entries:
            self._prune_old_memories()
        
        # Persist
        self._save_index()
        
        return mem_id
    
    def recall(
        self,
        query: str,
        memory_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 5,
        min_similarity: float = None
    ) -> List[Tuple[MemoryEntry, float]]:
        """
        Recall memories similar to query.
        
        Args:
            query: Query text
            memory_type: Filter by type
            tags: Filter by tags
            limit: Max results
            min_similarity: Minimum similarity score
        
        Returns:
            List of (MemoryEntry, similarity) tuples
        """
        threshold = min_similarity or self.similarity_threshold
        
        # Query vector store
        query_embedding = self.embedder.embed(query)
        where = {"memory_type": memory_type} if memory_type else None
        
        results = self.store.query(
            query_embedding=query_embedding,
            n_results=limit * 2,  # Get more, filter later
            where=where
        )
        
        # Build results with similarity scores
        memories = []
        for i, mem_id in enumerate(results["ids"]):
            if mem_id not in self._index:
                continue
            
            entry = self._index[mem_id]
            similarity = 1 - results["distances"][i]  # Convert distance to similarity
            
            # Apply filters
            if similarity < threshold:
                continue
            
            if tags and not any(tag in entry.tags for tag in tags):
                continue
            
            memories.append((entry, similarity))
        
        # Sort by score and limit
        memories.sort(key=lambda x: (x[1], x[0].importance), reverse=True)
        memories = memories[:limit]
        
        # Update access counts
        for entry, _ in memories:
            entry.access_count += 1
            entry.last_accessed = datetime.now().isoformat()
        
        return memories
    
    def learn(
        self,
        experience: str,
        outcome: str,
        context: Optional[Dict] = None
    ):
        """
        Learn from an experience (success/failure).
        
        Automatically categorizes and tags.
        """
        mem_type = (
            MemoryType.INSIGHT 
            if outcome == "success" 
            else MemoryType.PROCEDURAL
        )
        
        metadata = {
            "outcome": outcome,
            "context": context or {}
        }
        
        self.remember(
            content=f"{experience} [Outcome: {outcome}]",
            memory_type=mem_type,
            importance=0.9,
            tags=["learned", outcome],
            metadata=metadata
        )
    
    def forget(self, memory_id: str) -> bool:
        """Forget a specific memory."""
        if memory_id not in self._index:
            return False
        
        entry = self._index[memory_id]
        
        # Remove from indices
        del self._index[memory_id]
        self._type_index[entry.memory_type].remove(memory_id)
        for tag in entry.tags:
            if memory_id in self._tag_index[tag]:
                self._tag_index[tag].remove(memory_id)
        
        # Remove from vector store
        self.store.delete([memory_id])
        
        self._save_index()
        return True
    
    def _prune_old_memories(self):
        """Remove low-importance old memories."""
        # Sort by importance and access count
        entries = sorted(
            self._index.values(),
            key=lambda e: (e.importance, e.access_count),
            reverse=True
        )
        
        # Remove lowest priority
        to_remove = entries[self.max_entries // 2:]
        for entry in to_remove:
            self.forget(entry.id)
    
    def get_insights(self) -> List[str]:
        """Generate insights from patterns."""
        insights = []
        
        # Count by type
        type_counts = {k: len(v) for k, v in self._type_index.items()}
        insights.append(f"Memory breakdown: {type_counts}")
        
        # Find frequently accessed
        accessed = sorted(
            self._index.values(),
            key=lambda e: e.access_count,
            reverse=True
        )
        if accessed:
            insights.append(f"Most accessed: {accessed[0].content[:50]}...")
        
        # Find patterns
        recent = sorted(
            self._index.values(),
            key=lambda e: e.created_at,
            reverse=True
        )[:10]
        
        return insights
    
    def stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "total_memories": len(self._index),
            "by_type": {k: len(v) for k, v in self._type_index.items()},
            "total_tags": len(self._tag_index),
            "avg_importance": sum(e.importance for e in self._index.values()) / max(1, len(self._index))
        }
    
    def reset(self):
        """Reset all memory."""
        self._index.clear()
        self._type_index.clear()
        self._tag_index.clear()
        self.store.reset()
        self._save_index()
