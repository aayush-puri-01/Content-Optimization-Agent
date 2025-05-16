from __future__ import annotations

from langchain_core.tools import tool
from schemas.state import CampaignState, Message, Step, SearchResult, SearchItem
import json
from pydantic import BaseModel

from typing import TYPE_CHECKING

# if TYPE_CHECKING:
from configs.llm_config import get_llm

class HashtagGeneratorInput(BaseModel):
    state: CampaignState

@tool(args_schema=HashtagGeneratorInput)
def hashtag_generator(state: CampaignState) -> dict:
    """Generate relevant hashtags based on campaign theme, trends, and search results.
    
    Args:
        state: CampaignState with campaign_theme, trends, search_results.
    
    Returns:
        Dict with 'hashtags' (List[str]) and 'messages' (List[dict]).
    """
    llm = get_llm()
    theme = state.campaign_theme
    trends = state.trends
    search_results = state.search_results

    # Extract context
    trend_keywords = [trend.keyword for trend in trends]
    search_terms = []
    for result_set in search_results:
        #result_set is of the type SearchResult
        if result_set.term:
            search_terms.append(result_set.term)
        if result_set.results:
            search_terms.extend(item.title for item in result_set.results[:3])

    # for i in range(5):
    #     print(search_terms[i])
    #     print(type(search_terms[i]))

    # print(f"Trend Keywords: {', '.join(trend_keywords)}\n")


    # Generate hashtags
    prompt = (
        f"Generate 5 relevant and trending hashtags for a campaign:\n"
        f"Campaign Theme: {theme}\n"
        f"Trend Keywords: {', '.join(trend_keywords)}\n"
        f"Search Terms: {', '.join(search_terms)}\n"
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
            [{"role": "system", "content": "Do not make a tool call if theme, trend keywords and search terms are provided in the context from the user."},{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        print("----------------LLM HAS RESPONDED----------------")
        print(response)
        temp_json_load = json.loads(response.content)
        print(temp_json_load)
        hashtags = json.loads(response.content).get("hashtags", [])
        print("********hashtags populated*************")
        print(hashtags)
        hashtags = [f"#{tag.lstrip('#')}" for tag in hashtags]
        print("********hashtags beautified*************")
        print(hashtags)  # Ensure # prefix
    except Exception as e:
        print(f"Error generating hashtags: {e}")
        words = theme.split()
        hashtags = ["#" + "".join(words), f"#{words[0]}Campaign"] if words else ["#Campaign"]
        state.messages.append(Message(
            role="assistant",
            content=f"Error generating hashtags: {e}. Using basic hashtags."
        ))

    update_message = Message(
        role="assistant",
        content=f"Generated hashtags for '{theme}': {', '.join(hashtags)}"
    )

    return {
        "hashtags": hashtags,
        "messages": state.messages + [update_message]
    }
