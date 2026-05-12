"""
ElectionLens — VisualizationAgent.
Generates chart-ready JSON data structures for the frontend.
"""

from google.adk.agents import Agent

from tools.database import (
    get_all_constituencies,
    get_constituency,
    get_constituencies_by_party,
    get_constituencies_by_state,
)


def build_bar_chart_data(constituency: str = "", state: str = "", year: int = 2024) -> dict:
    """Build bar chart data for party-wise vote distribution.

    Args:
        constituency: Optional specific constituency for candidate-level chart.
        state: Optional state for state-level party chart.
        year: Election year.

    Returns:
        Plotly-compatible bar chart JSON.
    """
    if constituency:
        row = get_constituency(constituency, year)
        if not row:
            return {"error": f"Constituency '{constituency}' not found."}
        labels = [f"{row['winner']} ({row['party']})", f"{row['runner_up']} ({row['runner_up_party']})"]
        if row.get("nota_votes", 0) > 0:
            labels.append("NOTA")
        values = [row["votes"], row["runner_up_votes"]]
        if row.get("nota_votes", 0) > 0:
            values.append(row["nota_votes"])
        colors = ["#4CAF50", "#F44336", "#9E9E9E"]
        return {
            "chart_type": "bar",
            "title": f"Vote Distribution — {row['name']} ({year})",
            "labels": labels,
            "values": values,
            "colors": colors[:len(labels)],
        }

    if state:
        rows = get_constituencies_by_state(state, year)
    else:
        rows = get_all_constituencies(year)

    party_votes: dict[str, int] = {}
    for r in rows:
        party_votes[r["party"]] = party_votes.get(r["party"], 0) + r["votes"]
        party_votes[r["runner_up_party"]] = party_votes.get(r["runner_up_party"], 0) + r["runner_up_votes"]

    sorted_parties = sorted(party_votes.items(), key=lambda x: x[1], reverse=True)
    palette = ["#FF6F00", "#1565C0", "#2E7D32", "#C62828", "#6A1B9A",
               "#00838F", "#EF6C00", "#4527A0", "#AD1457", "#00695C"]
    return {
        "chart_type": "bar",
        "title": f"Party-wise Votes — {state or 'All India'} ({year})",
        "labels": [p[0] for p in sorted_parties],
        "values": [p[1] for p in sorted_parties],
        "colors": palette[:len(sorted_parties)],
    }


def build_pie_chart_data(constituency: str, year: int = 2024) -> dict:
    """Build pie chart data for vote share in a constituency.

    Args:
        constituency: Constituency name.
        year: Election year.

    Returns:
        Plotly-compatible pie chart JSON.
    """
    row = get_constituency(constituency, year)
    if not row:
        return {"error": f"Constituency '{constituency}' not found."}

    labels = [f"{row['winner']} ({row['party']})", f"{row['runner_up']} ({row['runner_up_party']})"]
    values = [row["votes"], row["runner_up_votes"]]
    if row.get("nota_votes", 0) > 0:
        labels.append("NOTA")
        values.append(row["nota_votes"])
    return {
        "chart_type": "pie",
        "title": f"Vote Share — {row['name']} ({year})",
        "labels": labels,
        "values": values,
        "colors": ["#4CAF50", "#F44336", "#9E9E9E"],
    }


def build_turnout_chart_data(state: str = "", year: int = 2024) -> dict:
    """Build turnout comparison bar chart.

    Args:
        state: Optional state filter.
        year: Election year.

    Returns:
        Plotly-compatible bar chart JSON for turnout comparison.
    """
    if state:
        rows = get_constituencies_by_state(state, year)
    else:
        rows = get_all_constituencies(year)

    rows_sorted = sorted(rows, key=lambda x: x["turnout_percent"], reverse=True)
    colors = []
    for r in rows_sorted:
        if r["turnout_percent"] >= 65:
            colors.append("#2E7D32")
        elif r["turnout_percent"] >= 50:
            colors.append("#FF8F00")
        else:
            colors.append("#C62828")

    return {
        "chart_type": "bar",
        "title": f"Voter Turnout — {state or 'All Constituencies'} ({year})",
        "labels": [r["name"] for r in rows_sorted],
        "values": [r["turnout_percent"] for r in rows_sorted],
        "colors": colors,
        "y_axis_label": "Turnout %",
    }


def build_seats_chart_data(year: int = 2024) -> dict:
    """Build party-wise seat count chart.

    Args:
        year: Election year.

    Returns:
        Plotly-compatible chart data for seats won by party.
    """
    rows = get_all_constituencies(year)
    seat_count: dict[str, int] = {}
    for r in rows:
        seat_count[r["party"]] = seat_count.get(r["party"], 0) + 1

    sorted_parties = sorted(seat_count.items(), key=lambda x: x[1], reverse=True)
    palette = ["#FF6F00", "#1565C0", "#2E7D32", "#C62828", "#6A1B9A",
               "#00838F", "#EF6C00", "#4527A0", "#AD1457", "#00695C"]
    return {
        "chart_type": "bar",
        "title": f"Seats Won by Party ({year})",
        "labels": [p[0] for p in sorted_parties],
        "values": [p[1] for p in sorted_parties],
        "colors": palette[:len(sorted_parties)],
    }


def build_margin_chart_data(state: str = "", year: int = 2024) -> dict:
    """Build victory margin comparison chart.

    Args:
        state: Optional state filter.
        year: Election year.

    Returns:
        Chart data for margin comparison across constituencies.
    """
    if state:
        rows = get_constituencies_by_state(state, year)
    else:
        rows = get_all_constituencies(year)

    rows_sorted = sorted(rows, key=lambda x: x["margin"])
    colors = []
    for r in rows_sorted:
        if r["margin"] < 15000:
            colors.append("#C62828")
        elif r["margin"] < 100000:
            colors.append("#FF8F00")
        else:
            colors.append("#2E7D32")

    return {
        "chart_type": "bar",
        "title": f"Victory Margins — {state or 'All Constituencies'} ({year})",
        "labels": [r["name"] for r in rows_sorted],
        "values": [r["margin"] for r in rows_sorted],
        "colors": colors,
        "y_axis_label": "Margin (votes)",
    }


INSTRUCTION = """\
You are the **VisualizationAgent** of ElectionLens.
Generate chart-ready JSON data for the frontend. You never produce HTML or CSS.
You have tools to build bar charts, pie charts, turnout charts, seat charts,
and margin charts. Call the appropriate tool based on the request.
"""

visualization_agent = Agent(
    name="visualization_agent",
    model="gemini-2.0-flash",
    instruction=INSTRUCTION,
    description="Generates chart-ready JSON: bar charts, pie charts, turnout, seats, and margins.",
    tools=[
        build_bar_chart_data,
        build_pie_chart_data,
        build_turnout_chart_data,
        build_seats_chart_data,
        build_margin_chart_data,
    ],
)
