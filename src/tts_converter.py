"""
TTS Converter Module - Convert script to speech using various TTS providers
"""

import logging
import os
import time
from datetime import datetime
from typing import List
import requests
from openai import OpenAI

from .utils import setup_logging, ensure_directories, save_binary, chunk_text
import config

logger = logging.getLogger(__name__)


class TTSConverter:
    def __init__(self):
        self.output_dir = config.OUTPUT_DIR
        ensure_directories([self.output_dir])

        # Initialize clients based on provider
        self.provider = config.TTS_PROVIDER

        if self.provider == 'openai':
            if not config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is required for OpenAI TTS")
            self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)

        elif self.provider == 'elevenlabs':
            if not config.ELEVENLABS_API_KEY:
                raise ValueError("ELEVENLABS_API_KEY is required for ElevenLabs TTS")
            self.elevenlabs_headers = {
                "xi-api-key": config.ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            }
            self.elevenlabs_url = f"https://api.elevenlabs.io/v1/text-to-speech/{config.ELEVENLABS_VOICE_ID}"

        elif self.provider == 'gtts':
            from gtts import gTTS
            self.gtts = gTTS

        else:
            raise ValueError(f"Unsupported TTS provider: {self.provider}")

    def call_elevenlabs(self, text: str) -> bytes:
        """Call ElevenLabs TTS API"""
        data = {
            "text": text,
            "voice_settings": {
                "stability": config.ELEVENLABS_STABILITY,
                "similarity_boost": config.ELEVENLABS_SIMILARITY_BOOST
            },
            "model_id": "eleven_multilingual_v2"
        }

        try:
            response = requests.post(
                self.elevenlabs_url,
                json=data,
                headers=self.elevenlabs_headers,
                stream=True,
                timeout=30
            )

            if response.status_code == 200:
                return response.content
            else:
                error_msg = f"ElevenLabs API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)

        except requests.RequestException as e:
            logger.error(f"ElevenLabs request failed: {e}")
            raise

    def call_openai_tts(self, text: str) -> bytes:
        """Call OpenAI TTS API"""
        try:
            response = self.openai_client.audio.speech.create(
                model=config.OPENAI_TTS_MODEL,
                voice=config.OPENAI_VOICE,
                input=text,
                response_format='mp3'
            )

            # Save to bytes
            return response.content

        except Exception as e:
            logger.error(f"OpenAI TTS failed: {e}")
            raise

    def call_gtts(self, text: str) -> bytes:
        """Call Google TTS (gTTS)"""
        try:
            tts = self.gtts(text=text, lang='en', slow=False)
            # gTTS saves to file, we need bytes
            temp_file = f"{self.output_dir}/temp_gtts.mp3"
            tts.save(temp_file)

            with open(temp_file, 'rb') as f:
                audio_bytes = f.read()

            os.remove(temp_file)
            return audio_bytes

        except Exception as e:
            logger.error(f"Google TTS failed: {e}")
            raise

    def convert_chunk(self, text: str) -> bytes:
        """Convert a single text chunk to speech based on provider"""
        if self.provider == 'elevenlabs':
            return self.call_elevenlabs(text)
        elif self.provider == 'openai':
            return self.call_openai_tts(text)
        elif self.provider == 'gtts':
            return self.call_gtts(text)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def convert_to_speech(self, script: str, output_path: str = None) -> str:
        """
        Main method: convert script to speech MP3

        Args:
            script: The podcast script text
            output_path: Optional custom output path

        Returns:
            Path to generated MP3 file
        """
        logger.info(f"Converting script to speech using {self.provider}...")
        logger.info(f"Script length: {len(script)} characters, {len(script.split())} words")

        # Determine output path
        if not output_path:
            date_str = datetime.now().strftime(config.DATE_FORMAT)
            output_path = f"{self.output_dir}/podcast_{date_str}.mp3"

        # Chunk script if necessary (ElevenLabs has 5000 char limit)
        chunks = chunk_text(script, max_chars=5000)
        logger.info(f"Split into {len(chunks)} chunks")

        # Convert each chunk
        audio_chunks = []
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"Converting chunk {i}/{len(chunks)} ({len(chunk)} chars)...")

            try:
                audio = self.convert_chunk(chunk)
                audio_chunks.append(audio)

                # Be polite: delay between chunks
                if i < len(chunks):
                    time.sleep(1)

            except Exception as e:
                logger.error(f"Failed to convert chunk {i}: {e}")
                # Continue with other chunks
                continue

        if not audio_chunks:
            raise ValueError("No audio chunks generated")

        # Concatenate all chunks
        logger.info(f"Concatenating {len(audio_chunks)} audio chunks...")
        final_audio = b''.join(audio_chunks)

        # Save to file
        save_binary(final_audio, output_path)
        logger.info(f"MP3 saved: {output_path} ({len(final_audio)} bytes)")

        return output_path


def convert_to_speech(script: str, output_path: str = None) -> str:
    """Convenience function for external calls"""
    converter = TTSConverter()
    return converter.convert_to_speech(script, output_path)


if __name__ == "__main__":
    # Test the module
    logger = setup_logging()

    # Load sample script
    try:
        script_file = "data/processed/script_2024-01-15.md"
        if os.path.exists(script_file):
            with open(script_file, 'r', encoding='utf-8') as f:
                script = f.read()

            output = convert_to_speech(script)
            print(f"Generated MP3: {output}")
        else:
            print("No sample script found. Run script_generator first.")
    except Exception as e:
        logger.error(f"Test failed: {e}")