from langchain_openai import ChatOpenAI


_llm = None

def get_llm() -> ChatOpenAI:
    """Initialize and return the LLM with bound tools."""
    global _llm

    if _llm is None:
        from services.trend_tool import trend_analyzer
        from services.search_tool import search_engine
        from services.hashtag_gen import hashtag_generator
        from services.script_tool import script_generator
        _llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        tools = [trend_analyzer, search_engine, hashtag_generator, script_generator]
        _llm = _llm.bind_tools(tools, strict=True)
    return _llm