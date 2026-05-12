"""
ElectionLens — InsightAgent.
Generates plain-language, citizen-friendly insights from raw analysis data.
"""

import json

from google.adk.agents import Agent

from tools.gemini_tools import (
    generate_plain_summary,
    generate_explainer,
    generate_comparison,
    generate_insight_from_data,
)
from tools.database import get_constituency


# ---------------------------------------------------------------------------
# Tool functions
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Agent definition
# ---------------------------------------------------------------------------

INSTRUCTION = """\
You are the **InsightAgent** of ElectionLens.

Your role is to convert raw election data and analysis into plain-language,
citizen-friendly insights that even a first-time voter can understand.

You can:
  • Generate 3-sentence summaries of analysis results
  • Explain election jargon (NOTA, EVM, by-election, etc.)
  • Compare two constituencies side-by-side with a narrative
  • Answer user questions using provided data

Rules:
  - Use simple language, no jargon, short sentences.
  - Always be factual — never speculate or editorialize.
  - Include specific numbers and percentages where relevant.
  - You are an educator, not a commentator.
"""

insight_agent = Agent(
    name="insight_agent",
    model="gemini-2.0-flash",
    instruction=INSTRUCTION,
    description=(
        "Converts raw election data into plain-language insights, "
        "explains election jargon, and compares constituencies for citizens."
    ),
    tools=[
        generate_summary,
        explain_election_term,
        compare_constituencies,
        generate_answer,
    ],
)
