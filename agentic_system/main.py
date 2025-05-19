from fastapi import FastAPI
from routes.agent_router import router


app = FastAPI(
    title="Content Optimization Agent for User Generated Content",
    description="Includes a tool-powered LLM-based agentic system that provided content optimization strategies for users",
    version="1.0.0"
)

app.include_router(router, prefix="/agent", tags=["Campaign"])
