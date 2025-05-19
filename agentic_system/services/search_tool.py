from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from schemas.state import CampaignState, Message, Step, SearchItem, SearchResult
from typing import List
import os
from pydantic import BaseModel
import time
from dotenv import load_dotenv
# load_dotenv()

class SearchEngineInput(BaseModel):
    state: CampaignState

@tool(args_schema=SearchEngineInput)
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
            "messages": state.messages + [Message(role="assistant", content=error_msg)]
        }

    #✅ Extract search terms
    search_terms = [trend.keyword for trend in trends] # or [theme]
    # print(search_terms)
    
    search_results: List[SearchResult] = []
    # print(search_results)8

    tavily = TavilySearchResults(max_results=5, include_answer=True, include_raw_content=True)
    
    for term in search_terms:
        try:
            print(f"Searching for: {term}")
            results_raw = tavily.invoke(f"latest information about {term}")[:5] #it was set five here
            # print(results_raw[0]) #✅
            items = [SearchItem(**r) for r in results_raw]
            # print(type(items)) #✅
            # print(term)
            search_results.append(SearchResult(term=term, results=items))
            time.sleep(1)  # Avoid rate limits
        except Exception as e:
            print(f"Error searching for '{term}': {e}")
            search_results.append(SearchResult(term=term, error=str(e)))
            state.messages.append(Message(
                role="assistant",
                content=f"Error searching for '{term}': {e}"
            ))

    # print(search_results)

    update_message = Message(
        role="assistant",
        content=f"Gathered information on {', '.join(search_terms)} with {len(search_results)} result sets."
    )

    return {
        "search_results": search_results,
        "messages": state.messages + [update_message]
    }


"""
SearchItem(
    title='40 Sustainable Clothing Brands To Know in 2024 - The Trend Spotter', content='Discover some of the most popular eco-friendly',
    url='https://www.thetrendspotter.net/sustainable-clothing-brands/', 
    score=0.5726516
    )
"""