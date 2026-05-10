import os
import tempfile
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

def get_elevenlabs_client():
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("ELEVENLABS_API_KEY missing.")
        return None
    return ElevenLabs(api_key=api_key)

def transcribe_audio(file_path: str) -> str:
    """Transcribe an audio file to text using ElevenLabs."""
    client = get_elevenlabs_client()
    if not client:
        return ""
        
    try:
        with open(file_path, "rb") as audio_file:
            result = client.speech_to_text.convert(
                file=audio_file,
                model_id="scribe_v1"
            )
        return result.text
    except Exception as e:
        print(f"Transcription error: {e}")
        return ""

def generate_speech(text: str) -> str:
    """Generate speech from text using ElevenLabs and return the path to the temp file."""
    client = get_elevenlabs_client()
    if not client:
        return ""
        
    try:
        audio = client.text_to_speech.convert(
            text=text,
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75)
        )
        
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f:
            for chunk in audio:
                f.write(chunk)
            temp_path = f.name
            
        return temp_path
    except Exception as e:
        print(f"Failed to generate speech: {e}")
        return ""
