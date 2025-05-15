from __future__ import annotations

from langchain_core.tools import tool
from schemas.state import CampaignState
import json

from typing import TYPE_CHECKING

# if TYPE_CHECKING:
from configs.llm_config import get_llm

@tool
def hashtag_generator(state: CampaignState) -> dict:
    """Generate relevant hashtags based on campaign theme, trends, and search results.
    
    Args:
        state: CampaignState with campaign_theme, trends, search_results.
        llm: ChatOpenAI instance for hashtag generation.
    
    Returns:
        Dict with 'hashtags' (List[str]) and 'messages' (List[dict]).
    """
    llm = get_llm()
    theme = state.campaign_theme
    trends = state.trends
    search_results = state.search_results

    # Extract context
    trend_keywords = [trend["keyword"] for trend in trends if "keyword" in trend]
    search_terms = []
    for result_set in search_results:
        if "term" in result_set:
            search_terms.append(result_set["term"])
        if "results" in result_set:
            search_terms.extend(item["title"] for item in result_set["results"][:3] if "title" in item)

    # Generate hashtags
    prompt = (
        f"Generate 5 relevant and trending hashtags for a campaign:\n"
        f"Campaign Theme: {theme}\n"
        f"Trend Keywords: {', '.join(trend_keywords)}\n"
        f"Search Terms: {', '.join(search_terms[:10])}\n"
        "Hashtags should be:\n"
        "1. Memorable and catchy\n"
        "2. Relevant to the theme\n"
        "3. Likely to trend\n"
        "4. Mix of broad and specific\n"
        "5. Not overused\n"
        "Return a JSON object with a 'hashtags' list of strings."
    )
    try:
        response = llm.invoke(
            [{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        hashtags = json.loads(response.content).get("hashtags", [])
        hashtags = [f"#{tag.lstrip('#')}" for tag in hashtags]  # Ensure # prefix
    except Exception as e:
        print(f"Error generating hashtags: {e}")
        words = theme.split()
        hashtags = ["#" + "".join(words), f"#{words[0]}Campaign"] if words else ["#Campaign"]
        state.messages.append({
            "role": "assistant",
            "content": f"Error generating hashtags: {e}. Using basic hashtags."
        })

    update_message = {
        "role": "assistant",
        "content": f"Generated hashtags for '{theme}': {', '.join(hashtags)}"
    }
    return {
        "hashtags": hashtags,
        "messages": state.messages + [update_message]
    }
