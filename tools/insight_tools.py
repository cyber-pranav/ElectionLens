"""
ElectionLens — Insight tool functions.
Plain-language, citizen-friendly insight generation.
Separated from agent definition so tools can be tested without ADK installed.
"""

import json

from tools.gemini_tools import (
    generate_plain_summary,
    generate_explainer,
    generate_comparison,
    generate_insight_from_data,
)
from tools.database import get_constituency


def generate_summary(analysis_json: str) -> dict:
    """Produce a 3-sentence plain-English summary from election analysis JSON.

    Args:
        analysis_json: A JSON string containing election analysis data.

    Returns:
        A dict with the summary text.
    """
    summary = generate_plain_summary(analysis_json)
    return {"summary": summary}


def explain_election_term(term: str) -> dict:
    """Explain an election-related term in simple language for first-time voters.

    Args:
        term: The term to explain, e.g. 'NOTA', 'EVM', 'by-election', 'electoral bond'.

    Returns:
        A dict with the term and its explanation.
    """
    explanation = generate_explainer(term)
    return {"term": term, "explanation": explanation}


def compare_constituencies(constituency_a: str, constituency_b: str, year: int = 2024) -> dict:
    """Compare two constituencies side-by-side with a narrative summary.

    Args:
        constituency_a: Name of the first constituency.
        constituency_b: Name of the second constituency.
        year: Election year (default 2024).

    Returns:
        A dict with both data sets and a comparison narrative.
    """
    data_a = get_constituency(constituency_a, year)
    data_b = get_constituency(constituency_b, year)

    if not data_a:
        return {"error": f"Constituency '{constituency_a}' not found for {year}."}
    if not data_b:
        return {"error": f"Constituency '{constituency_b}' not found for {year}."}

    narrative = generate_comparison(json.dumps(data_a), json.dumps(data_b))
    return {
        "constituency_a": data_a,
        "constituency_b": data_b,
        "comparison_narrative": narrative,
    }


def generate_answer(query: str, data: str) -> dict:
    """Generate a citizen-friendly answer for a user's election question.

    Args:
        query: The user's question in natural language.
        data: JSON string of relevant election data to base the answer on.

    Returns:
        A dict with the answer text.
    """
    answer = generate_insight_from_data(query, data)
    return {"answer": answer}
