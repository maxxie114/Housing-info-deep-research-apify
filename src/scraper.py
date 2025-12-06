from __future__ import annotations

import asyncio
import os
import logging
from typing import List, Optional, Tuple

from playwright.async_api import async_playwright
from openai import OpenAI
from apify import Actor

from src.models import BuildingCodeReport, BuildingCodeRequirement

# OpenAI client initialization (lazy)
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ALLOWED_ACTIONS = """
You may ONLY respond with exactly ONE of the following actions (no explanation):

NAVIGATE <url>
CLICK <selector>
EXTRACT
FINISH
"""

AGENT_SYSTEM_PROMPT = f"""
You are an autonomous web agent tasked with researching building codes and zoning requirements.
Your goal is to navigate the building code website to find specific requirements matching the user's task.

Your job is to:
1. Read the current rendered HTML of the page.
2. Decide the best next action to move towards answering the user's building code task.
3. Determine which Volume / Part / Chapter / Section is relevant.
4. When you have reached a page that contains the key code requirements, issue EXTRACT.
5. If you are truly finished and have nothing more to extract, issue FINISH.

You control a headless browser that can:
- NAVIGATE <url>  (go to an absolute or relative URL)
- CLICK <selector> (click a link/button/etc. using Playwright selector syntax)
- EXTRACT         (tell the controller to return the current HTML and screenshot)
- FINISH          (stop the agent loop)

Rules:
- You are NOT restricted to a single domain, but stay on relevant building code sites (e.g. UpCodes, Municode, city/state portals).
- Prefer NAVIGATE for obvious URLs (e.g. direct links to chapters).
- Use CLICK when you need to expand menus, open parts/chapters, or follow links.
- Think step-by-step, but DO NOT output your thinking, only actions.

{ALLOWED_ACTIONS}
"""

class WebScraperActor:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    async def init_browser(self):
        if self.playwright is None:
            self.playwright = await async_playwright().start()
        if self.browser is None:
            try:
                # Try launching with typical Apify Actor arguments
                self.browser = await self.playwright.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-dev-shm-usage",
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-gpu",
                    ],
                )
            except Exception as e:
                Actor.log.error(f"Failed to launch browser: {e}")
                raise

        if self.page is None or self.page.is_closed():
            self.page = await self.browser.new_page()

    async def goto(self, url: str) -> str:
        await self.init_browser()
        try:
            await self.page.goto(url, wait_until="load", timeout=60000)
            # small wait to allow dynamic content
            await self.page.wait_for_timeout(1500)
            return await self.page.content()
        except Exception as e:
            Actor.log.error(f"Error navigating to {url}: {e}")
            return ""

    async def click(self, selector: str) -> str:
        """
        selector can be any Playwright selector.
        """
        await self.init_browser()
        try:
            await self.page.click(selector, timeout=10000)
            await self.page.wait_for_timeout(1500)
            return await self.page.content()
        except Exception as e:
            Actor.log.error(f"Error clicking selector {selector}: {e}")
            return await self.page.content()

    async def extract_html(self) -> str:
        await self.init_browser()
        return await self.page.content()

    async def screenshot(self, path="page.png") -> str:
        await self.init_browser()
        await self.page.screenshot(path=path, full_page=True)
        return path

    async def screenshot_bytes(self) -> bytes:
        await self.init_browser()
        return await self.page.screenshot(full_page=True)

    async def close(self):
        try:
            if self.browser is not None:
                await self.browser.close()
        except Exception:
            pass
        try:
            if self.playwright is not None:
                await self.playwright.stop()
        except Exception:
            pass
        self.playwright = None
        self.browser = None
        self.page = None

async def llm_choose_action(current_html: str, history: List[str], user_task: str) -> str:
    """
    Ask gpt-4o-mini to choose the next agent action.
    """
    html_snippet = current_html[:8000]  # keep it within reasonable token budget
    history_text = "\n".join(history[-10:])  # last 10 actions
    
    from apify import Configuration
    token = Configuration.get_global_configuration().token

    client = OpenAI(
        base_url="https://openrouter.apify.actor/api/v1",
        api_key="no-key-required-but-must-not-be-empty",
        default_headers={"Authorization": f"Bearer {token}"}
    )

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.1,
            messages=[
                {"role": "system", "content": AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": f"USER TASK: {user_task}"},
                {
                    "role": "assistant",
                    "content": f"RECENT ACTIONS:\n{history_text if history_text else '(none)'}",
                },
                {
                    "role": "assistant",
                    "content": f"CURRENT PAGE HTML (truncated):\n{html_snippet}",
                },
            ],
        )
        action = resp.choices[0].message.content.strip()
        return action
    except Exception as e:
        Actor.log.error(f"LLM API error: {e}")
        return "FINISH"


async def search_for_start_url(user_task: str) -> str:
    """
    Uses apify/rag-web-browser to search key terms and find a good starting URL.
    Returns the URL of the first organic result.
    """
    Actor.log.info(f"Searching for starting URL for task: {user_task}")
    
    # Construct a search query that explicitly asks for the code location
    search_query = f"{user_task} building code official site"
    
    try:
        # Call apify/rag-web-browser
        run = await Actor.call(
            "apify/rag-web-browser",
            run_input={
                "query": search_query,
                "maxResults": 1,
            }
        )
        
        # Get the default dataset items
        if run:
            dataset_id = run.get("defaultDatasetId")
            if dataset_id:
                items = await Actor.apify_client.dataset(dataset_id).list_items()
                if items.items:
                    first_result = items.items[0]
                    start_url = first_result.get("metadata", {}).get("url")
                    if start_url:
                        Actor.log.info(f"Found starting URL: {start_url}")
                        return start_url
        
        Actor.log.warning("No URL found via search. Defaulting to Google.")
        return "https://www.google.com/search?q=" + user_task.replace(" ", "+")
        
    except Exception as e:
        Actor.log.error(f"Search failed: {e}. Defaulting to Google.")
        return "https://www.google.com/search?q=" + user_task.replace(" ", "+")

async def research_agent_get_html(user_task: str, max_steps: int = 10) -> Tuple[str, bytes]:
    """
    Agentic loop:
    1. Search for a good starting point.
    2. Lets the LLM decide actions to navigate/extract.
    3. Returns the final extracted HTML and screenshot.
    """
    scraper = WebScraperActor()
    
    # Dynamic start URL based on search
    start_url = await search_for_start_url(user_task)

    # initial page
    html = await scraper.goto(start_url)
    history: List[str] = []

    try:
        for step in range(1, max_steps + 1):
            Actor.log.info(f"=== STEP {step} ===")

            action = await llm_choose_action(html, history, user_task)
            history.append(action)
            Actor.log.info(f"Agent action: {action}")

            upper = action.upper().strip()

            if upper.startswith("NAVIGATE "):
                raw_url = action[len("NAVIGATE "):].strip()
                if not raw_url.startswith("http"):
                    # Attempt to handle relative paths blindly if we know the base, 
                    # but pure relative handling is hard without current URL context.
                    # For now, we assume the LLM sees the links and provides full or resolvable URLs.
                    # If it's a root relative path:
                    if raw_url.startswith("/") and scraper.page:
                        # naive reconstruct
                        base = "/".join(scraper.page.url.split("/")[:3]) # https://host
                        raw_url = base + raw_url
                
                Actor.log.info(f"Navigating to: {raw_url}")
                html = await scraper.goto(raw_url)
                continue

            if upper.startswith("CLICK "):
                selector = action[len("CLICK "):].strip()
                Actor.log.info(f"Clicking selector: {selector}")
                html = await scraper.click(selector)
                continue

            if "EXTRACT" in upper:
                Actor.log.info("Extracting current page HTML and screenshot...")
                html = await scraper.extract_html()
                screenshot_bytes = await scraper.screenshot_bytes()
                return html, screenshot_bytes

            if "FINISH" in upper:
                Actor.log.info("Agent indicated FINISH. Returning current HTML and a blank screenshot.")
                return html, b''

            # Fallback: unknown action
            Actor.log.warning("Unknown action or FINISH. Returning current HTML.")
            return html, b''

        Actor.log.warning("Max steps reached. Returning current HTML.")
        return html, b''

    finally:
        await scraper.close()

def summarize_requirements(html: str, user_task: str) -> BuildingCodeReport:
    """
    Takes the final HTML retrieved by the agent and returns
    a structured BuildingCodeReport using gpt-4o-mini.
    """
    html_snippet = html[:15000]  # keep under token limits

    system_prompt = """
You are an expert in building codes and zoning regulations.

You will be given:
- The user's task (e.g. "Find parking requirements for an ADU in Los Angeles").
- The HTML of a relevant building code page.

Your job:
- Identify the key code requirements relevant to the task.
- Summarise the requirements in clear, non-legal language.
- Extract generic code references (Section, Chapter, Table numbers).

You MUST:
- Fill the BuildingCodeReport schema.
- Provide concise requirement statements.
- List any important assumptions (e.g. jurisdiction, year of code).
"""

    user_prompt = f"""
User task:
{user_task}

HTML Content (truncated):
\"\"\"{html_snippet}\"\"\"
"""
    
    from apify import Configuration
    token = Configuration.get_global_configuration().token

    client = OpenAI(
        base_url="https://openrouter.apify.actor/api/v1",
        api_key="no-key-required-but-must-not-be-empty",
        default_headers={"Authorization": f"Bearer {token}"}
    )

    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=BuildingCodeReport,
        )
        return completion.choices[0].message.parsed
    except Exception as e:
        Actor.log.error(f"Error in summarization: {e}")
        return BuildingCodeReport(
            task=user_task,
            jurisdiction="Unknown",
            code_source="Error",
            assumptions=["Failed to summarize"],
            requirements=[]
        )

async def run_research_agent(user_task: str, max_steps: int = 15) -> BuildingCodeReport:
    """
    High-level entry:
    1) Run the research agent (Search -> Navigate -> Extract).
    2) Summarise extracted HTML into a BuildingCodeReport.
    """
    html, screenshot_data = await research_agent_get_html(user_task=user_task, max_steps=max_steps)
    report = summarize_requirements(html, user_task)
    return report
