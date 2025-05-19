from pydantic import BaseModel

class CampaignRequest(BaseModel):
    prompt: str

class CampaignResponse(BaseModel):
    formatted_output: str
