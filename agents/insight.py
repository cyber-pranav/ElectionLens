"""
ElectionLens — InsightAgent.
Generates plain-language, citizen-friendly insights from raw analysis data.
"""

from google.adk.agents import Agent

from tools.insight_tools import (
    generate_summary,
    explain_election_term,
    compare_constituencies,
    generate_answer,
)


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
