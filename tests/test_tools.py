"""
Tests for ElectionLens agent tools.
"""

import json
import os
import sys
import pytest

# Ensure project root is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.database import init_db, get_all_constituencies, get_constituency, get_all_parties, get_all_states


@pytest.fixture(autouse=True)
def setup_db():
    """Ensure DB is initialized before every test."""
    init_db()


class TestDatabase:
    """Tests for database.py CRUD operations."""

    def test_init_db_creates_data(self):
        rows = get_all_constituencies()
        assert len(rows) >= 20, f"Expected >= 20 constituencies, got {len(rows)}"

    def test_get_constituency_varanasi(self):
        row = get_constituency("Varanasi")
        assert row is not None
        assert row["winner"] == "Narendra Modi"
        assert row["party"] == "BJP"
        assert row["year"] == 2024

    def test_get_constituency_case_insensitive(self):
        row = get_constituency("varanasi")
        assert row is not None
        assert row["name"] == "Varanasi"

    def test_get_constituency_not_found(self):
        row = get_constituency("Nonexistent Place")
        assert row is None

    def test_get_all_parties(self):
        parties = get_all_parties()
        assert "BJP" in parties
        assert "INC" in parties
        assert len(parties) >= 3

    def test_get_all_states(self):
        states = get_all_states()
        assert "Uttar Pradesh" in states
        assert len(states) >= 5


class TestElectionAPI:
    """Tests for election_api.py tool functions."""

    def test_fetch_election_results(self):
        from tools.election_api import fetch_election_results
        result = fetch_election_results("Uttar Pradesh")
        assert result["state"] == "Uttar Pradesh"
        assert result["count"] >= 3

    def test_fetch_candidate_profile(self):
        from tools.election_api import fetch_candidate_profile
        result = fetch_candidate_profile("Modi")
        assert "results" in result
        assert len(result["results"]) >= 1
        assert result["results"][0]["candidate"] == "Narendra Modi"

    def test_fetch_voter_turnout(self):
        from tools.election_api import fetch_voter_turnout
        result = fetch_voter_turnout("Varanasi")
        assert result["constituency"] == "Varanasi"
        assert result["turnout_percent"] == 54.8

    def test_fetch_voter_turnout_not_found(self):
        from tools.election_api import fetch_voter_turnout
        result = fetch_voter_turnout("Atlantis")
        assert "error" in result

    def test_list_all_constituencies(self):
        from tools.election_api import list_all_constituencies
        result = list_all_constituencies()
        assert result["count"] >= 20
        assert "Varanasi" in result["constituencies"]

    def test_list_all_parties(self):
        from tools.election_api import list_all_parties
        result = list_all_parties()
        assert "BJP" in result["parties"]


class TestMonitoringTools:
    """Tests for monitoring agent tool functions."""

    def test_detect_anomaly_finds_high_turnout(self):
        from agents.monitoring import detect_anomaly
        result = detect_anomaly()
        assert result["anomalies_found"] >= 1
        # Wayanad has 73.6% turnout — should be flagged
        names = [a["constituency"] for a in result["anomalies"]]
        assert "Wayanad" in names

    def test_check_close_contest(self):
        from agents.monitoring import check_close_contest
        result = check_close_contest()
        assert result["close_contests_found"] >= 1
        names = [c["constituency"] for c in result["close_contests"]]
        # Amritsar has margin of 6,333 — very close
        assert "Amritsar" in names

    def test_track_recount_risk(self):
        from agents.monitoring import track_recount_risk
        result = track_recount_risk()
        assert result["risks_found"] >= 1
        names = [r["constituency"] for r in result["risks"]]
        assert "Amritsar" in names

    def test_run_full_scan(self):
        from agents.monitoring import run_full_scan
        result = run_full_scan()
        assert result["total_alerts"] >= 2


class TestAnalysisTools:
    """Tests for analysis agent tool functions."""

    def test_compute_vote_share(self):
        from agents.analysis import compute_vote_share
        result = compute_vote_share("BJP")
        assert result["party"] == "BJP"
        assert result["vote_share_percent"] > 0
        assert result["seats_won"] >= 1

    def test_rank_candidates(self):
        from agents.analysis import rank_candidates
        result = rank_candidates("Varanasi")
        assert result["winner"] == "Narendra Modi"
        assert result["winner_party"] == "BJP"
        assert result["margin"] == 152513

    def test_rank_candidates_not_found(self):
        from agents.analysis import rank_candidates
        result = rank_candidates("Nowhere")
        assert "error" in result

    def test_trend_analysis(self):
        from agents.analysis import trend_analysis
        result = trend_analysis("BJP")
        assert result["seats_won"] >= 1
        assert "Varanasi" in result["constituencies_won"]


class TestVisualizationTools:
    """Tests for visualization agent tool functions."""

    def test_build_pie_chart(self):
        from agents.visualization import build_pie_chart_data
        result = build_pie_chart_data("Varanasi")
        assert result["chart_type"] == "pie"
        assert len(result["labels"]) >= 2
        assert len(result["values"]) >= 2

    def test_build_bar_chart(self):
        from agents.visualization import build_bar_chart_data
        result = build_bar_chart_data(constituency="Varanasi")
        assert result["chart_type"] == "bar"
        assert len(result["labels"]) >= 2

    def test_build_turnout_chart(self):
        from agents.visualization import build_turnout_chart_data
        result = build_turnout_chart_data()
        assert result["chart_type"] == "bar"
        assert len(result["labels"]) >= 20

    def test_build_seats_chart(self):
        from agents.visualization import build_seats_chart_data
        result = build_seats_chart_data()
        assert result["chart_type"] == "bar"
        assert "BJP" in result["labels"]
