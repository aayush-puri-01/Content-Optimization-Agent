from fastapi import APIRouter
from fastapi.responses import JSONResponse
from agent import format_campaign_output, build_graph
from schemas.state import CampaignState, Message


from schemas.api_schemas import CampaignRequest, CampaignResponse
from configs.logging_config import setup_logging
import logging
setup_logging()
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/query", response_model=CampaignResponse)
def query_agent(request:CampaignRequest):

    try:
        if not request:
            return JSONResponse(content={"error": "Query is required"}, status_code=400)
        
        try:
            initial_state = CampaignState(
                campaign_theme="",
                target_audience="",
                duration_seconds=60,
                tone="",
                steps=[],
                trends=[],
                search_results=[],
                hashtags=[],
                script="",
                production_ideas=[],
                messages=[Message(role="user", content=request.prompt)],
                current_step=""
            )

            graph = build_graph()

            result = graph.invoke(initial_state)
            final_state = CampaignState(**result)
            formatted_state = format_campaign_output(final_state)
            logger.info(f"\n------------Complete campaign description------------\n{formatted_state}")
            return CampaignResponse(formatted_output=formatted_state)
        except Exception as e:
            return JSONResponse(content={"error":f"Internal Processing Error, API endpoint entered but couldnt produce results! : {str(e)}"})
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error, API endpoint not entered! HTTP Error"}, status_code=500)
    


