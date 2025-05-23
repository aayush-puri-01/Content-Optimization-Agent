from __future__ import annotations

from langchain_core.tools import tool
from schemas.state import CampaignState, Message
from pydantic import BaseModel

from configs.llm_config import get_llm
from configs.logging_config import setup_logging
import logging
setup_logging()
logger = logging.getLogger(__name__)

from google import genai
from google.genai import types
import pyaudio
import base64

import traceback

client = genai.Client(api_key="GEMINI_API_KEY")


class ttsInput(BaseModel):
    state: CampaignState

@tool(args_schema = ttsInput)
def tts(state: CampaignState) -> dict:
    """Provides text to speech for the script generated for the campaign.
    
    Args:
        state: CampaignState with campaign_theme, trends, search_results, hashtags, target_audience, duration_seconds, and script.

    Returns:
    Dict with 'messages' (List[dict]) for state update.
    """

    script = state.script

    try:
        prompt = f"""TTS the following script for a marketing campaign. Make it sound like you are a person pitching the idea of the script! SCRIPT:\n {script}"""
        
        logger.info("Executing the tts tool")
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",  # Use full model path
            contents= prompt,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Kore"
                        )
                    )
                ),
            )
        )
        logger.info("GEMINI TTS service has responded")

        # Decode base64 audio data
        audio_data_b64 = response.candidates[0].content.parts[0].inline_data.data
        logger.info("Base 64 data extracted")
        audio_bytes = base64.b64decode(audio_data_b64)
        logger.info("Audio bytes decoded")

        # Audio settings (must match the output format of the TTS API)
        FORMAT = pyaudio.paInt16  # 16-bit
        CHANNELS = 1              # Mono
        RATE = 24000              # Gemini TTS default sample rate is 24kHz
        # CHUNK = 1024              # Buffer size

        # Initialize PyAudio
        logger.info("Initializing pyaudio streaming service")
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True)

        # Play the audio
        stream.write(audio_bytes)

        # Clean up
        stream.stop_stream()
        stream.close()
        p.terminate()
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error encountered for tts")
        state.messages.append(Message(
            role="assistant",
            content=f"Error generating script: {e}. Using fallback script."
        ))

    update_message = Message(
        role="assistant",
        content=f"Coverted the script text to speech for the campaign"
    )

    return {
        "messages": state.messages + [update_message]
    }