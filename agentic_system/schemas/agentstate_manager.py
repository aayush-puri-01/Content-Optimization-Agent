# # campaign_agent.py
# from __future__ import annotations
# import os
# import json

# from typing import Dict, Any, List, Optional, TypedDict, TYPE_CHECKING

# from openai import OpenAI

# if TYPE_CHECKING:
#     from services.toolclass import BaseTool
#     from services.llm_node import initialize_chat_model
#     from services.trend_tool import TrendAnalyzer
#     from services.search_tool import SearchEngine
#     from services.hashtag_gen import HashtagGenerator
#     from services.script_tool import ScriptGenerator

        

# class CampaignAgent:
#     """Main agent class that orchestrates tools and processes user requests"""
    
#     def __init__(self):
#         # Initialize OpenAI client
#         self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
#         # Initialize state
#         self.state = {
#             "campaign_theme": None,
#             "target_audience": None,
#             "duration_seconds": 30,  # Default duration
#             "trends": [],
#             "search_results": [],
#             "hashtags": [],
#             "script": None,
#             "messages": [],
#             "current_step": None,
#             "next": None
#         }
        
#         # Initialize tools
#         self.tools = {
#             "trend_analyzer": TrendAnalyzer(self.client),
#             "search_engine": SearchEngine(),
#             "hashtag_generator": HashtagGenerator(self.client),
#             "script_generator": ScriptGenerator(self.client)
#         }
        
#         # Define the workflow sequences
#         self.workflows = {
#             "complete": ["trend_analyzer", "search_engine", "hashtag_generator", "script_generator"],
#             "research_only": ["trend_analyzer", "search_engine"],
#             "script_only": ["script_generator"]
#         }
    
#     def _determine_workflow(self, user_input: str) -> str:
#         """Determine which workflow to use based on user input"""
#         # Ask the LLM to help determine the workflow
#         prompt = f"""
#         Based on the following user request, determine which workflow is most appropriate:
#         "{user_input}"
        
#         Choose one of the following workflows:
#         1. "complete" - Full campaign process including trend analysis, search, hashtag generation, and script creation
#         2. "research_only" - Only perform trend analysis and search without creating content
#         3. "script_only" - Jump straight to script generation (only if enough information is already available)
        
#         Return only the workflow name without explanation.
#         """
        
#         try:
#             temp_state = {
#                 "messages": [{
#                     "role": "user",
#                     "content": prompt
#                 }]
#             }

#             callback_function = initialize_chat_model()
#             response = callback_function(temp_state)
            

#             # response = self.client.chat.completions.create(
#             #     model="gpt-4o-mini",
#             #     messages=[{"role": "user", "content": prompt}],
#             #     temperature=0.3,
#             #     max_tokens=20
#             # )
            
#             # workflow = response.choices[0].message.content.strip().lower()
#             workflow = response["messages"][-1]["content"].strip().lower()
            
#             # Validate workflow name
#             if workflow in self.workflows:
#                 return workflow
            
#             # If invalid, default to complete workflow
#             return "complete"
            
#         except Exception as e:
#             print(f"Error determining workflow: {str(e)}")
#             return "complete"  # Default to complete workflow
    
#     def _extract_parameters(self, user_input: str) -> Dict[str, Any]:
#         """Extract key parameters from user input using LLM"""
#         prompt = f"""
#         Extract the following parameters from the user request:
#         "{user_input}"
        
#         Parameters to extract:
#         1. campaign_theme - The main subject or focus of the campaign
#         2. target_audience - Who the campaign is targeting (default: "general audience")
#         3. duration_seconds - How long the script should be in seconds (default: 60)
        
#         Return the parameters as a JSON object. If a parameter is not mentioned, omit it.
#         """
        
#         try:
#             # response = self.client.chat.completions.create(
#             #     model="gpt-4o-mini",
#             #     messages=[{"role": "user", "content": prompt}],
#             #     temperature=0.3,
#             #     response_format={"type": "json_object"}
#             # )
#             temp_state = {
#                 "messages": [{
#                     "role": "user",
#                     "content": prompt
#                 }]
#             }

#             callback_function = initialize_chat_model()
#             response = callback_function(temp_state)
            
#             parameters = json.loads(response["messages"][-1]["content"])
#             return parameters
            
#         except Exception as e:
#             print(f"Error extracting parameters: {str(e)}")
            
#             # Try to extract campaign theme directly if JSON parsing fails
#             if "campaign" in user_input and "about" in user_input:
#                 start_idx = user_input.find("about") + 5
#                 campaign_theme = user_input[start_idx:].strip().split(".")[0]
#                 return {"campaign_theme": campaign_theme}
            
#             return {}  # Return empty dict if extraction fails
    
#     def _update_state(self, updates: Dict[str, Any]) -> None:
#         """Update the agent state with new values"""
#         for key, value in updates.items():
#             if key in self.state:
#                 self.state[key] = value
    
#     def _execute_next_tool(self) -> Dict[str, Any]:
#         """Execute the next tool in the workflow"""
#         current_tool_name = self.state.get("next")
        
#         if not current_tool_name or current_tool_name not in self.tools:
#             return {"error": f"Invalid next tool: {current_tool_name}"}
        
#         # Update current step
#         self.state["current_step"] = current_tool_name
        
#         # Get the tool
#         tool = self.tools[current_tool_name]
        
#         # Execute the tool with the current state
#         result = tool.execute(self.state)
        
#         # Update state with tool results
#         self._update_state(result)
        
#         return result
    
#     def process_request(self, user_input: str) -> str:
#         """Process a user request and return a response"""
#         # Add user message to conversation history
#         self.state["messages"].append({"role": "user", "content": user_input})
        
#         # Extract parameters from user input
#         parameters = self._extract_parameters(user_input)
#         self._update_state(parameters)
        
#         # Ensure we have a campaign theme
#         if not self.state.get("campaign_theme"):
#             response = "I need a campaign theme to proceed. Please provide a topic or theme for your campaign."
#             self.state["messages"].append({"role": "assistant", "content": response})
#             return response
        
#         # Determine which workflow to use
#         workflow_name = self._determine_workflow(user_input)
#         workflow = self.workflows[workflow_name]
        
#         # Set the first tool as next
#         self.state["next"] = workflow[0]
        
#         # Process through the workflow
#         while self.state.get("next"):
#             result = self._execute_next_tool()
            
#             # If there was an error, return it
#             if "error" in result:
#                 return f"An error occurred: {result['error']}"
        
#         # Construct the final response
#         final_message = {
#             "role": "assistant",
#             "content": f"I've completed the campaign creation process for '{self.state['campaign_theme']}'."
#         }
        
#         # Add details based on what was generated
#         details = []
        
#         if self.state.get("trends"):
#             trend_keywords = [t.get("keyword") for t in self.state.get("trends", []) if "keyword" in t]
#             trend_summary = ", ".join(trend_keywords[:3])
#             details.append(f"Analyzed trends related to {trend_summary}")
        
#         if self.state.get("hashtags"):
#             hashtag_sample = ", ".join(self.state.get("hashtags", [])[:3])
#             details.append(f"Generated hashtags including {hashtag_sample}")
        
#         if self.state.get("script"):
#             script_preview = self.state.get("script", "")[:100] + "..."
#             details.append(f"Created a script: {script_preview}")
        
#         # Include next steps or recommendations
#         next_steps = ""
#         if workflow_name == "research_only":
#             next_steps = " Would you like me to generate a script based on this research?"
#         elif workflow_name == "script_only":
#             next_steps = " Let me know if you'd like any revisions to the script."
        
#         # Build the complete response
#         if details:
#             final_message["content"] += " I've " + ", and ".join(details) + "." + next_steps
        
#         # Add the final message to the conversation history
#         self.state["messages"].append(final_message)
        
#         # Return the final message content and the script if available
#         response = final_message["content"]
#         if self.state.get("script"):
#             response += f"\n\n--- SCRIPT ---\n\n{self.state['script']}"
        
#         return response
    
#     def get_script(self) -> Optional[str]:
#         """Get the generated script if available"""
#         return self.state.get("script")
    
#     def get_hashtags(self) -> List[str]:
#         """Get the generated hashtags if available"""
#         return self.state.get("hashtags", [])