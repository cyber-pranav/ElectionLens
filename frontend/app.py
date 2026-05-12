"""
ElectionLens — Streamlit Frontend.
Single-page app with 3 tabs: Ask Anything, Explore, Alerts.
"""

import json
import os
import sys
import time
from pathlib import Path

import plotly.graph_objects as go
import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

API_BASE = os.getenv("ELECTIONLENS_API", "http://localhost:8000")
st.set_page_config(
    page_title="ElectionLens — Election Intelligence",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS for premium look
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }

    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif;
    }

    .hero-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        color: white;
        text-align: center;
    }

    .hero-header h1 {
        color: white;
        font-size: 2rem;
        margin: 0;
        font-weight: 700;
    }

    .hero-header p {
        color: rgba(255,255,255,0.85);
        font-size: 1rem;
        margin: 0.3rem 0 0 0;
    }

    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid rgba(0,0,0,0.06);
    }

    .metric-card h3 {
        font-size: 2rem;
        margin: 0;
        color: #1a1a2e;
    }

    .metric-card p {
        color: #666;
        margin: 0.2rem 0 0 0;
        font-size: 0.85rem;
    }

    .alert-critical {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.8rem;
    }

    .alert-warning {
        background: linear-gradient(135deg, #f9ca24 0%, #f0932b 100%);
        color: #333;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.8rem;
    }

    .alert-info {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.8rem;
    }

    .agent-trace {
        background: #1a1a2e;
        color: #a8e6cf;
        padding: 0.8rem 1rem;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }

    .demo-btn {
        margin: 0.2rem;
    }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }

    div[data-testid="stSidebar"] .stMarkdown {
        color: #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def api_call(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """Make an API call to the FastAPI backend."""
    try:
        url = f"{API_BASE}{endpoint}"
        if method == "POST":
            resp = requests.post(url, json=data, timeout=120)
        else:
            resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to ElectionLens API. Make sure the backend is running on port 8000."}
    except Exception as e:
        return {"error": str(e)}


def render_plotly_chart(chart_data: dict):
    """Render a Plotly chart from chart-ready JSON."""
    if "error" in chart_data:
        st.error(chart_data["error"])
        return

    chart_type = chart_data.get("chart_type", "bar")
    labels = chart_data.get("labels", [])
    values = chart_data.get("values", [])
    colors = chart_data.get("colors", [])
    title = chart_data.get("title", "")

    if chart_type == "pie":
        fig = go.Figure(data=[go.Pie(
            labels=labels, values=values,
            marker_colors=colors,
            hole=0.4,
            textinfo="label+percent",
            textfont_size=12,
        )])
    else:
        fig = go.Figure(data=[go.Bar(
            x=labels, y=values,
            marker_color=colors,
            text=[f"{v:,}" for v in values],
            textposition="auto",
        )])

    fig.update_layout(
        title=dict(text=title, font=dict(size=16, family="Inter")),
        template="plotly_white",
        height=420,
        margin=dict(l=40, r=40, t=60, b=80),
        font=dict(family="Inter"),
        xaxis=dict(tickangle=-45) if chart_type != "pie" else {},
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### 🗳️ ElectionLens")
    st.markdown("---")

    st.markdown("**Model**")
    model_choice = st.selectbox(
        "Gemini Model",
        ["gemini-2.0-flash", "gemini-1.5-pro"],
        label_visibility="collapsed",
    )

    st.markdown("**Dataset**")
    st.success("✅ 2024 Lok Sabha (loaded)")

    st.markdown("---")
    st.markdown("**Agent Status**")

    agents = [
        ("🟢", "Orchestrator"),
        ("🟢", "Data Ingestion"),
        ("🟢", "Analysis"),
        ("🟢", "Insight"),
        ("🟢", "Monitoring"),
        ("🟢", "Visualization"),
    ]
    for icon, name in agents:
        st.markdown(f"{icon} {name}")

    st.markdown("---")
    st.markdown(
        "<small>Built for Google Agentic Premier League Hackathon — GDG Build with AI</small>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown("""
<div class="hero-header">
    <h1>🗳️ ElectionLens</h1>
    <p>Election Intelligence, Simplified — Powered by Google ADK + Gemini</p>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab1, tab2, tab3 = st.tabs(["💬 Ask Anything", "📊 Explore", "🚨 Alerts"])

# ----- Tab 1: Ask Anything -------------------------------------------------
with tab1:
    st.markdown("### Ask any question about Indian elections")

    # Demo query buttons
    st.markdown("**Quick demos for judges:**")
    demo_queries = [
        "Who won in Varanasi in 2024 and by how much?",
        "Which party had the highest vote share in Uttar Pradesh?",
        "Show me constituencies with unusually high voter turnout",
        "Compare the results in Varanasi and Mumbai North",
        "What is NOTA and how many votes did it get?",
    ]

    cols = st.columns(len(demo_queries))
    selected_demo = None
    for i, q in enumerate(demo_queries):
        short_label = q[:40] + "…" if len(q) > 40 else q
        if cols[i % len(cols)].button(short_label, key=f"demo_{i}", use_container_width=True):
            selected_demo = q

    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("trace"):
                with st.expander("🔍 Agent Trace"):
                    st.markdown(
                        '<div class="agent-trace">' +
                        " → ".join(msg["trace"]) +
                        '</div>',
                        unsafe_allow_html=True,
                    )

    # Process input
    user_input = st.chat_input("Ask about elections...")
    query_to_process = selected_demo or user_input

    if query_to_process:
        st.session_state.messages.append({"role": "user", "content": query_to_process})
        with st.chat_message("user"):
            st.markdown(query_to_process)

        with st.chat_message("assistant"):
            with st.spinner("🔄 Agents working..."):
                result = api_call("/query", "POST", {
                    "query": query_to_process,
                    "session_id": "streamlit_session",
                })

            if "error" in result:
                st.error(result["error"])
                answer = result["error"]
                trace = []
            else:
                answer = result.get("answer", "No answer received.")
                trace = result.get("agent_trace", [])
                st.markdown(answer)

                if trace:
                    with st.expander("🔍 Agent Trace"):
                        st.markdown(
                            '<div class="agent-trace">' +
                            " → ".join(trace) +
                            '</div>',
                            unsafe_allow_html=True,
                        )

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "trace": trace,
        })

# ----- Tab 2: Explore -------------------------------------------------------
with tab2:
    st.markdown("### Constituency Deep Dive")

    # Load constituencies
    const_data = api_call("/constituencies")
    if "error" not in const_data:
        const_names = [c["name"] for c in const_data.get("constituencies", [])]
    else:
        const_names = []
        st.warning("Could not load constituencies from API.")

    if const_names:
        selected_const = st.selectbox("Select a constituency", const_names)

        if selected_const:
            col1, col2 = st.columns([1, 1])

            # Fetch constituency data via query
            with st.spinner("Loading constituency data..."):
                result = api_call("/query", "POST", {
                    "query": f"Give me the complete results for {selected_const} in 2024",
                    "session_id": "explore_session",
                })

            with col1:
                st.markdown(f"#### 📋 {selected_const} — Results")
                if "error" not in result:
                    st.markdown(result.get("answer", ""))
                else:
                    st.error(result["error"])

            with col2:
                st.markdown(f"#### 📊 Vote Distribution")
                # Build chart data locally for instant rendering
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
                try:
                    from tools.visualization_tools import build_pie_chart_data, build_bar_chart_data
                    from tools.database import init_db
                    init_db()

                    pie_data = build_pie_chart_data(selected_const)
                    render_plotly_chart(pie_data)
                except Exception as e:
                    st.info(f"Chart generation: {e}")

            # Turnout and Margin charts
            st.markdown("---")
            col3, col4 = st.columns(2)
            try:
                from tools.visualization_tools import build_turnout_chart_data, build_margin_chart_data

                with col3:
                    st.markdown("#### 📈 Turnout Comparison (All)")
                    turnout_data = build_turnout_chart_data()
                    render_plotly_chart(turnout_data)

                with col4:
                    st.markdown("#### 📊 Victory Margins (All)")
                    margin_data = build_margin_chart_data()
                    render_plotly_chart(margin_data)
            except Exception as e:
                st.info(f"Additional charts: {e}")

    # Party Performance Section
    st.markdown("---")
    st.markdown("### Party Performance Tracker")

    party_data = api_call("/parties")
    if "error" not in party_data:
        party_list = party_data.get("parties", [])
    else:
        party_list = []

    if party_list:
        selected_party = st.selectbox("Select a party", party_list)
        if selected_party:
            with st.spinner("Analysing party performance..."):
                party_result = api_call("/query", "POST", {
                    "query": f"Analyse {selected_party}'s performance across all constituencies in 2024",
                    "session_id": "party_session",
                })
            if "error" not in party_result:
                st.markdown(party_result.get("answer", ""))
            else:
                st.error(party_result["error"])

            try:
                from tools.visualization_tools import build_bar_chart_data
                bar_data = build_bar_chart_data(state="")
                render_plotly_chart(bar_data)
            except Exception:
                pass

# ----- Tab 3: Alerts ---------------------------------------------------------
with tab3:
    st.markdown("### 🚨 Monitoring Alert Feed")
    st.markdown("Real-time anomaly detection across all loaded constituencies.")

    if st.button("🔄 Refresh Alerts", use_container_width=True):
        api_call("/scan", "POST")

    alerts_data = api_call("/alerts")

    if "error" in alerts_data:
        st.error(alerts_data["error"])
    else:
        alert_list = alerts_data.get("alerts", [])
        if not alert_list:
            st.success("✅ No alerts — all constituencies within normal parameters.")
        else:
            # Summary metrics
            critical = sum(1 for a in alert_list if a.get("severity") == "CRITICAL")
            warnings = sum(1 for a in alert_list if a.get("severity") == "WARNING")
            info = sum(1 for a in alert_list if a.get("severity") == "INFO")

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{len(alert_list)}</h3>
                    <p>Total Alerts</p>
                </div>
                """, unsafe_allow_html=True)
            with m2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #C62828">{critical}</h3>
                    <p>Critical</p>
                </div>
                """, unsafe_allow_html=True)
            with m3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #EF6C00">{warnings}</h3>
                    <p>Warnings</p>
                </div>
                """, unsafe_allow_html=True)
            with m4:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #0984e3">{info}</h3>
                    <p>Info</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            # Alert feed
            for alert in alert_list:
                severity = alert.get("severity", "INFO")
                css_class = {
                    "CRITICAL": "alert-critical",
                    "WARNING": "alert-warning",
                    "INFO": "alert-info",
                }.get(severity, "alert-info")

                icon = {"CRITICAL": "🔴", "WARNING": "⚠️", "INFO": "ℹ️"}.get(severity, "ℹ️")
                alert_type = alert.get("alert_type", "unknown").replace("_", " ").title()

                st.markdown(f"""
                <div class="{css_class}">
                    <strong>{icon} [{severity}] {alert_type}</strong><br>
                    {alert.get("message", "")}
                </div>
                """, unsafe_allow_html=True)
