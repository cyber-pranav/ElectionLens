"""
ElectionLens — AnalysisAgent.
Performs quantitative analysis on ingested election data.
"""

from google.adk.agents import Agent

from tools.analysis_tools import (
    compute_vote_share,
    detect_swing,
    rank_candidates,
    trend_analysis,
    party_performance_by_state,
)


# ---------------------------------------------------------------------------
# Agent definition
# ---------------------------------------------------------------------------

INSTRUCTION = """\
You are the **AnalysisAgent** of ElectionLens.

Your job is to perform quantitative analysis on election data.
You can compute vote shares, detect swings, rank candidates, analyse trends,
and break down party performance by state.

When asked an analytical question:
1. Identify the right tool to call.
2. Return the structured result with numbers, percentages, and deltas.
3. Do NOT generate prose — leave plain-language explanations to the InsightAgent.
"""

analysis_agent = Agent(
    name="analysis_agent",
    model="gemini-2.0-flash",
    instruction=INSTRUCTION,
    description=(
        "Performs quantitative election analysis: vote shares, swings, "
        "candidate rankings, party trends, and state-level breakdowns."
    ),
    tools=[
        compute_vote_share,
        detect_swing,
        rank_candidates,
        trend_analysis,
        party_performance_by_state,
    ],
)
