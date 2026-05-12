"""
ElectionLens — OrchestratorAgent (Root Agent).
Receives user queries, routes to specialist sub-agents, aggregates responses.
"""

import asyncio
import json
import os
from typing import Optional

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from tools.database import init_db
from agents.data_ingestion import data_ingestion_agent
from agents.analysis import analysis_agent
from agents.insight import insight_agent
from agents.monitoring import monitoring_agent
from agents.visualization import visualization_agent


# ---------------------------------------------------------------------------
# Root orchestrator — delegates to sub-agents automatically via ADK
# ---------------------------------------------------------------------------

INSTRUCTION = """\
You are **ElectionLens**, an AI-powered election intelligence assistant for India.
You help citizens, journalists, and election monitors understand election data
through simple, clear, factual answers.

You coordinate a team of specialist agents:

1. **data_ingestion_agent** — Fetches raw election data (results by state,
   candidate profiles, voter turnout, constituency lists, party lists).
   Route here when the user wants to look up raw data.

2. **analysis_agent** — Performs quantitative analysis: vote shares, swings,
   candidate rankings, party trends, state-level breakdowns.
   Route here for analytical questions about numbers and comparisons.

3. **insight_agent** — Converts raw data into plain-language summaries,
   explains election jargon, and compares constituencies narratively.
   Route here to make answers citizen-friendly. Also route jargon questions
   (e.g. "What is NOTA?") directly here.

4. **monitoring_agent** — Detects anomalies (turnout spikes/drops), close
   contests (margin < 2%), and recount risks. Route here for alert-related
   questions or when asked about irregularities.

5. **visualization_agent** — Generates chart-ready JSON for bar charts, pie
   charts, turnout comparisons, seat counts, and margin charts.
   Route here when the user asks to "show", "chart", or "visualize" something.

Workflow rules:
- For factual questions ("Who won Varanasi?"): data_ingestion → analysis → insight.
- For anomaly/alert questions: monitoring_agent.
- For chart requests: visualization_agent.
- For jargon explanations: insight_agent directly.
- For comparisons: analysis_agent → insight_agent.
- Always provide a final plain-language answer. Include specific numbers.
- Be factual — never speculate or editorialize.
- When presenting data, format numbers with commas for readability.
"""

# Build the root agent with sub-agents for automatic delegation
orchestrator_agent = Agent(
    name="electionlens_orchestrator",
    model="gemini-2.0-flash",
    instruction=INSTRUCTION,
    description="Root orchestrator for ElectionLens election intelligence system.",
    sub_agents=[
        data_ingestion_agent,
        analysis_agent,
        insight_agent,
        monitoring_agent,
        visualization_agent,
    ],
)


# ---------------------------------------------------------------------------
# Runner wrapper for the API layer
# ---------------------------------------------------------------------------

APP_NAME = "electionlens"
_session_service = InMemorySessionService()
_runner = Runner(
    agent=orchestrator_agent,
    app_name=APP_NAME,
    session_service=_session_service,
)


async def ensure_session(session_id: str, user_id: str = "user") -> None:
    """Create session if it doesn't already exist."""
    try:
        await _session_service.get_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id,
        )
    except Exception:
        await _session_service.create_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id,
        )


async def query_agent(query: str, session_id: str = "default",
                       user_id: str = "user") -> dict:
    """Send a natural-language query through the orchestrator and return the result.

    Returns:
        {
            "answer": str,
            "agent_trace": list[str],
            "raw_events": list[dict],
        }
    """
    await ensure_session(session_id, user_id)

    content = types.Content(
        role="user",
        parts=[types.Part(text=query)],
    )

    answer_parts: list[str] = []
    agent_trace: list[str] = []
    raw_events: list[dict] = []

    async for event in _runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        # Track which agents participated
        if hasattr(event, "author") and event.author:
            if event.author not in agent_trace:
                agent_trace.append(event.author)

        # Capture final text response
        if event.is_final_response():
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        answer_parts.append(part.text)

        # Stash a minimal event record
        raw_events.append({
            "author": getattr(event, "author", None),
            "is_final": event.is_final_response(),
        })

    return {
        "answer": "\n".join(answer_parts) if answer_parts else "I couldn't find an answer. Please rephrase your question.",
        "agent_trace": agent_trace,
        "raw_events": raw_events,
    }


def initialize() -> None:
    """Initialize the database and run startup monitoring scan."""
    init_db()
    # Run monitoring scan on startup so alerts are pre-populated
    from agents.monitoring import run_full_scan
    run_full_scan(2024)
