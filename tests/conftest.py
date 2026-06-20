"""Pytest configuration and fixtures."""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def sample_memory():
    from nanocorp.memory import AgentMemory
    mem = AgentMemory(persist_dir="./.test_memory")
    yield mem
    import shutil
    shutil.rmtree("./.test_memory", ignore_errors=True)

@pytest.fixture
def sample_agent_manager():
    from nanocorp.agents import AgentManager
    return AgentManager()
