# Creator Content Optimizer Agent

A LangGraph-powered intelligent agent that helps creators and marketers generate optimized content assets such as hashtags, scripts, and production ideas using up-to-date web trends, ethical SEO insights, and campaign goals. Built using GPT-4o-mini, Tavily Search, PyTrends, and OpenAI function-calling with tool orchestration.

---

## Features

- **Trend-Aware Content Generation**: Integrates real-time Google Trends and search engine results using PyTrends and Tavily.
- **Hashtag Generation**: Creates relevant, engaging, and up-to-date hashtags aligned with campaign themes.
- **Graph-Based Workflow**: Uses LangGraph to conditionally route between tools and human-in-the-loop steps.
- **Tool-Centric Modular Design**: Each capability is encapsulated in a reusable, independently callable tool.
- **Text-To-Speech Conversion**: The script generated for the campaign can be converted to an audio file using the google gemini tts service.

---

## Tech Stack

- [LangGraph](https://github.com/langchain-ai/langgraph) for orchestrating conditional flows
- [OpenAI GPT-4o-mini](https://openai.com) as the central LLM
- [Tavily](https://www.tavily.com/) for up-to-date search results
- [PyTrends](https://github.com/GeneralMills/pytrends) for keyword trend analysis
- [SerpAPI](https://serpapi.com) for web search
- [Pydantic](https://docs.pydantic.dev) for structured tool schemas
- [LangChain](https://www.langchain.com/) for tools and prompt management

---

## Running the API Server

```bash
uvicorn main:app --reload
```

Ensure your `main.py` contains FastAPI app setup and includes the campaign route.

### Request Body

```json
{
  "prompt": "Generate a complete campaign for sunglasses brand for Gen Z in a humorous tone"
}
```

### Response

```json
{
  "formatted_output": "=== 📣 Campaign Overview ===\n🎯 Theme: ..."
}
```

---

## Making Requests from Terminal (with `jq`)

You can use `curl` and `jq` to make requests directly from your terminal and format the output cleanly.

### Install `jq` (if not already)

- Ubuntu/Debian:

  ```bash
  sudo apt install jq
  ```

- macOS (Homebrew):

  ```bash
  brew install jq
  ```

---

### Example Usage

```bash
curl -s -X POST 'http://127.0.0.1:8000/agent/query' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Generate a complete campaign for sunglasses brand for Gen Z in a humorous tone"
  }' | jq -r '.formatted_output'
```

This command sends the prompt and prints only the `formatted_output` (the campaign content) to your terminal in a clean, readable format.

---

## Dependencies

This project uses [`uv`](https://pypi.org/project/uv/) as the package manager. To install all dependencies:

```bash
uv sync
```

You can also place those dependencies in a `requirements.txt` and install accordingly:

```bash
uv pip install -r requirements.txt
```

---

## Project Structure

```
agent.py
main.py
routes/
  └── campaign_router.py
services/
  └── (llm_node.py, trend_tool.py, etc.)
schemas/
  └── state.py
```
