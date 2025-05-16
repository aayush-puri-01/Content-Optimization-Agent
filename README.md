# Creator Content Optimizer Agent

A LangGraph-powered intelligent agent that helps creators and marketers generate optimized content assets such as hashtags, scripts, and production ideas using up-to-date web trends, ethical SEO insights, and campaign goals. Built using GPT-4o-mini, Tavily Search, PyTrends, and OpenAI function-calling with tool orchestration.

---

## Features

- **Trend-Aware Content Generation**: Integrates real-time Google Trends and search engine results using PyTrends and Tavily.
- **Hashtag Generation**: Creates relevant, engaging, and up-to-date hashtags aligned with campaign themes.
- **Graph-Based Workflow**: Uses LangGraph to conditionally route between tools and human-in-the-loop steps.
- **Tool-Centric Modular Design**: Each capability is encapsulated in a reusable, independently callable tool.

---

## Tech Stack

- [LangGraph](https://github.com/langchain-ai/langgraph) for orchestrating conditional flows
- [OpenAI GPT-4o-mini](https://openai.com) as the central LLM
- [Tavily](https://www.tavily.com/) for up-to-date search results
- [PyTrends](https://github.com/GeneralMills/pytrends) for keyword trend analysis
- [Pydantic](https://docs.pydantic.dev) for structured tool schemas
- [LangChain](https://www.langchain.com/) for tools and prompt management
