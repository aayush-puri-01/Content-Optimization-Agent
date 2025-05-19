from __future__ import annotations

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from schemas.state import CampaignState, Message, Step, SearchItem, SearchResult
import json
from pydantic import BaseModel
from typing import TYPE_CHECKING

# if TYPE_CHECKING:
from configs.llm_config import get_llm

class ScriptGeneratorInput(BaseModel):
    state: CampaignState

@tool(args_schema=ScriptGeneratorInput)
def script_generator(state: CampaignState) -> dict:
    """Generate a script for the campaign based on collected data.
    
    Args:
        state: CampaignState with campaign_theme, trends, search_results, hashtags, target_audience, duration_seconds.
    
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
    trend_keywords = [t.keyword for t in trends]
    print(trend_keywords)
    search_terms = [r.term for r in search_results]
    print(search_terms)
    hashtags_text = ", ".join(hashtags) if hashtags else "None"
    print(hashtags_text)

    # Generate script
    prompt = (
        f"Carry all the steps without calling any tools that you have access to:\n\n"
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
        "Return a JSON object with 'script' as a string and 'production_ideas' as a list of strings."
    )
    try:
        response = llm.invoke(
            [{"role": "system", "content": "You are a helpful assistant, Do not make any tool call."}, {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        print("_____HASH INFO: LLM RESPONDED_____________")
        print(response)
        result = json.loads(response.content)
        print("_____HASH INFO: json content loaded_____________")
        print(result)
        script = result.get("script", "")
        print("\nThis is the script\n\n")
        print(script)
        production_ideas = result.get("production_ideas", [])
        if not script:
            raise ValueError("Empty script generated")
        
    except Exception as e:
        print(f"Error generating script: {e}")
        script = f"Script for {theme} campaign (fallback due to error)."
        production_ideas = ["Use vibrant visuals", "Highlight key product moments"]
        state.messages.append(Message(
            role="assistant",
            content=f"Error generating script: {e}. Using fallback script."
        ))


    update_message = Message(
        role="assistant",
        content=f"Generated a {tone} script for '{theme}' campaign."
    )

    return {
        "script": script,
        "production_ideas": production_ideas,
        "messages": state.messages + [update_message]
    }