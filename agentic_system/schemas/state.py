from typing import List, Dict, Union
from typing_extensions import TypedDict
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str

    class Config:
        extra = 'forbid'  # Disallow additional fields

class Step(BaseModel):
    step: str
    executed: bool

    class Config:
        extra = 'forbid'

class CampaignState(BaseModel):
    messages: List[Message] 
    tone: str
    campaign_theme: str
    target_audience: str = "General Audience"
    duration_seconds: int = 30
    trends: List[str]
    search_results: List[Dict]
    hashtags: List[str]
    script: str
    current_step: str
    production_ideas: List[str]
    steps: List[Step]

    class Config:
        extra = "forbid"

    