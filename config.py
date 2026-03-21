"""
Configuration file for BBC News AI Podcast Transformer
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ========== RSS FEEDS ==========
# BBC News RSS feeds - có thể thêm/bớt tùy ý
RSS_FEEDS = [
    'http://feeds.bbci.co.uk/news/rss.xml',  # Main news
    'http://feeds.bbci.co.uk/news/world/rss.xml',  # World news
    'http://feeds.bbci.co.uk/news/technology/rss.xml',  # Tech news
]

# ========== OPENAI ==========
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', 0.7))
MAX_TOKENS = int(os.getenv('MAX_TOKENS', 1000))

# Prompt settings
SYSTEM_PROMPT = """
You are a professional podcast host with 10 years of experience.
Your style is: friendly, engaging, clear, and informative.
You speak at a moderate pace with natural pauses.
"""

# ========== TTS (Text-to-Speech) ==========
TTS_PROVIDER = os.getenv('TTS_PROVIDER', 'elevenlabs')  # 'elevenlabs', 'openai', 'gtts'

# ElevenLabs settings
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', '21m00Tcm4TlvDq8ikWAM')  # Bella (female)
ELEVENLABS_STABILITY = float(os.getenv('ELEVENLABS_STABILITY', 0.5))
ELEVENLABS_SIMILARITY_BOOST = float(os.getenv('ELEVENLABS_SIMILARITY_BOOST', 0.5))

# OpenAI TTS settings
OPENAI_VOICE = os.getenv('OPENAI_VOICE', 'alloy')  # alloy, echo, fable, onyx, nova, shimmer
OPENAI_TTS_MODEL = os.getenv('OPENAI_TTS_MODEL', 'tts-1')  # 'tts-1' or 'tts-1-hd'

# ========== GITHUB ==========
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'username/repo-name')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME', 'username')
GITHUB_REPO_NAME = os.getenv('GITHUB_REPO_NAME', 'repo-name')
GITHUB_BRANCH = os.getenv('GITHUB_BRANCH', 'gh-pages')

# ========== PATHS ==========
DATA_DIR = 'data'
ARTICLES_DIR = f'{DATA_DIR}/articles'
PROCESSED_DIR = f'{DATA_DIR}/processed'
OUTPUT_DIR = 'output'
LOGS_DIR = 'logs'

# ========== SETTINGS ==========
PODCAST_DURATION_TARGET = int(os.getenv('PODCAST_DURATION_TARGET', 300))  # seconds (5 minutes)
MAX_ARTICLES_PER_PODCAST = int(os.getenv('MAX_ARTICLES_PER_PODCAST', 5))
RECENT_HOURS = int(os.getenv('RECENT_HOURS', 24))  # Only articles from last 24h

# File naming
DATE_FORMAT = '%Y-%m-%d'

# ========== LOGGING ==========
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# ========== VALIDATION ==========
def validate_config():
    """Validate required configuration"""
    errors = []

    if not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is required")

    if TTS_PROVIDER == 'elevenlabs' and not ELEVENLABS_API_KEY:
        errors.append("ELEVENLABS_API_KEY is required when TTS_PROVIDER='elevenlabs'")

    if not GITHUB_TOKEN:
        errors.append("GITHUB_TOKEN is required")

    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

# Call validation on import (optional)
# validate_config()