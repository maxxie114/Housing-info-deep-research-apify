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
    _instance = None
    _browser = None
    _playwright = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_browser(cls):
        async with cls._lock:
            if cls._playwright is None:
                cls._playwright = await async_playwright().start()
            if cls._browser is None:
                try:
                    cls._browser = await cls._playwright.chromium.launch(
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
            return cls._browser

    @classmethod
    async def close(cls):
        try:
            if cls._browser:
                await cls._browser.close()
        except: pass
        try:
            if cls._playwright:
                await cls._playwright.stop()
        except: pass
        cls._browser = None
        cls._playwright = None

    @staticmethod
    async def new_page():
        browser = await WebScraperActor.get_browser()
        # Create a new context for isolation if needed, or just new page
        ctx = await browser.new_context()
        page = await ctx.new_page()
        return page, ctx

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


async def perform_search_get_urls(user_task: str) -> List[str]:
    """
    Uses apify/rag-web-browser to search and returns the top 3 result URLs.
    """
    Actor.log.info(f"Searching for task: {user_task}")
    search_query = f"{user_task} building code official site"
    
    try:
        run = await Actor.call(
            "apify/rag-web-browser",
            run_input={
                "query": search_query,
                "maxResults": 3,
            },
            memory_mbytes=2048,
        )
        
        if not run: return []
        dataset_id = run.default_dataset_id
        if not dataset_id: return []

        items = await Actor.apify_client.dataset(dataset_id).list_items()
        urls = []
        for item in items.items:
            # rag-web-browser output format varies. Sometimes metadata.url, sometimes url.
            # but usually it actually navigates. Wait, rag-web-browser without markdown
            # just returns results if we ask it to? 
            # Actually, standard rag-web-browser usage scrapes content.
            # If we just want URLs, we might fish from metadata.
            url = item.get("metadata", {}).get("url")
            if url: urls.append(url)
            
        return urls
    except Exception as e:
        Actor.log.error(f"Search failed: {e}")
        return []

async def run_single_agent_tab(url: str, user_task: str, max_steps: int = 15) -> str:
    """
    Spawns a new page, navigates to the start URL, and runs the ReAct agent loop.
    Returns the extracted Markdown/HTML content.
    """
    Actor.log.info(f"Starting agent tab for URL: {url}")
    page = None
    context = None
    try:
        page, context = await WebScraperActor.new_page()
        
        # Initial navigation
        try:
            await page.goto(url, wait_until="load", timeout=60000)
            await page.wait_for_timeout(2000)
        except Exception as e:
            Actor.log.error(f"Failed to load start URL {url}: {e}")
            return ""

        history: List[str] = []
        html = await page.content()

        for step in range(1, max_steps + 1):
             # Decide action
            action = await llm_choose_action(html, history, user_task)
            history.append(action)
            Actor.log.info(f"[{url}] Agent Step {step} Action: {action}")
            
            upper = action.upper().strip()

            if upper.startswith("NAVIGATE "):
                raw_url = action[len("NAVIGATE "):].strip()
                # Relative URL handling
                if not raw_url.startswith("http") and not raw_url.startswith("www"):
                     if raw_url.startswith("/"):
                         # simplistic join
                         base = "/".join(page.url.split("/")[:3])
                         raw_url = base + raw_url
                     else:
                         current_dir = "/".join(page.url.split("/")[:-1])
                         raw_url = current_dir + "/" + raw_url
                
                try:
                    await page.goto(raw_url, wait_until="load", timeout=30000)
                    await page.wait_for_timeout(1000)
                    html = await page.content()
                except Exception as e:
                    Actor.log.warning(f"[{url}] Nav failed: {e}")
                continue

            if upper.startswith("CLICK "):
                selector = action[len("CLICK "):].strip()
                try:
                    await page.click(selector, timeout=5000)
                    await page.wait_for_timeout(1000)
                    html = await page.content()
                except Exception as e:
                    Actor.log.warning(f"[{url}] Click failed: {e}")
                continue

            if "EXTRACT" in upper:
                Actor.log.info(f"[{url}] EXTRACT issued. Capturing content.")
                # We could try to convert to markdown here if we want, or just return HTML.
                # For consistency with parallel search, let's keep HTML for now and let summarizer handle it? 
                # Actually, the new summarizer expects Markdown-ish content.
                # Let's return the HTML; the summarizer handles HTML snippet or Markdown.
                return f"--- START SOURCE: {page.url} ---\n{html}\n--- END SOURCE ---\n"

            if "FINISH" in upper:
                Actor.log.info(f"[{url}] FINISH issued.")
                # Return what we have currently
                return f"--- START SOURCE: {page.url} ---\n{html}\n--- END SOURCE ---\n"

        # Max steps
        Actor.log.warning(f"[{url}] Max steps reached.")
        return f"--- START SOURCE: {page.url} ---\n{html}\n--- END SOURCE ---\n"

    except Exception as e:
        Actor.log.error(f"[{url}] Agent tab crashed: {e}")
        return ""
    finally:
        if page: await page.close()
        if context: await context.close()

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
    - The Markdown content of multiple relevant building code pages (concatenated).

    Your job:
    - Identify the key code requirements relevant to the task.
    - Summarise the requirements in clear, non-legal language.
    - Extract generic code references (Section, Chapter, Table numbers) and Source URLs.
    
    You MUST:
    - Fill the BuildingCodeReport schema.
    - Provide concise requirement statements.
    - List any important assumptions (e.g. jurisdiction, year of code).
    """

    user_prompt = f"""
    User task:
    {user_task}
    
    Content (Markdown):
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
    1) Search to get candidate URLs.
    2) Run multiple agent tabs in parallel to navigate/extract.
    3) Summarise aggregated content.
    """
    # 1. Search (fast)
    urls = await perform_search_get_urls(user_task)
    if not urls:
         # Fallback search if Rag fails?
         urls = ["https://www.google.com/search?q=" + user_task.replace(" ", "+")]

    # Limit to top 3 to avoid overloading browser memory
    urls = urls[:3]
    Actor.log.info(f"Parallel Agents launching for: {urls}")

    # 2. Run Parallel Agents
    tasks = [run_single_agent_tab(url, user_task, max_steps) for url in urls]
    results = await asyncio.gather(*tasks)
    
    # Filter empty results
    valid_results = [r for r in results if r]
    aggregated_markdown = "\n\n".join(valid_results)

    if not aggregated_markdown:
        Actor.log.warning("All parallel agents failed to retrieve content.")
        return BuildingCodeReport(
            task=user_task,
            jurisdiction="Unknown",
            code_source="All Agents Failed",
            assumptions=["Could not retrieve content via parallel deep agents."],
            requirements=[]
        )

    # 3. Summarize
    Actor.log.info("Aggregated content retrieved. Summarizing...")
    report = summarize_requirements(aggregated_markdown, user_task)
    
    # Cleanup browser
    await WebScraperActor.close()
    
    return report
