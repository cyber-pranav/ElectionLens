"""
ElectionLens — FastAPI backend.
Exposes /query, /constituencies, /parties, /alerts, /health endpoints.
"""

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure project root is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

load_dotenv()

from agents.orchestrator import initialize, query_agent
from tools.database import (
    get_all_constituencies,
    get_all_parties,
    get_all_states,
    get_all_alerts,
)
from agents.monitoring import run_full_scan


# ---------------------------------------------------------------------------
# Lifespan — init DB + monitoring scan on startup
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize()
    yield


app = FastAPI(
    title="ElectionLens API",
    description="Election Data Intelligence System — powered by Google ADK + Gemini",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    query: str
    session_id: str = "default"


class QueryResponse(BaseModel):
    answer: str
    data: dict = {}
    alerts: list = []
    agent_trace: list[str] = []


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "ElectionLens API",
        "agents": [
            "electionlens_orchestrator",
            "data_ingestion_agent",
            "analysis_agent",
            "insight_agent",
            "monitoring_agent",
            "visualization_agent",
        ],
    }


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Process a natural-language election query through the agent pipeline."""
    result = await query_agent(request.query, request.session_id)
    alerts = get_all_alerts()
    return QueryResponse(
        answer=result["answer"],
        data={"agent_trace_details": result.get("raw_events", [])},
        alerts=alerts,
        agent_trace=result["agent_trace"],
    )


@app.get("/constituencies")
async def constituencies(year: int = 2024):
    """Return all loaded constituency names."""
    rows = get_all_constituencies(year)
    return {
        "year": year,
        "count": len(rows),
        "constituencies": [{"name": r["name"], "state": r["state"]} for r in rows],
    }


@app.get("/parties")
async def parties(year: int = 2024):
    """Return all parties in the dataset."""
    party_list = get_all_parties(year)
    return {"year": year, "count": len(party_list), "parties": party_list}


@app.get("/states")
async def states(year: int = 2024):
    """Return all states in the dataset."""
    state_list = get_all_states(year)
    return {"year": year, "count": len(state_list), "states": state_list}


@app.get("/alerts")
async def alerts(year: int = 2024):
    """Return all MonitoringAgent flags."""
    alert_list = get_all_alerts()
    return {"year": year, "total": len(alert_list), "alerts": alert_list}


@app.post("/scan")
async def trigger_scan(year: int = 2024):
    """Manually trigger a full monitoring scan."""
    result = run_full_scan(year)
    return result
