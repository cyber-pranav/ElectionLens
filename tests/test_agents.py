"""
Tests for ElectionLens agents (integration-level).
These test that agents can be instantiated and their tool functions work.
Requires google-adk to be installed — skipped automatically if unavailable.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.database import init_db

# Skip all tests in this module if google-adk is not installed
pytestmark = pytest.mark.skipif(
    not __import__("importlib").util.find_spec("google.adk"),
    reason="google-adk not installed — agent instantiation tests skipped",
)


@pytest.fixture(autouse=True)
def setup_db():
    """Ensure DB is initialized before every test."""
    init_db()


class TestAgentInstantiation:
    """Verify all agents can be imported and have the expected attributes."""

    def test_data_ingestion_agent(self):
        from agents.data_ingestion import data_ingestion_agent
        assert data_ingestion_agent.name == "data_ingestion_agent"
        assert len(data_ingestion_agent.tools) >= 3

    def test_analysis_agent(self):
        from agents.analysis import analysis_agent
        assert analysis_agent.name == "analysis_agent"
        assert len(analysis_agent.tools) >= 4

    def test_insight_agent(self):
        from agents.insight import insight_agent
        assert insight_agent.name == "insight_agent"
        assert len(insight_agent.tools) >= 3

    def test_monitoring_agent(self):
        from agents.monitoring import monitoring_agent
        assert monitoring_agent.name == "monitoring_agent"
        assert len(monitoring_agent.tools) >= 4

    def test_visualization_agent(self):
        from agents.visualization import visualization_agent
        assert visualization_agent.name == "visualization_agent"
        assert len(visualization_agent.tools) >= 4

    def test_orchestrator_agent(self):
        from agents.orchestrator import orchestrator_agent
        assert orchestrator_agent.name == "electionlens_orchestrator"
        assert len(orchestrator_agent.sub_agents) == 5


class TestOrchestratorSetup:
    """Test orchestrator initialization."""

    def test_initialize_runs_without_error(self):
        from agents.orchestrator import initialize
        initialize()  # Should not raise

    def test_monitoring_scan_produces_alerts(self):
        from agents.orchestrator import initialize
        from tools.database import get_all_alerts
        initialize()
        alerts = get_all_alerts()
        assert len(alerts) >= 1, "Monitoring scan should produce at least 1 alert from seed data"
