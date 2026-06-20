"""Unit tests for memory."""
import pytest
from nanocorp.memory import AgentMemory, MemoryType

def test_remember_recall(sample_memory):
    mem_id = sample_memory.remember("NanoCorp is awesome", memory_type=MemoryType.SEMANTIC)
    assert mem_id is not None
    results = sample_memory.recall("NanoCorp", limit=5)
    assert len(results) >= 1

def test_memory_stats(sample_memory):
    sample_memory.remember("Test 1")
    sample_memory.remember("Test 2")
    stats = sample_memory.stats()
    assert stats["total_memories"] >= 2
