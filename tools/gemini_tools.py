"""
ElectionLens — Gemini generation helpers.
Thin wrappers around the google-generativeai SDK used by InsightAgent
and any agent that needs free-form text generation beyond tool-calling.
"""

import json
import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure the SDK once at import time
genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))

_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


def generate_plain_summary(analysis_json: str) -> str:
    """Turn structured election analysis JSON into a 3-sentence plain-English summary.

    Args:
        analysis_json: JSON string of election analysis data.

    Returns:
        A plain-language summary string suitable for first-time voters.
    """
    prompt = (
        "You are an election educator in India. "
        "Given the following election data, write a concise 3-sentence summary "
        "in simple language for a first-time voter. Be factual, avoid jargon, "
        "and use short sentences.\n\n"
        f"Data:\n{analysis_json}"
    )
    model = genai.GenerativeModel(_MODEL_NAME)
    response = model.generate_content(prompt)
    return response.text


def generate_explainer(term: str) -> str:
    """Explain an election-related term in plain language.

    Args:
        term: The election term to explain, e.g. 'NOTA', 'EVM', 'by-election'.

    Returns:
        A plain-language explanation string.
    """
    prompt = (
        "You are an election educator in India. "
        f"Explain the election term '{term}' to a first-time voter in India. "
        "Use simple language, no jargon, 2-3 short sentences. Be factual."
    )
    model = genai.GenerativeModel(_MODEL_NAME)
    response = model.generate_content(prompt)
    return response.text


def generate_comparison(data_a: str, data_b: str) -> str:
    """Generate a narrative comparison of two constituencies.

    Args:
        data_a: JSON string of constituency A data.
        data_b: JSON string of constituency B data.

    Returns:
        A 2-sentence comparative narrative.
    """
    prompt = (
        "You are an election educator in India. "
        "Compare the following two constituencies side-by-side. "
        "Write a 2-sentence narrative comparison highlighting key differences. "
        "Use simple language.\n\n"
        f"Constituency A:\n{data_a}\n\n"
        f"Constituency B:\n{data_b}"
    )
    model = genai.GenerativeModel(_MODEL_NAME)
    response = model.generate_content(prompt)
    return response.text


def generate_insight_from_data(query: str, data: str) -> str:
    """Generate an insight about election data for a user query.

    Args:
        query: The user's original question.
        data: JSON string of relevant election data.

    Returns:
        A clear, citizen-friendly answer string.
    """
    prompt = (
        "You are ElectionLens, an AI election intelligence assistant for India. "
        "Answer the following question using the provided data. "
        "Be factual, concise, and use simple language suitable for any citizen. "
        "Include specific numbers and percentages where relevant.\n\n"
        f"Question: {query}\n\n"
        f"Data:\n{data}"
    )
    model = genai.GenerativeModel(_MODEL_NAME)
    response = model.generate_content(prompt)
    return response.text
