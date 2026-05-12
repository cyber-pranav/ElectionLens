# 🗳️ ElectionLens — Election Data Intelligence System

> **Built for Google Agentic Premier League Hackathon — GDG Build with AI**

## Problem Statement

Indian elections generate massive amounts of complex data — vote tallies, turnout figures, margin statistics — spread across thousands of constituencies. Citizens, journalists, and election monitors struggle to extract meaningful insights from this raw data, making it hard to understand electoral outcomes, spot irregularities, or compare performances across regions.

## Solution Overview

**ElectionLens** is a multi-agent AI system built with Google's Agent Development Kit (ADK) that transforms raw election data into simple, intuitive, real-time insights. Users can ask natural-language questions like *"Who won in Varanasi?"* and receive factual, citizen-friendly answers powered by 5 specialised AI agents working in orchestration. The system includes anomaly detection for flagging suspicious patterns, visual analytics through interactive charts, and an election jargon explainer for first-time voters.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      STREAMLIT FRONTEND                         │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────────────┐  │
│  │ Ask Chat │  │ Explore Tab  │  │  Alerts Feed              │  │
│  └────┬─────┘  └──────┬───────┘  └────────────┬──────────────┘  │
│       └───────────────┼───────────────────────┘                 │
└───────────────────────┼─────────────────────────────────────────┘
                        │ HTTP
┌───────────────────────┼─────────────────────────────────────────┐
│                   FASTAPI BACKEND                               │
│               POST /query  GET /alerts  GET /health             │
└───────────────────────┼─────────────────────────────────────────┘
                        │
┌───────────────────────┼─────────────────────────────────────────┐
│            ORCHESTRATOR AGENT (Root — ADK)                      │
│                       │                                         │
│    ┌──────────────────┼──────────────────────┐                  │
│    │                  │                      │                  │
│  ┌─┴──────────┐  ┌───┴──────────┐  ┌────────┴───────┐          │
│  │   Data     │  │  Analysis   │  │   Insight      │          │
│  │ Ingestion  │  │   Agent     │  │    Agent       │          │
│  │   Agent    │  │             │  │  (Gemini)      │          │
│  └────────────┘  └─────────────┘  └────────────────┘          │
│                                                                │
│  ┌──────────────┐  ┌───────────────────┐                       │
│  │ Monitoring   │  │  Visualization    │                       │
│  │   Agent      │  │     Agent         │                       │
│  └──────────────┘  └───────────────────┘                       │
└────────────────────────────────────────────────────────────────┘
                        │
              ┌─────────┴─────────┐
              │  SQLite Database  │
              │  (elections.db)   │
              └───────────────────┘
```

## Agent Descriptions

| Agent | Role | Key Tools |
|---|---|---|
| **OrchestratorAgent** | Routes user queries to the right sub-agent(s), aggregates responses | Sub-agent delegation via ADK |
| **DataIngestionAgent** | Fetches and normalises election data | `fetch_election_results`, `fetch_candidate_profile`, `fetch_voter_turnout` |
| **AnalysisAgent** | Quantitative analysis — vote shares, swings, rankings | `compute_vote_share`, `detect_swing`, `rank_candidates`, `trend_analysis` |
| **InsightAgent** | Plain-language summaries and jargon explanations via Gemini | `generate_summary`, `explain_election_term`, `compare_constituencies` |
| **MonitoringAgent** | Anomaly detection, close-contest flags, recount risks | `detect_anomaly`, `check_close_contest`, `track_recount_risk`, `run_full_scan` |
| **VisualizationAgent** | Chart-ready JSON for Plotly rendering | `build_bar_chart_data`, `build_pie_chart_data`, `build_turnout_chart_data` |

## Setup Instructions

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd electionlens

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 3. Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run ElectionLens
python run.py

# 6. Open the app
# Frontend: http://localhost:8501
# API:      http://localhost:8000
# Health:   http://localhost:8000/health
```

## Demo Queries

Try these queries in the **"Ask Anything"** tab:

1. **`"Who won in Varanasi in 2024 and by how much?"`**
2. **`"Which party had the highest vote share in Uttar Pradesh?"`**
3. **`"Show me constituencies with unusually high voter turnout"`**
4. **`"Compare the results in Varanasi and Mumbai North"`**
5. **`"What is NOTA and how many votes did it get?"`**

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check — lists all active agents |
| `/query` | POST | Natural language query processing |
| `/constituencies` | GET | List all loaded constituency names |
| `/parties` | GET | List all parties in dataset |
| `/states` | GET | List all states in dataset |
| `/alerts` | GET | Get all monitoring alerts |
| `/scan` | POST | Trigger full monitoring scan |

## Tech Stack

| Layer | Technology |
|---|---|
| Agent Framework | Google ADK (Python) — `google-adk` |
| AI Model | Gemini 2.0 Flash via `google-generativeai` |
| Backend API | FastAPI + Uvicorn |
| Frontend | Streamlit + Plotly |
| Database | SQLite via SQLAlchemy |
| Data | 21 real 2024 Lok Sabha constituencies (seed data) |

## Running Tests

```bash
cd electionlens
pytest tests/ -v
```

## Project Structure

```
electionlens/
├── agents/                    # ADK agent definitions
│   ├── orchestrator.py        # Root orchestrator with sub-agents
│   ├── data_ingestion.py      # Data fetch agent
│   ├── analysis.py            # Quantitative analysis agent
│   ├── insight.py             # Plain-language insight agent
│   ├── monitoring.py          # Anomaly detection agent
│   └── visualization.py       # Chart data generation agent
├── tools/                     # Shared tool functions
│   ├── database.py            # SQLite ORM + CRUD
│   ├── election_api.py        # Election data fetch helpers
│   └── gemini_tools.py        # Gemini generation wrappers
├── data/
│   └── sample_elections.json  # Seed: 21 real 2024 constituencies
├── frontend/
│   └── app.py                 # Streamlit single-page app
├── api/
│   └── main.py                # FastAPI server
├── tests/
│   ├── test_agents.py         # Agent integration tests
│   └── test_tools.py          # Tool function unit tests
├── .env.example
├── requirements.txt
├── run.py                     # Single entry point
└── README.md
```

## Hackathon Context

**Built for Google Agentic Premier League Hackathon — GDG Build with AI**

This project demonstrates:
- ✅ Multi-agent orchestration with Google ADK
- ✅ Gemini AI for natural language understanding and generation
- ✅ Real election data analysis and anomaly detection
- ✅ Citizen-friendly insights for democratic transparency
- ✅ Production-ready API with interactive frontend

---

*ElectionLens — Making election data accessible to every citizen.* 🇮🇳
