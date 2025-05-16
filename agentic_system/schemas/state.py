from typing import List, Dict, Union
from typing_extensions import TypedDict
from pydantic import BaseModel

class RelatedContent(BaseModel):
    title: str
    snippet: str

class TrendItem(BaseModel):
    keyword: str
    relevance: int
    related_content: List[RelatedContent]
    related_queries: List[str]
    trend_direction: str

class Message(BaseModel):
    role: str
    content: str

    # class Config:
    #     extra = 'forbid'  # Disallow additional fields

class Step(BaseModel):
    step: str
    executed: bool

    # class Config:
    #     extra = 'forbid'

class SearchItem(BaseModel):
    title: str
    content: str
    url: str
    score: float

    # class Config:
    #     extra = 'forbid'  # In case Tavily returns more fields

class SearchResult(BaseModel):
    term: str
    results: List[SearchItem] 
    # error: Union[str, None] 

    class Config:
        extra = 'forbid'

class CampaignState(BaseModel):
    messages: List[Message] 
    tone: str
    campaign_theme: str
    target_audience: str
    duration_seconds: int 
    trends: List[TrendItem]
    search_results: List[SearchResult]
    hashtags: List[str]
    script: str
    current_step: str
    production_ideas: List[str]
    steps: List[Step]

    # class Config:
    #     extra = "forbid"

    