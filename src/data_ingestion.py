"""
Data Ingestion Module - Fetch articles from BBC News RSS feed
"""

import logging
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dateutil import parser
import time

from .utils import (
    setup_logging, ensure_directories, save_json, load_json,
    is_recent, generate_article_hash, clean_text
)
import config

logger = logging.getLogger(__name__)


class DataIngestion:
    def __init__(self):
        self.articles_dir = config.ARTICLES_DIR
        ensure_directories([self.articles_dir])

    def fetch_rss_feed(self, url: str) -> List[Dict[str, Any]]:
        """Fetch and parse RSS feed"""
        logger.info(f"Fetching RSS feed: {url}")

        try:
            feed = feedparser.parse(url)

            if feed.bozo:  # RSS feed has errors
                logger.warning(f"RSS feed warning: {feed.bozo_exception}")

            entries = feed.entries
            logger.info(f"Found {len(entries)} entries in feed")
            return entries

        except Exception as e:
            logger.error(f"Failed to fetch RSS feed {url}: {e}")
            return []

    def scrape_article_content(self, url: str) -> str:
        """Scrape full article content from URL"""
        logger.debug(f"Scraping article: {url}")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # BBC News content selectors (may need updates if BBC changes layout)
            selectors = [
                'div.ssrcss-11r1m41-RichText',  # Main article body
                'div.ssrcss-1f5n92u-RichText',  # Alternative
                'div[class*="RichText"]',  # Generic
                'article div.ssrcss-1f5n92u-RichText',
            ]

            content = ""
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    content = ' '.join([elem.get_text(strip=True) for elem in elements])
                    break

            # Fallback: try to find main content div
            if not content:
                main_content = soup.find('main') or soup.find('article')
                if main_content:
                    content = main_content.get_text(strip=True)

            if content:
                content = clean_text(content)
                logger.debug(f"Scraped {len(content)} characters")
                return content
            else:
                logger.warning(f"No content found for {url}")
                return ""

        except requests.RequestException as e:
            logger.error(f"Network error scraping {url}: {e}")
            return ""
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return ""

    def process_feed_entries(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process RSS feed entries into article objects"""
        articles = []

        for entry in entries:
            try:
                # Check if article is recent
                published_date = entry.get('published', entry.get('updated', ''))
                if not is_recent(published_date, config.RECENT_HOURS):
                    logger.debug(f"Skipping old article: {entry.get('title', 'Unknown')}")
                    continue

                # Get article URL
                url = entry.get('link', '')
                if not url:
                    continue

                # Scrape full content
                content = self.scrape_article_content(url)
                if not content or len(content) < 100:
                    logger.warning(f"Skipping article with insufficient content: {entry.get('title')}")
                    continue

                # Build article object
                article = {
                    'id': generate_article_hash({
                        'url': url,
                        'title': entry.get('title', ''),
                        'published': published_date
                    }),
                    'title': entry.get('title', 'Untitled'),
                    'url': url,
                    'published_date': published_date,
                    'content': content,
                    'summary': entry.get('summary', entry.get('description', ''))[:500],
                    'source': 'BBC News'
                }

                articles.append(article)
                logger.info(f"Processed article: {article['title'][:50]}...")

                # Be polite: delay between requests
                time.sleep(1)

            except Exception as e:
                logger.error(f"Error processing entry: {e}")
                continue

        logger.info(f"Total articles processed: {len(articles)}")
        return articles

    def save_articles(self, articles: List[Dict[str, Any]]) -> str:
        """Save articles to JSON file"""
        date_str = datetime.now().strftime(config.DATE_FORMAT)
        filename = f"articles_{date_str}.json"
        filepath = f"{self.articles_dir}/{filename}"

        save_json(articles, filepath)
        return filepath

    def fetch_articles(self) -> List[Dict[str, Any]]:
        """Main method: fetch articles from all configured RSS feeds"""
        logger.info("Starting data ingestion...")

        all_articles = []

        for feed_url in config.RSS_FEEDS:
            entries = self.fetch_rss_feed(feed_url)
            if entries:
                articles = self.process_feed_entries(entries)
                all_articles.extend(articles)

            # Be polite: delay between feeds
            time.sleep(2)

        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)

        logger.info(f"Total unique articles fetched: {len(unique_articles)}")

        # Save to file
        if unique_articles:
            filepath = self.save_articles(unique_articles)
            logger.info(f"Articles saved to: {filepath}")

        return unique_articles


def fetch_articles() -> List[Dict[str, Any]]:
    """Convenience function for external calls"""
    ingestion = DataIngestion()
    return ingestion.fetch_articles()


if __name__ == "__main__":
    # Test the module
    logger = setup_logging()
    articles = fetch_articles()
    print(f"Fetched {len(articles)} articles")
    for a in articles[:3]:
        print(f"- {a['title'][:60]}...")