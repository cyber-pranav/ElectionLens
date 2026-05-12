"""
ElectionLens — Election data fetch functions.
These are used as ADK agent tools for the DataIngestionAgent.
All functions return plain dicts/lists so ADK can serialise them automatically.
"""

from tools.database import (
    get_all_constituencies,
    get_constituency,
    get_constituencies_by_party,
    get_constituencies_by_state,
    get_all_parties,
    get_all_states,
)


# ---------------------------------------------------------------------------
# Tool: fetch_election_results
# ---------------------------------------------------------------------------

def fetch_election_results(state: str, year: int = 2024) -> dict:
    """Fetch election results for a given state and year.

    Args:
        state: Name of the Indian state, e.g. 'Uttar Pradesh'.
        year: Election year (default 2024).

    Returns:
        A dict with 'state', 'year', and 'constituencies' list.
    """
    rows = get_constituencies_by_state(state, year)
    return {
        "state": state,
        "year": year,
        "count": len(rows),
        "constituencies": rows,
    }


# ---------------------------------------------------------------------------
# Tool: fetch_candidate_profile
# ---------------------------------------------------------------------------

def fetch_candidate_profile(name: str) -> dict:
    """Fetch a candidate's profile from the loaded election data.

    Args:
        name: Full or partial name of the candidate.

    Returns:
        A dict with candidate details from the election data.
    """
    all_rows = get_all_constituencies()
    matches = []
    lower_name = name.lower()
    for row in all_rows:
        if lower_name in row["winner"].lower():
            matches.append({
                "candidate": row["winner"],
                "party": row["party"],
                "constituency": row["name"],
                "state": row["state"],
                "votes_received": row["votes"],
                "margin_of_victory": row["margin"],
                "role": "winner",
                "year": row["year"],
            })
        if lower_name in row["runner_up"].lower():
            matches.append({
                "candidate": row["runner_up"],
                "party": row["runner_up_party"],
                "constituency": row["name"],
                "state": row["state"],
                "votes_received": row["runner_up_votes"],
                "role": "runner_up",
                "year": row["year"],
            })
    if not matches:
        return {"error": f"No candidate found matching '{name}' in loaded data."}
    return {"candidate_name": name, "results": matches}


# ---------------------------------------------------------------------------
# Tool: fetch_voter_turnout
# ---------------------------------------------------------------------------

def fetch_voter_turnout(constituency: str) -> dict:
    """Retrieve voter turnout data for a specific constituency.

    Args:
        constituency: Name of the constituency, e.g. 'Varanasi'.

    Returns:
        A dict with turnout stats.
    """
    row = get_constituency(constituency)
    if not row:
        return {"error": f"Constituency '{constituency}' not found."}
    return {
        "constituency": row["name"],
        "state": row["state"],
        "turnout_percent": row["turnout_percent"],
        "total_voters": row["total_voters"],
        "votes_polled": row["votes"] + row["runner_up_votes"] + row.get("nota_votes", 0),
        "year": row["year"],
    }


# ---------------------------------------------------------------------------
# Tool: list_all_constituencies
# ---------------------------------------------------------------------------

def list_all_constituencies(year: int = 2024) -> dict:
    """Return the names of every constituency loaded for a given year.

    Args:
        year: Election year (default 2024).

    Returns:
        A dict with constituency names and count.
    """
    rows = get_all_constituencies(year)
    return {
        "year": year,
        "count": len(rows),
        "constituencies": [r["name"] for r in rows],
    }


# ---------------------------------------------------------------------------
# Tool: list_all_parties
# ---------------------------------------------------------------------------

def list_all_parties(year: int = 2024) -> dict:
    """Return all distinct winning parties for a given year.

    Args:
        year: Election year (default 2024).

    Returns:
        A dict with party names and count.
    """
    parties = get_all_parties(year)
    return {"year": year, "count": len(parties), "parties": parties}


# ---------------------------------------------------------------------------
# Tool: list_all_states
# ---------------------------------------------------------------------------

def list_all_states(year: int = 2024) -> dict:
    """Return all distinct states in the dataset.

    Args:
        year: Election year (default 2024).

    Returns:
        A dict with state names.
    """
    states = get_all_states(year)
    return {"year": year, "count": len(states), "states": states}
