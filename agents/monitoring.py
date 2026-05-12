"""
ElectionLens — MonitoringAgent.
Watches for anomalies, close contests, and recount-risk patterns.
"""

from google.adk.agents import Agent

from tools.database import (
    get_all_constituencies,
    get_constituency,
    save_alert,
    clear_alerts,
    get_all_alerts,
)

NATIONAL_AVG_TURNOUT = 55.0
TURNOUT_DEVIATION_THRESHOLD = 10.0
CLOSE_CONTEST_MARGIN_PERCENT = 2.0
RECOUNT_MARGIN_ABSOLUTE = 15000


def detect_anomaly(constituency: str = "", year: int = 2024) -> dict:
    """Flag constituencies with abnormal voter turnout vs national average.

    Args:
        constituency: Optional. If empty, scans all.
        year: Election year.

    Returns:
        Dict with anomalies list.
    """
    if constituency:
        row = get_constituency(constituency, year)
        rows = [row] if row else []
        if not row:
            return {"error": f"Constituency '{constituency}' not found."}
    else:
        rows = get_all_constituencies(year)

    anomalies = []
    for r in rows:
        deviation = r["turnout_percent"] - NATIONAL_AVG_TURNOUT
        if abs(deviation) >= TURNOUT_DEVIATION_THRESHOLD:
            direction = "above" if deviation > 0 else "below"
            severity = "CRITICAL" if abs(deviation) >= 15 else "WARNING"
            msg = (
                f"{r['name']} ({r['state']}): {r['turnout_percent']}% turnout — "
                f"{abs(round(deviation, 1))}% {direction} national average"
            )
            anomalies.append({
                "constituency": r["name"], "state": r["state"],
                "turnout_percent": r["turnout_percent"],
                "deviation": round(deviation, 1), "severity": severity, "message": msg,
            })
    return {"scan_type": "turnout_anomaly", "anomalies_found": len(anomalies), "anomalies": anomalies}


def check_close_contest(constituency: str = "", year: int = 2024) -> dict:
    """Flag constituencies where winning margin is less than 2%.

    Args:
        constituency: Optional. If empty, scans all.
        year: Election year.

    Returns:
        Dict with close contests list.
    """
    if constituency:
        row = get_constituency(constituency, year)
        rows = [row] if row else []
        if not row:
            return {"error": f"Constituency '{constituency}' not found."}
    else:
        rows = get_all_constituencies(year)

    close = []
    for r in rows:
        total = r["votes"] + r["runner_up_votes"] + r.get("nota_votes", 0)
        mpct = (r["margin"] / total * 100) if total else 0
        if mpct < CLOSE_CONTEST_MARGIN_PERCENT:
            msg = (
                f"{r['name']} ({r['state']}): {r['winner']} won by only "
                f"{r['margin']:,} votes ({round(mpct, 2)}%) — TOO CLOSE TO CALL"
            )
            close.append({
                "constituency": r["name"], "state": r["state"],
                "winner": r["winner"], "margin": r["margin"],
                "margin_percent": round(mpct, 2),
                "severity": "CRITICAL" if mpct < 1.0 else "WARNING", "message": msg,
            })
    return {"scan_type": "close_contest", "close_contests_found": len(close), "close_contests": close}


def track_recount_risk(constituency: str = "", year: int = 2024) -> dict:
    """Highlight seats with margins small enough to trigger recount demands.

    Args:
        constituency: Optional. If empty, scans all.
        year: Election year.

    Returns:
        Dict with recount risk list.
    """
    if constituency:
        row = get_constituency(constituency, year)
        rows = [row] if row else []
        if not row:
            return {"error": f"Constituency '{constituency}' not found."}
    else:
        rows = get_all_constituencies(year)

    risks = []
    for r in rows:
        if r["margin"] < RECOUNT_MARGIN_ABSOLUTE:
            msg = f"{r['name']} ({r['state']}): margin of only {r['margin']:,} votes — recount risk"
            severity = "CRITICAL" if r["margin"] < 8000 else "WARNING"
            risks.append({
                "constituency": r["name"], "state": r["state"],
                "winner": r["winner"], "party": r["party"],
                "margin": r["margin"], "severity": severity, "message": msg,
            })
    return {"scan_type": "recount_risk", "risks_found": len(risks), "risks": risks}


def run_full_scan(year: int = 2024) -> dict:
    """Run all monitoring checks and persist alerts.

    Args:
        year: Election year.

    Returns:
        Summary of all alerts found.
    """
    clear_alerts()
    anomalies = detect_anomaly("", year)
    close_contests = check_close_contest("", year)
    recount_risks = track_recount_risk("", year)

    total = 0
    for a in anomalies.get("anomalies", []):
        save_alert(a["constituency"], a["state"], "anomaly", a["severity"], a["message"], year)
        total += 1
    for c in close_contests.get("close_contests", []):
        save_alert(c["constituency"], c["state"], "close_contest", c["severity"], c["message"], year)
        total += 1
    for r in recount_risks.get("risks", []):
        save_alert(r["constituency"], r["state"], "recount_risk", r["severity"], r["message"], year)
        total += 1

    return {
        "scan_type": "full_scan", "year": year, "total_alerts": total,
        "anomalies": anomalies["anomalies_found"],
        "close_contests": close_contests["close_contests_found"],
        "recount_risks": recount_risks["risks_found"],
    }


def get_alerts(year: int = 2024) -> dict:
    """Retrieve all persisted monitoring alerts.

    Args:
        year: Election year.

    Returns:
        Dict with all stored alerts.
    """
    alerts = get_all_alerts()
    return {"total": len(alerts), "alerts": alerts}


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
