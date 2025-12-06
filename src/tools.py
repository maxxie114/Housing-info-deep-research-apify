from __future__ import annotations

import logging
from apify import Actor
from langchain_core.tools import tool

from src.models import BCARequirementReport
from src.scraper import run_bca_ncc_agent


@tool
async def tool_research_bca(user_task: str, max_steps: int = 15) -> BCARequirementReport:
    """
    Research the National Construction Code (NCC) / Building Code of Australia (BCA) to find requirements for a specific building task.
    This tool controls a headless browser to navigate the NCC website, extract relevant sections, and summarize the findings.

    Args:
        user_task (str): The specific task or question about building codes (e.g., "Find stair and balustrade requirements for a new Class 1 dwelling").
        max_steps (int, optional): Maximum number of navigation steps. Defaults to 15.

    Returns:
        BCARequirementReport: A structured report containing the findings and requirements.
    """
    Actor.log.info(f"Starting BCA research for task: {user_task}")
    try:
        report = await run_bca_ncc_agent(user_task, max_steps)
        return report
    except Exception as e:
        Actor.log.error(f"Error executing tool_research_bca: {e}")
        # Return a meaningful error structure or re-raise depending on agent needs
        # For now, returning an empty report with error message in task field to avoid crashing the agent
        return BCARequirementReport(
            task=f"Error: {e}",
            assumed_location="Error",
            assumed_volume=None,
            assumptions=[],
            requirements=[]
        )
