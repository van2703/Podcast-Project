"""
Script Generator Module - Generate podcast script using OpenAI GPT
"""

import logging
import os
from datetime import datetime
from typing import List, Dict, Any
from openai import OpenAI
import tiktoken

from .utils import setup_logging, ensure_directories, save_text, format_articles_for_prompt
import config

logger = logging.getLogger(__name__)


class ScriptGenerator:
    def __init__(self):
        self.processed_dir = config.PROCESSED_DIR
        ensure_directories([self.processed_dir])

        # Initialize OpenAI client
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")

        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_MODEL

        # Initialize tokenizer for counting
        try:
            self.tokenizer = tiktoken.encoding_for_model(self.model)
        except KeyError:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))

    def build_prompt(self, articles: List[Dict[str, Any]]) -> tuple[str, str]:
        """Build system and user prompts for GPT"""
        system_prompt = config.SYSTEM_PROMPT

        # Format articles for prompt
        articles_text = format_articles_for_prompt(articles)

        user_prompt = f"""
Create a podcast script from these BBC news articles:

{articles_text}

REQUIREMENTS:
- Total length: 3-5 minutes (400-600 words)
- Structure:
  * Intro (30 seconds): Welcome, overview of today's stories
  * 2-3 main stories (60-90 seconds each)
  * Outro (30 seconds): Summary, sign-off, tomorrow preview
- Tone: Conversational, professional but friendly
- Format:
  * Use [INTRO MUSIC], [TRANSITION], [OUTRO MUSIC] cues
  * Speaker labels: HOST:
  * Add natural pauses with "..."
  * No complex jargon, explain if needed
- End with: "Thanks for listening, see you tomorrow!"

FORMAT AS MARKDOWN with clear sections.
"""

        return system_prompt, user_prompt

    def call_gpt(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI GPT API"""
        logger.info(f"Calling OpenAI API with model: {self.model}")

        # Count input tokens
        input_tokens = self.count_tokens(system_prompt + user_prompt)
        logger.info(f"Input tokens: {input_tokens}")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=config.OPENAI_TEMPERATURE,
                max_tokens=config.MAX_TOKENS
            )

            script = response.choices[0].message.content

            # Log token usage
            usage = response.usage
            logger.info(
                f"OpenAI API usage: "
                f"prompt={usage.prompt_tokens}, "
                f"completion={usage.completion_tokens}, "
                f"total={usage.total_tokens}"
            )

            return script

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise

    def generate_script(self, articles: List[Dict[str, Any]]) -> str:
        """Main method: generate podcast script from articles"""
        logger.info("Generating podcast script...")

        if not articles:
            raise ValueError("No articles provided for script generation")

        # Limit number of articles
        articles = articles[:config.MAX_ARTICLES_PER_PODCAST]
        logger.info(f"Using {len(articles)} articles for script")

        # Build prompts
        system_prompt, user_prompt = self.build_prompt(articles)

        # Call GPT
        script = self.call_gpt(system_prompt, user_prompt)

        # Validate script
        if not script or len(script) < 100:
            raise ValueError("Generated script is too short or empty")

        logger.info(f"Generated script: {len(script)} characters, {len(script.split())} words")

        # Save script
        date_str = datetime.now().strftime(config.DATE_FORMAT)
        filename = f"script_{date_str}.md"
        filepath = f"{self.processed_dir}/{filename}"

        save_text(script, filepath)
        logger.info(f"Script saved to: {filepath}")

        return script

    def generate_fallback_script(self, articles: List[Dict[str, Any]]) -> str:
        """Generate a simple fallback script if GPT fails"""
        logger.warning("Generating fallback script...")

        date_str = datetime.now().strftime(config.DATE_FORMAT)
        lines = [
            "# BBC News Podcast - Fallback",
            f"Date: {date_str}",
            "",
            "[INTRO MUSIC]",
            "",
            "HOST: Welcome to BBC News Daily. Today we have the following stories:",
        ]

        for i, article in enumerate(articles[:3], 1):
            lines.append(f"{i}. {article['title']}")

        lines.extend([
            "",
            "HOST: Let's start with the first story.",
            "",
            "[TRANSITION MUSIC]",
            "",
            "HOST: " + articles[0]['content'][:500] if articles[0]['content'] else "No content available.",
            "",
            "[OUTRO MUSIC]",
            "",
            "HOST: That's all for today. Thanks for listening!"
        ])

        script = "\n".join(lines)
        return script


def generate_script(articles: List[Dict[str, Any]]) -> str:
    """Convenience function for external calls"""
    generator = ScriptGenerator()
    return generator.generate_script(articles)


if __name__ == "__main__":
    # Test the module
    logger = setup_logging()

    # Load sample articles
    try:
        sample_file = "data/articles/articles_2024-01-15.json"
        if os.path.exists(sample_file):
            articles = load_json(sample_file)
            script = generate_script(articles[:3])
            print(f"Generated script:\n{script[:500]}...")
        else:
            print("No sample articles found. Run data_ingestion first.")
    except Exception as e:
        logger.error(f"Test failed: {e}")