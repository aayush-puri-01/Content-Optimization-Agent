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
import os

from dotenv import load_dotenv
load_dotenv()

try:
    gemini_key = os.getenv("GEMINI_API_KEY")
except:
    print("GEMINI API KEY CANNOT BE FETCHED! ")

client = genai.Client(api_key=gemini_key)

import wave

# Set up the wave file to save the output:
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
   with wave.open(filename, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      wf.writeframes(pcm)


class ttsInput(BaseModel):
    state: CampaignState

@tool(args_schema = ttsInput)
def tts_generator(state: CampaignState) -> dict:
    """Provides text to speech for the script generated for the campaign.
    
    Args:
        state: CampaignState with campaign_theme, trends, search_results, hashtags, target_audience, duration_seconds, and script.

    Returns:
    Dict with 'messages' (List[dict]) for state update.
    """

    script = state.script
    # script = f"""
    # TITLE: Shoes So Cool, Even Your Crusty Ex Will Notice

    # [0:00–0:05]
    # (Opening shot: a messy room. Zoom in on crusty, old sneakers with holes. Sad violin music plays.)
    # Narrator (sarcastically):
    # "This was your shoe game? In *2025*? Honey… no."

    # [0:06–0:15]
    # (Cut to dramatic makeover sequence. A Gen Z protagonist holds up new flashy, ultra-stylish shoes — the brand’s product — glowing like they’re holy.)
    # Narrator:
    # "Introducing [Brand Name] — the only shoes that scream *‘I have my life together’* even if you're crying over an astrology meme."

    # [0:16–0:25]
    # (They step outside in slow motion. Heads turn. A squirrel drops its acorn in shock. The ex walks by and double-takes.)
    # Narrator:
    # "Stylish? Check. Comfortable? Like walking on your childhood stuffed animal. Affordable? Yep, you can still afford iced coffee."

    # [0:26–0:40]
    # (Jump cuts: dancing, skateboarding, walking into class late but confidently, doing a terrible TikTok dance, all in the same shoes.)
    # On-screen text (flashing):
    # One pair. Endless vibes.
    # Zero regrets.

    # [0:41–0:55]
    # (Cut to protagonist’s ex crying in the rain, barefoot, as the camera zooms into the shoes walking away into the sunset.)
    # Narrator:
    # "Break hearts. Break norms. Just don't break your ankles. Get [Brand Name]."

    # [0:56–1:00]
    # (Logo + tagline on screen with upbeat music)
    # Voiceover:
    # "[Brand Name] — Step Up or Step Aside."
    # """

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
        # print(response)

        # Decode base64 audio data
        audio_data_b64 = response.candidates[0].content.parts[0].inline_data.data

        file_name='out.wav'
        wave_file(file_name, audio_data_b64)
        logger.info("WAV file has been saved successfully")  

        # logger.info("Base 64 data extracted")
        # print(audio_data_b64)

        # audio_bytes = base64.b64decode(audio_data_b64)
        # logger.info("Audio bytes decoded")
        # print(audio_bytes)

        # Audio settings (must match the output format of the TTS API)
        # FORMAT = pyaudio.paInt16  # 16-bit
        # CHANNELS = 1              # Mono
        # RATE = 24000              # Gemini TTS default sample rate is 24kHz
        # CHUNK = 1024              # Buffer size

        # Initialize PyAudio
        # logger.info("Initializing pyaudio streaming service")
        # p = pyaudio.PyAudio()
        # stream = p.open(format=FORMAT,
        #                 channels=CHANNELS,
        #                 rate=RATE,
        #                 output=True)

        # # Play the audio
        # stream.write(audio_bytes)

        # # Clean up
        # stream.stop_stream()
        # stream.close()
        # p.terminate()
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error encountered for tts")
        state.messages.append(Message(
            role="assistant",
            content=f"Error generating script: {e}. Using fallback script."
        ))

    update_message = Message(
        role="assistant",
        content=f"Coverted the script text to speech for the campaign, saved as out.wav file!"
    )

    return {
        "messages": state.messages + [update_message]
    }