# Creator Content Optimizer Agent

A LangGraph-powered intelligent agent that helps creators and marketers generate optimized content assets such as hashtags, scripts, and production ideas using up-to-date web trends, ethical SEO insights, and campaign goals. Built using GPT-4o-mini, Tavily Search, PyTrends, and OpenAI function-calling with tool orchestration.

---

## System Architecture

In this architecture, each tool operates as an independent agent with specific expertise, while loose coupling allows for easy extension and modification.The LLM Router acts as a central coordinator. Steps are generated based on user requirements, not pre-defined which allows felexible execution order with dependency management.

![System Architecture](docs\agent.png)

### 1. LLM Router Node (`llm_node.py`)

**Role:** Central orchestrator and decision-making hub  
**Responsibilities:**

- Extracts campaign parameters (campaign theme, target audience, duration, tone) from user input
- Dynamically generates execution steps based on requirements
- Routes between different tools in the workflow
- Manages step execution state and determines workflow completion

---

### 2. Tool Suite

#### Trend Analyzer (`trend_tool.py`)

**Purpose:** Analyzes current trends related to campaign themes  
**Implementation:**

- Uses SerpAPI for Google search-based trend analysis
- LLM-powered keyword generation for comprehensive trend coverage
- Extracts trend direction, related content, and relevance scores

**Output:** Structured trend data with keywords, relevance metrics, and trend directions

---

#### Search Engine (`search_tool.py`)

**Purpose:** Gathers comprehensive information on identified trends  
**Implementation:**

- Integrates Tavily Search API for deep web research
- Searches across multiple trend keywords simultaneously
- Implements rate limiting and error handling

**Output:** Detailed search results with content summaries and metadata

---

#### Hashtag Generator (`hashtag_gen_tool.py`)

**Purpose:** Creates relevant and trending hashtags for campaigns  
**Implementation:**

- Analyzes campaign theme, trends, and search results
- Generates memorable, catchy hashtags with viral potential
- Balances broad appeal with niche specificity

**Output:** Curated list of 5 optimized hashtags with proper formatting

---

#### Script Generator (`script_tool.py`)

**Purpose:** Creates engaging campaign scripts  
**Implementation:**

- Synthesizes all collected data (trends, search results, hashtags)
- Generates audience-appropriate content with specified tone
- Includes production suggestions and timing considerations

**Output:** Complete script with production ideas and call-to-action elements

---

#### Text-to-Speech Generator (`tts_tool.py`)

**Purpose:** Converts scripts into audio content  
**Implementation:**

- Integrates Google Gemini TTS API
- Configurable voice settings (currently uses "Kore" voice)
- Outputs high-quality WAV files for immediate use

**Output:** Audio file (`out.wav`) ready for campaign deployment

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
