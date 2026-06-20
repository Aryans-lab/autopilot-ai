"""Unit tests for agents."""
import pytest
from nanocorp.agents import AgentManager, CEOAgent

def test_create_workforce(sample_agent_manager):
    ceo = sample_agent_manager.create_workforce("TestCorp", "Test mission")
    assert ceo is not None
    assert ceo.company_name == "TestCorp"

def test_ceo_add_goal():
    ceo = CEOAgent(name="Test CEO")
    goal_id = ceo.add_goal("Build product", priority="high")
    assert goal_id is not None
    assert len(ceo.goals) == 1
