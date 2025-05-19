from __future__ import annotations


from configs.llm_config import get_llm

from schemas.state import CampaignState, Message, Step
import json
from dotenv import load_dotenv
load_dotenv()

def llm_router(state: CampaignState) -> dict:
    """Dynamically route to the next tool or end, using steps in state."""
    llm = get_llm()
    if not state.current_step:
        print("Current step not found so extracting parameters")
        # Initial invocation: extract parameters and generate steps
        user_input = state.messages[0].content
        prompt = (
            f"Extract from '{user_input}':\n"
            "1. campaign_theme (main subject, required)\n"
            "2. target_audience (default: 'general audience')\n"
            "3. duration_seconds (default: 60)\n"
            "4. tone (e.g., humorous, professional, default: 'neutral')\n"
            "Return a JSON object with 'parameters' and 'steps' fields.\n"
            "Parameters: include the extracted fields.\n"
            "Steps: a list of steps, each with 'step' (tool name) based on the user input.\n"
            "Available tools: trend_analyzer, search_engine, hashtag_generator, script_generator.\n"
            "It is to be noted that Hashtags generation and Script generation need to be performed only after trend analysis and web search.\n"
            "Example: for a full campaign, include all tools in order; for research, include trend_analyzer and search_engine."
        )
        try:
            response = llm.invoke([{"role": "user", "content": prompt}], response_format={"type": "json_object"})
            #response_fromat in json string only works with gpt-40-mini and some snapshots, for other models, response_format is a string and not a json string
            # print(response) #✅ correct parsing of parameters
            result = json.loads(response.content) 
            # print(result) #✅ correct loading of json
            params = result.get("parameters", {})
            steps = [
                Step(step=s["step"], executed=False)
                for s in result.get("steps", [])
                if s.get("step") in ["trend_analyzer", "search_engine", "hashtag_generator", "script_generator"]
            ]
            print(steps) #✅ steps found
            if not params.get("campaign_theme"):
                return {
                    "messages": state.messages + [Message(role="assistant", content="Please provide a campaign theme.")],
                    "current_step": "END"
                }
            state_updates = {
                "campaign_theme": params.get("campaign_theme", ""),
                "target_audience": params.get("target_audience", "general audience"),
                "duration_seconds": params.get("duration_seconds", 60),
                "tone": params.get("tone", "neutral"),
                "steps": steps,
                "messages": state.messages + [Message(role="system", content=f"Parameters: {params}, Steps: {steps}")],
                "current_step": steps[0].step if steps else "END"
            }
            return state_updates
        except Exception as e:
            print(f"Error extracting parameters or steps: {e}")
            return {
                "messages": state.messages + [Message(role="assistant", content=f"Error initializing workflow: {e}")],
                "current_step": "END"
            }

    # After a tool: mark current step as executed and find next step
    steps = state.steps
    # Mark current step as executed
    for step in steps:
        if step.step == state.current_step:
            step.executed = True

    # Find next unexecuted step
    next_step = next((s.step for s in steps if not s.executed), None)
    if next_step:
        return {
            "steps": steps,
            "current_step": next_step
        }
    
    print("\n\nAll planned steps executed. Ending workflow.")
    return {
        "steps": steps,
        "current_step": "END",
        "messages": state.messages + [Message(role="system", content="All planned steps have been executed. Workflow complete.")]
    }


    # # No unexecuted steps: ask LLM if workflow is complete
    # prompt = (
    #     f"Current state:\n"
    #     f"Campaign Theme: {state.campaign_theme}\n"
    #     f"Target Audience: {state.target_audience}\n"
    #     f"Tone: {state.tone}\n"
    #     f"Steps Executed: {', '.join(s.step for s in steps if s.executed)}\n"
    #     f"Trends: {len(state.trends)} found\n"
    #     f"Search Results: {len(state.search_results)} sets\n"
    #     f"Hashtags: {len(state.hashtags)} generated\n"
    #     f"Script: {'generated' if state.script else 'not generated'}\n"
    #     f"User Input: {state.messages[0].content}\n"
    #     "All planned steps are executed. Decide if the workflow is complete or if additional tools are needed.\n"
    #     # "Hashtags generation and Script generation need to be performed only after trend analysis and web search.\n"
    #     "Available tools: trend_analyzer, search_engine, hashtag_generator, script_generator.\n"
    #     "Return a JSON object with 'current_step' and 'new_steps' as keys. 'current_step' is a tool name or END and 'new_steps' is a list of new steps, if any)."
    # )

    # # return {
    # #     "steps": steps,
    # #     "current_step": next_step
    # # } 

    # try:
    #     response = llm.invoke([{"role": "user", "content": prompt}], response_format={"type": "json_object"})
    #     result = json.loads(response.content)
    #     new_steps = [
    #         Step(step=s, executed=False)
    #         for s in result.get("new_steps", [])
    #         if s in ["trend_analyzer", "search_engine", "hashtag_generator", "script_generator"]
    #     ]
    #     steps.extend(new_steps)
    #     next_step = result.get("current_step", "END")
    #     if next_step not in ["trend_analyzer", "search_engine", "hashtag_generator", "script_generator", "END"]:
    #         next_step = "END"
    #     return {
    #         "steps": steps,
    #         "current_step": next_step
    #     }
    # except Exception as e:
    #     print(f"Error in dynamic routing: {e}")
    #     return {
    #         "steps": steps,
    #         "messages": state.messages + [Message(role="assistant", content=f"Error determining next step: {e}")],
    #         "current_step": "END"
    #     }