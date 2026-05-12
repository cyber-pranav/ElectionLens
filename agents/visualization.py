"""
ElectionLens — VisualizationAgent.
Generates chart-ready JSON data structures for the frontend.
"""

from google.adk.agents import Agent

from tools.visualization_tools import (
    build_bar_chart_data,
    build_pie_chart_data,
    build_turnout_chart_data,
    build_seats_chart_data,
    build_margin_chart_data,
)

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
