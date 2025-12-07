
from typing import Literal, List, Dict, Any

# Assume apify_client and tavily_client are initialized elsewhere in the app
apify_client = None
tavily_client = None


def create_search_tool(api_url: str = ""):
    """Compatibility wrapper to return the ncc_bca_search tool."""
    return ncc_bca_search

def ncc_bca_search(
    query: str,
    max_results: int = 10,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = True,
) -> List[Dict[str, Any]]:
    """
    Search for NCC/BCA building code information, clauses, and DTS requirements.
    
    This tool is optimized for retrieving Australian building code information from:
    - ABCB.gov.au (Australian Building Codes Board official site)
    - NCC Online documentation
    - State-specific building regulation sites
    - Industry compliance guides and technical resources
    
    Args:
        query: Search query for NCC/BCA clauses, DTS provisions, or building code requirements
        max_results: Maximum number of results to return (default 10 for comprehensive coverage)
        topic: Search topic type (use 'general' for building codes)
        include_raw_content: Include full content from sources (True for detailed clause text)
    
    Returns:
        List of search results with URLs, content, and titles
    
    Example queries:
        - "NCC 2022 Class 2 fire resistance requirements"
        - "BCA Deemed-to-Satisfy stairway dimensions Part D3"
        - "NCC Volume 1 Part C fire safety egress requirements"
        - "Accessible toilet DTS provisions NCC Part F2.4"
    """
    # Enhance query with NCC/BCA context if not already specified
    ncc_keywords = ["NCC", "BCA", "Building Code", "ABCB", "Deemed-to-Satisfy", "DTS"]
    if not any(keyword.lower() in query.lower() for keyword in ncc_keywords):
        query = f"Australian NCC BCA building code {query}"
    
    if apify_client:
        try:
            # actor-runs/rH0FaDlBhXMB52MGz matches actor 5njSjIbSndERjFLTt (Tavily wrapper on Apify)
            run_input = {
                "query": query,
                "max_results": max_results,
                "topic": topic,
                "include_raw_content": include_raw_content
            }
            print(f"Running Apify Actor for NCC/BCA query: {query}")
            run = apify_client.actor("5njSjIbSndERjFLTt").call(run_input=run_input)
            # Fetch results from the default dataset of the run
            dataset_items = apify_client.dataset(run["defaultDatasetId"]).list_items().items
            return dataset_items
        except Exception as e:
            print(f"Apify search failed: {e}")
            return [{
                "url": "https://ncc.abcb.gov.au/error",
                "content": f"NCC/BCA search failed: {e}",
                "title": "Search Error"
            }]

    if tavily_client:
        try:
            search_docs = tavily_client.search(
                query,
                max_results=max_results,
                include_raw_content=include_raw_content,
                topic=topic,
            )
            return search_docs
        except Exception as e:
            print(f"Tavily search failed: {e}")
            return [{
                "url": "https://ncc.abcb.gov.au/error",
                "content": f"Search execution failed: {e}",
                "title": "Search Error"
            }]

    # Mock fallback with building code context
    print(f"Mocking NCC/BCA search for query: {query}")
    return [{
        "url": "https://ncc.abcb.gov.au/mock-clause",
        "content": f"Mock NCC/BCA search result for: {query}. No valid search API key found. In production, this would retrieve actual building code clauses and DTS requirements from official ABCB sources.",
        "title": f"Mock NCC/BCA Result for {query}"
    }]

# Alias for backward compatibility
internet_search = ncc_bca_search
