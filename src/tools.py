from __future__ import annotations

import logging
from apify import Actor
from langchain_core.tools import tool

from src.models import BuildingCodeReport
from src.scraper import run_research_agent


@tool
async def tool_research_building_code(user_task: str, max_steps: int = 15) -> BuildingCodeReport:
    """
    Research building codes and zoning requirements for a specific task.
    This tool controls a headless browser to search for the relevant code, navigate the website, extract relevant sections, and summarize the findings.

    Args:
        user_task (str): The specific task or question about building codes (e.g., "Find stair requirements for a new house in Los Angeles").
        max_steps (int, optional): Maximum number of navigation steps. Defaults to 15.

    Returns:
        BuildingCodeReport: A structured report containing the findings and requirements.
    """
    Actor.log.info(f"Starting building code research for task: {user_task}")
    try:
        report = await run_research_agent(user_task, max_steps)
        return report
    except Exception as e:
        Actor.log.error(f"Error executing tool_research_building_code: {e}")
        # Return a meaningful error structure
        return BuildingCodeReport(
            task=f"Error: {e}",
            jurisdiction="Error",
            code_source=None,
            assumptions=[],
            requirements=[]
        )
