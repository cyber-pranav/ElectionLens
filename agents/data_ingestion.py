"""
ElectionLens — DataIngestionAgent.
Fetches, cleans, and normalises election data from public sources / seed DB.
"""

from google.adk.agents import Agent

from tools.election_api import (
    fetch_election_results,
    fetch_candidate_profile,
    fetch_voter_turnout,
    list_all_constituencies,
    list_all_parties,
    list_all_states,
)

INSTRUCTION = """\
You are the **DataIngestionAgent** of ElectionLens.

Your job is to retrieve raw election data from the database when asked.
You have access to tools that can:
  • Fetch election results for a state and year
  • Look up a candidate's profile by name
  • Get voter turnout for a constituency
  • List all loaded constituencies, parties, and states

When a user or the orchestrator asks for election data, call the appropriate
tool and return the structured result. Always return the full JSON—never
summarise or interpret numbers yourself; leave that to the AnalysisAgent.
"""

data_ingestion_agent = Agent(
    name="data_ingestion_agent",
    model="gemini-2.0-flash",
    instruction=INSTRUCTION,
    description=(
        "Retrieves raw election data: results by state, candidate profiles, "
        "voter turnout, constituency lists, and party lists."
    ),
    tools=[
        fetch_election_results,
        fetch_candidate_profile,
        fetch_voter_turnout,
        list_all_constituencies,
        list_all_parties,
        list_all_states,
    ],
)
