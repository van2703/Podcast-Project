"""
Utility functions for BBC News AI Podcast Transformer
"""

import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import hashlib


def setup_logging(log_dir: str = 'logs', log_level: str = 'INFO'):
    """Setup logging configuration"""
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y-%m-%d")}.log')

    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger(__name__)


def ensure_directories(dirs: List[str]):
    """Create directories if they don't exist"""
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
        logging.debug(f"Ensured directory exists: {directory}")


def save_json(data: Any, filepath: str):
    """Save data to JSON file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logging.info(f"Saved JSON: {filepath}")


def load_json(filepath: str) -> Any:
    """Load data from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_text(text: str, filepath: str):
    """Save text to file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)
    logging.info(f"Saved text: {filepath}")


def load_text(filepath: str) -> str:
    """Load text from file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def save_binary(data: bytes, filepath: str):
    """Save binary data to file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as f:
        f.write(data)
    logging.info(f"Saved binary: {filepath} ({len(data)} bytes)")


def is_recent(published_date: str, hours: int = 24) -> bool:
    """Check if a published date is within the last N hours"""
    try:
        # Parse date string (handle various formats)
        from dateutil import parser
        pub_time = parser.parse(published_date)

        # Remove timezone info for comparison
        pub_time = pub_time.replace(tzinfo=None)
        now = datetime.now()

        time_diff = now - pub_time
        return time_diff < timedelta(hours=hours)
    except Exception as e:
        logging.warning(f"Failed to parse date '{published_date}': {e}")
        return False


def generate_article_hash(article: Dict[str, Any]) -> str:
    """Generate unique hash for an article based on URL and title"""
    content = f"{article.get('url', '')}{article.get('title', '')}"
    return hashlib.md5(content.encode()).hexdigest()[:12]


def get_date_str() -> str:
    """Get current date string in YYYY-MM-DD format"""
    return datetime.now().strftime('%Y-%m-%d')


def clean_text(text: str) -> str:
    """Clean text: remove extra whitespace, newlines"""
    if not text:
        return ""
    # Replace multiple whitespace with single space
    text = ' '.join(text.split())
    return text.strip()


def chunk_text(text: str, max_chars: int = 5000) -> List[str]:
    """Split text into chunks of max_chars, trying to split at paragraph boundaries"""
    if len(text) <= max_chars:
        return [text]

    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        # If adding this paragraph exceeds limit, save current chunk
        if len(current_chunk) + len(para) + 2 > max_chars:
            if current_chunk:
                chunks.append(current_chunk)
            # If single paragraph is too long, split by sentences
            if len(para) > max_chars:
                chunks.extend(split_by_sentences(para, max_chars))
                current_chunk = ""
            else:
                current_chunk = para
        else:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def split_by_sentences(text: str, max_chars: int) -> List[str]:
    """Split text by sentences when paragraph is too long"""
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 > max_chars:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence
        else:
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def format_articles_for_prompt(articles: List[Dict[str, Any]]) -> str:
    """Format list of articles into a single text for GPT prompt"""
    formatted = []
    for i, article in enumerate(articles, 1):
        formatted.append(f"Article {i}:")
        formatted.append(f"Title: {article.get('title', 'N/A')}")
        formatted.append(f"Source: {article.get('source', 'BBC News')}")
        formatted.append(f"Date: {article.get('published_date', 'N/A')}")
        formatted.append(f"Content: {article.get('content', 'N/A')[:1000]}...")  # Limit content
        formatted.append("")  # Empty line

    return "\n".join(formatted)


def create_latest_symlink(target_path: str, link_path: str):
    """Create a symlink for the latest podcast (Unix) or copy (Windows)"""
    try:
        if os.path.exists(link_path):
            os.remove(link_path)

        # On Windows, symlink may require admin privileges
        # Use copy as fallback
        import shutil
        shutil.copy2(target_path, link_path)
        logging.info(f"Created latest link: {link_path} -> {target_path}")
    except Exception as e:
        logging.warning(f"Failed to create symlink: {e}")