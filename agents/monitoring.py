"""
ElectionLens — MonitoringAgent.
Watches for anomalies, close contests, and recount-risk patterns.
"""

from google.adk.agents import Agent

from tools.monitoring_tools import (
    detect_anomaly,
    check_close_contest,
    track_recount_risk,
    run_full_scan,
    get_alerts,
)

INSTRUCTION = """\
You are the **MonitoringAgent** of ElectionLens.
Detect anomalies, close contests, and recount risks in election data.
Severity: INFO (normal), WARNING (unusual), CRITICAL (abnormal).
Always run the appropriate scan tool and return structured results.
"""

monitoring_agent = Agent(
    name="monitoring_agent",
    model="gemini-2.0-flash",
    instruction=INSTRUCTION,
    description="Monitors election data for anomalies: turnout spikes, close contests, recount risks.",
    tools=[detect_anomaly, check_close_contest, track_recount_risk, run_full_scan, get_alerts],
)
