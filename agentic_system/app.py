import gradio as gr
import requests
import json
import traceback

API_URL = "http://localhost:8000/agent/query"

def generate_campaign(user_query:str):
    payload = {
        "prompt" : user_query
    }
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        print(result)
        bot_response = result.get("formatted_output")
        print(bot_response)
        return [(user_query, bot_response)]
    except Exception as e:
        traceback.print_exc()
        return [(user_query, f"Error wih API request {str(e)}")]

def get_interface():
    with gr.Blocks() as demo:
        gr.Markdown("# UGC Optimization with Tool-Powered LLM Agent")
        gr.Markdown("Enter a request to get a detailed response")
        chatbot = gr.Chatbot(
            label="Agent Response",
            height=500,
        )
        with gr.Row():
            user_input = gr.Textbox(
                label="Query Box",
                placeholder="Enter what you want the agent to do (e.g., 'Create a complete campaign...')",
            )
        with gr.Row():
            generate_btn = gr.Button("Generate Response", variant="primary")

        generate_btn.click(
            fn=generate_campaign,
            inputs=user_input,
            outputs=chatbot
        )
    return demo

demo = get_interface()
demo.launch(server_name="0.0.0.0", server_port=7860)
