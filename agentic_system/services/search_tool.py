from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from schemas.state import CampaignState
import os
import time
from dotenv import load_dotenv
load_dotenv()


@tool
def search_engine(state: CampaignState) -> dict:
    """Search for information on trends or campaign theme using Tavily.
    
    Args:
        state: CampaignState with trends and campaign_theme.
    
    Returns:
        Dict with 'search_results' (List[dict]) and 'messages' (List[dict]).
    """
    trends = state.trends
    theme = state.campaign_theme
    tavily_api_key = os.environ.get("TAVILY_API_KEY")
    
    if not tavily_api_key:
        error_msg = "TAVILY_API_KEY not set. Cannot perform search."
        print(error_msg)
        return {
            "search_results": [],
            "messages": state.messages + [{"role": "assistant", "content": error_msg}]
        }

    # Extract search terms
    search_terms = [trend["keyword"] for trend in trends if "keyword" in trend] or [theme]
    
    search_results = []
    tavily = TavilySearchResults(max_results=5, include_answer=True, include_raw_content=True)
    
    for term in search_terms:
        try:
            print(f"Searching for: {term}")
            results = tavily.invoke(f"latest information about {term}")
            search_results.append({"term": term, "results": results[:5]})
            time.sleep(1)  # Avoid rate limits
        except Exception as e:
            print(f"Error searching for '{term}': {e}")
            search_results.append({"term": term, "error": str(e)})
            state.messages.append({
                "role": "assistant",
                "content": f"Error searching for '{term}': {e}"
            })

    update_message = {
        "role": "assistant",
        "content": f"Gathered information on {', '.join(search_terms)} with {len(search_results)} result sets."
    }
    return {
        "search_results": search_results,
        "messages": state.messages + [update_message]
    }