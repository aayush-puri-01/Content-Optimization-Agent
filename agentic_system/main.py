from __future__ import annotations

from typing import TYPE_CHECKING

from langgraph.graph import StateGraph, END
from schemas.state import CampaignState

# if TYPE_CHECKING:
from services.llm_node import llm_router
from services.trend_tool import trend_analyzer
from services.search_tool import search_engine
from services.hashtag_gen import hashtag_generator
from services.script_tool import script_generator

from configs.llm_config import get_llm


def format_response(state: CampaignState) -> str:
    """Format a detailed response."""
    details = []
    if state["trends"]:
        trends = ", ".join(t["keyword"] for t in state.trends[:3])
        details.append(f"analyzed trends related to {trends}")
    if state["hashtags"]:
        hashtags = ", ".join(state["hashtags"][:3])
        details.append(f"generated hashtags including {hashtags}")
    if state["script"]:
        script_preview = state["script"][:100] + "..." if len(state["script"]) > 100 else state["script"]
        details.append(f"created a script: {script_preview}")
        if state["production_ideas"]:
            ideas = ", ".join(state["production_ideas"][:2])
            details.append(f"production ideas: {ideas}")
    if state["script"]:
        executed = ", ".join(s["step"] for s in state["steps"] if s["executed"])
        pending = ", ".join(s["step"] for s in state["steps"] if not s["executed"])
        details.append(f"executed steps: {executed}")
        if pending:
            details.append(f"pending steps: {pending}")

    next_steps = ""
    if state["current_step"] in ["search_engine", "trend_analyzer"]:
        next_steps = " Would you like to continue with the next steps?"
    elif state["current_step"] == "script_generator":
        next_steps = " Let me know if you'd like any revisions to the script."

    response = f"I've processed the campaign for '{state['campaign_theme']}'."
    if details:
        response += " I've " + ", and ".join(details) + "." + next_steps
    if state["script"]:
        response += f"\n\n--- SCRIPT ---\n\n{state['script']}"
    return response

# Initialize LLM
llm = get_llm()

# Nodes
def trend_analyzer_node(state: CampaignState) -> CampaignState:
    result = trend_analyzer.invoke(state)
    return {
        "trends": result["trends"],
        "messages": result["messages"],
        "current_step": "trend_analyzer"
    }

def search_engine_node(state: CampaignState) -> CampaignState:
    result = search_engine.invoke(state)
    return {
        "search_results": result["search_results"],
        "messages": result["messages"],
        "current_step": "search_engine"
    }

def hashtag_generator_node(state: CampaignState) -> CampaignState:
    result = hashtag_generator.invoke(state)
    return {
        "hashtags": result["hashtags"],
        "messages": result["messages"],
        "current_step": "hashtag_generator"
    }

def script_generator_node(state: CampaignState) -> CampaignState:
    result = script_generator.invoke(state)
    return {
        "script": result["script"],
        "production_ideas": result["production_ideas"],
        "messages": result["messages"],
        "current_step": "script_generator"
    }

# Build graph
workflow = StateGraph(CampaignState)
workflow.add_node("llm_router", llm_router)
workflow.add_node("trend_analyzer", trend_analyzer_node)
workflow.add_node("search_engine", search_engine_node)
workflow.add_node("hashtag_generator", hashtag_generator_node)
workflow.add_node("script_generator", script_generator_node)

# Edges
workflow.add_conditional_edges(
    "llm_router",
    lambda state: state.current_step,
    {
        "trend_analyzer": "trend_analyzer",
        "search_engine": "search_engine",
        "hashtag_generator": "hashtag_generator",
        "script_generator": "script_generator",
        "END": END
    }
)
workflow.add_edge("trend_analyzer", "llm_router")
workflow.add_edge("search_engine", "llm_router")
workflow.add_edge("hashtag_generator", "llm_router")
workflow.add_edge("script_generator", "llm_router")
workflow.set_entry_point("llm_router")

# Compile graph
graph = workflow.compile()

# from IPython.display import Image, display
# try:
#     display(Image(graph.get_graph().draw_mermaid_png()))
# except Exception:
#     pass 

# Example invocation
if __name__ == "__main__":
    initial_state = CampaignState(
        campaign_theme="",
        target_audience="",
        duration_seconds=60,
        tone="",
        steps=[],
        trends=[],
        search_results=[],
        hashtags=[],
        script="",
        production_ideas=[],
        messages=[{"role": "user", "content": "Create a complete campaign about sustainable fashion for Gen Z with a humorous tone"}],
        current_step=""
    )
    result = graph.invoke(initial_state)
    print(format_response(result))