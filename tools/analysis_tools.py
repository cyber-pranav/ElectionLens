"""
ElectionLens — Analysis tool functions.
Pure-logic quantitative analysis on election data.
Separated from agent definition so tools can be tested without ADK installed.
"""

from tools.database import (
    get_all_constituencies,
    get_constituency,
    get_constituencies_by_party,
    get_constituencies_by_state,
)


def compute_vote_share(party: str, state: str = "", year: int = 2024) -> dict:
    """Calculate the percentage vote share for a party, optionally filtered by state.

    Args:
        party: Party abbreviation, e.g. 'BJP', 'INC'.
        state: Optional state filter. Empty string means all states.
        year: Election year (default 2024).

    Returns:
        A dict with party, region, total_votes, total_votes_in_region, and vote_share_percent.
    """
    if state:
        all_rows = get_constituencies_by_state(state, year)
    else:
        all_rows = get_all_constituencies(year)

    total_votes_all = sum(r["votes"] + r["runner_up_votes"] + r.get("nota_votes", 0) for r in all_rows)
    party_lower = party.lower()
    party_votes = 0
    seats_won = 0
    for r in all_rows:
        if r["party"].lower() == party_lower:
            party_votes += r["votes"]
            seats_won += 1
        if r["runner_up_party"].lower() == party_lower:
            party_votes += r["runner_up_votes"]

    share = round(party_votes / total_votes_all * 100, 2) if total_votes_all else 0
    return {
        "party": party,
        "region": state or "All India (loaded data)",
        "party_votes": party_votes,
        "total_votes_in_region": total_votes_all,
        "vote_share_percent": share,
        "seats_won": seats_won,
        "total_seats_in_region": len(all_rows),
        "year": year,
    }


def detect_swing(constituency: str, year1: int = 2019, year2: int = 2024) -> dict:
    """Compute electoral swing between two elections for a constituency.

    Args:
        constituency: Constituency name.
        year1: Earlier election year.
        year2: Later election year.

    Returns:
        A dict with swing data or an error if data is unavailable.
    """
    d1 = get_constituency(constituency, year1)
    d2 = get_constituency(constituency, year2)
    if not d2:
        return {"error": f"No data for {constituency} in {year2}."}
    if not d1:
        return {
            "constituency": constituency,
            "note": f"Only {year2} data available. Cannot compute swing without {year1} data.",
            "year2_winner": d2["winner"],
            "year2_party": d2["party"],
            "year2_margin": d2["margin"],
        }
    swing = round(
        (d2["margin"] / (d2["votes"] + d2["runner_up_votes"]) * 100)
        - (d1["margin"] / (d1["votes"] + d1["runner_up_votes"]) * 100),
        2,
    )
    return {
        "constituency": constituency,
        "year1": year1,
        "year2": year2,
        "year1_winner": d1["winner"],
        "year2_winner": d2["winner"],
        "margin_change": d2["margin"] - d1["margin"],
        "swing_percent": swing,
    }


def rank_candidates(constituency: str, year: int = 2024) -> dict:
    """Return winner, runner-up, and margin for a constituency.

    Args:
        constituency: Constituency name.
        year: Election year (default 2024).

    Returns:
        A dict with ranking data.
    """
    row = get_constituency(constituency, year)
    if not row:
        return {"error": f"Constituency '{constituency}' not found for {year}."}
    total_valid = row["votes"] + row["runner_up_votes"] + row.get("nota_votes", 0)
    return {
        "constituency": row["name"],
        "state": row["state"],
        "winner": row["winner"],
        "winner_party": row["party"],
        "winner_votes": row["votes"],
        "winner_vote_share": round(row["votes"] / total_valid * 100, 2) if total_valid else 0,
        "runner_up": row["runner_up"],
        "runner_up_party": row["runner_up_party"],
        "runner_up_votes": row["runner_up_votes"],
        "runner_up_vote_share": round(row["runner_up_votes"] / total_valid * 100, 2) if total_valid else 0,
        "margin": row["margin"],
        "margin_percent": round(row["margin"] / total_valid * 100, 2) if total_valid else 0,
        "turnout_percent": row["turnout_percent"],
        "nota_votes": row.get("nota_votes", 0),
        "year": year,
    }


def trend_analysis(party: str, year: int = 2024) -> dict:
    """Analyse a party's performance across all loaded constituencies for a year.

    Args:
        party: Party abbreviation, e.g. 'BJP'.
        year: Election year (default 2024).

    Returns:
        A dict with performance metrics.
    """
    all_rows = get_all_constituencies(year)
    party_lower = party.lower()
    won = [r for r in all_rows if r["party"].lower() == party_lower]
    lost = [r for r in all_rows if r["runner_up_party"].lower() == party_lower]
    total_votes = sum(r["votes"] for r in won) + sum(r["runner_up_votes"] for r in lost)
    avg_margin_won = round(sum(r["margin"] for r in won) / len(won), 0) if won else 0
    return {
        "party": party,
        "year": year,
        "seats_won": len(won),
        "seats_lost": len(lost),
        "total_seats_contested": len(won) + len(lost),
        "total_votes_received": total_votes,
        "average_winning_margin": avg_margin_won,
        "constituencies_won": [r["name"] for r in won],
        "constituencies_lost": [r["name"] for r in lost],
    }


def party_performance_by_state(party: str, year: int = 2024) -> dict:
    """Break down party performance by state.

    Args:
        party: Party abbreviation.
        year: Election year.

    Returns:
        A dict with per-state breakdown.
    """
    all_rows = get_all_constituencies(year)
    party_lower = party.lower()
    state_map: dict[str, dict] = {}
    for r in all_rows:
        s = r["state"]
        if s not in state_map:
            state_map[s] = {"state": s, "won": 0, "lost": 0, "total": 0, "total_votes": 0}
        state_map[s]["total"] += 1
        if r["party"].lower() == party_lower:
            state_map[s]["won"] += 1
            state_map[s]["total_votes"] += r["votes"]
        elif r["runner_up_party"].lower() == party_lower:
            state_map[s]["lost"] += 1
            state_map[s]["total_votes"] += r["runner_up_votes"]
    return {
        "party": party,
        "year": year,
        "states": list(state_map.values()),
    }
