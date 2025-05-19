from __future__ import annotations

from typing import TYPE_CHECKING

from langchain_core.tools import tool
from schemas.state import CampaignState, Message, Step
from serpapi.google_search import GoogleSearch
import os
import time
import json
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()


from configs.llm_config import get_llm

class TrendAnalyzerInput(BaseModel):
    state: CampaignState

@tool(args_schema=TrendAnalyzerInput)
def trend_analyzer(state: CampaignState) -> dict:
    """Fetch trends related to the campaign theme using SerpAPI and LLM-generated keywords.
    
    Args:
        state: CampaignState containing campaign_theme and other fields.
    
    Returns:
        Dict with 'trends' (List[dict]) and 'messages' (List[dict]) for state update.
    """
    llm = get_llm()
    theme = state.campaign_theme
    serpapi_key = os.environ.get("NEW_SERPAPI_KEY")
    if not serpapi_key:
        error_msg = "SERPAPI_KEY not set. Cannot fetch trends."
        print(error_msg)
        return {
            "trends": [{"keyword": theme, "error": "Missing API key"}],
            "messages": state.messages + [Message(role="assistant", content=error_msg)]
        }

    # Generate keywords using LLM with structured output
    prompt = (
        f"Based on the campaign theme '{theme}', generate 3-5 relevant keywords or phrases "
        "for searching trends. Return a JSON object with a 'keywords' list of strings."
    )
    try:
        response = llm.invoke(
            [{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        # print(response)
        keywords = json.loads(response.content).get("keywords", [theme])
    except Exception as e:
        print(f"Error generating keywords: {e}")
        keywords = [theme]
        state.messages.append({
            "role": "assistant",
            "content": f"Failed to generate keywords for '{theme}'. Using theme as keyword."
        })

    # Fetch trends via SerpAPI
    trends_data = []
    for keyword in keywords[:5]:  # Limit to 5 keywords
        try:
            params = {
                "engine": "google_light",
                "q": keyword,
                "location": "United States",
                "api_key": serpapi_key
            }

            search = GoogleSearch(params)

            results = search.get_dict()

            trend_info = {"keyword": keyword, "relevance": 100}
            
            # Extract organic results
            if "organic_results" in results and results["organic_results"]:
                top_results = results["organic_results"][:3]
                trend_info["related_content"] = [
                    {"title": r["title"], "snippet": r["snippet"]}
                    for r in top_results if "title" in r and "snippet" in r
                ]
                
                # Extract related queries from sitelinks
                related_queries = []
                if top_results and "sitelinks" in top_results[0] and "inline" in top_results[0]["sitelinks"]:
                    related_queries = [
                        s["title"] for s in top_results[0]["sitelinks"]["inline"][:3] if "title" in s
                    ]
                trend_info["related_queries"] = related_queries


            # Trend direction heuristic
            trend_direction = "neutral"
            if "organic_results" in results:
                mention_count = sum(
                    1 for r in results["organic_results"][:5]
                    if "snippet" in r and keyword.lower() in r["snippet"].lower()
                )
                trend_direction = "increasing" if mention_count > 3 else "decreasing" if mention_count < 2 else "neutral"
            trend_info["trend_direction"] = trend_direction

            trends_data.append(trend_info)
            time.sleep(1)  # Avoid rate limits
        except Exception as e:
            print(f"Error processing keyword '{keyword}': {e}")
            trends_data.append({"keyword": keyword, "error": str(e)})
            # state.messages.append({
            #     "role": "assistant",
            #     "content": f"Error fetching trends for '{keyword}': {e}"
            # })
            state.messages.append(Message(
                role="assistant",
                content=f"Error fetching trends for '{keyword}': {e}"
            ))

    # Update state
    update_message = Message(
        role="assistant",
        content=f"Analyzed trends for '{theme}': {', '.join(t['keyword'] for t in trends_data)}"
    )
    return {
        "trends": trends_data,
        "messages": state.messages + [update_message]
    }