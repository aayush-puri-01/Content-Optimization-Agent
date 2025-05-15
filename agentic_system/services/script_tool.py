from __future__ import annotations

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from schemas.state import CampaignState
import json

from typing import TYPE_CHECKING

# if TYPE_CHECKING:
from configs.llm_config import get_llm

@tool
def script_generator(state: CampaignState) -> dict:
    """Generate a campaign script based on collected data.
    
    Args:
        state: CampaignState with campaign_theme, trends, search_results, hashtags, target_audience, duration_seconds, tone.
        llm: ChatOpenAI instance for script generation.
    
    Returns:
        Dict with 'script' (str), 'production_ideas' (List[str]), and 'messages' (List[dict]).
    """
    llm = get_llm()
    theme = state.campaign_theme
    trends = state.trends
    search_results = state.search_results
    hashtags = state.hashtags
    audience = state.target_audience
    duration = state.duration_seconds
    tone = state.tone

    # Summarize context
    trend_keywords = [t["keyword"] for t in trends if "keyword" in t]
    search_terms = [r["term"] for r in search_results if "term" in r]
    hashtags_text = ", ".join(hashtags) if hashtags else "None"

    # Generate script
    prompt = (
        f"Create an engaging {duration}-second campaign script:\n"
        f"Campaign Theme: {theme}\n"
        f"Target Audience: {audience}\n"
        f"Tone: {tone}\n"
        f"Trends: {', '.join(trend_keywords) if trend_keywords else 'None'}\n"
        f"Search Insights: {', '.join(search_terms) if search_terms else 'None'}\n"
        f"Hashtags: {hashtags_text}\n"
        "Include:\n"
        "1. Engaging hook\n"
        "2. Persuasive messaging aligned with theme\n"
        "3. Strong call to action\n"
        "4. Tone suitable for audience\n"
        "5. Timing for duration\n"
        "Also provide 2 production ideas (e.g., visuals, settings).\n"
        "Return JSON with 'script' (string) and 'production_ideas' (list of strings)."
    )
    try:
        response = llm.invoke(
            [{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        result = json.loads(response.content)
        script = result.get("script", "")
        production_ideas = result.get("production_ideas", [])
        if not script:
            raise ValueError("Empty script generated")
    except Exception as e:
        print(f"Error generating script: {e}")
        script = f"Script for {theme} campaign (fallback due to error)."
        production_ideas = "Use vibrant visuals"
        state.messages.append({
            "role": "assistant",
            "content": f"Error generating script: {e}. Using fallback script."
        })

    update_message = {
        "role": "assistant",
        "content": f"Generated a {tone} script for '{theme}' campaign."
    }
    return {
        "script": script,
        "production_ideas": production_ideas,
        "messages": state.messages + [update_message]
    }