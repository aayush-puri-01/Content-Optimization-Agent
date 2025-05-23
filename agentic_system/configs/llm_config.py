from langchain_openai import ChatOpenAI


_llm = None

def get_llm() -> ChatOpenAI:
    """Initialize and return the LLM with bound tools."""
    global _llm #the llm instance is announced global, for use across the project and not having to insantiate a LLM instance everytime

    if _llm is None:
        from services.trend_tool import trend_analyzer
        from services.search_tool import search_engine
        from services.hashtag_gen import hashtag_generator
        from services.script_tool import script_generator
        from services.tts_tool import tts
        _llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        tools = [trend_analyzer, search_engine, hashtag_generator, script_generator, tts]
        _llm = _llm.bind_tools(tools, strict=True)
    return _llm