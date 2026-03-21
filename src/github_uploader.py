"""
GitHub Uploader Module - Upload podcast MP3 to GitHub Pages
"""

import logging
import os
from datetime import datetime
from typing import Optional
from github import Github
from github.GithubException import GithubException

from .utils import setup_logging, ensure_directories, save_text
import config

logger = logging.getLogger(__name__)


class GitHubUploader:
    def __init__(self):
        if not config.GITHUB_TOKEN:
            raise ValueError("GITHUB_TOKEN is required")

        self.token = config.GITHUB_TOKEN
        self.repo_name = config.GITHUB_REPO
        self.branch = config.GITHUB_BRANCH

        # Initialize GitHub client
        try:
            self.g = Github(self.token)
            self.repo = self.g.get_repo(self.repo_name)
            logger.info(f"Connected to GitHub repo: {self.repo_name}")
        except GithubException as e:
            logger.error(f"Failed to connect to GitHub: {e}")
            raise

    def upload_file(self, file_path: str, repo_path: str, commit_message: str) -> bool:
        """
        Upload a file to GitHub repository

        Args:
            file_path: Local file path
            repo_path: Path in repository (e.g., 'output/podcast_2024-01-15.mp3')
            commit_message: Commit message

        Returns:
            True if successful
        """
        try:
            # Read file content
            with open(file_path, 'rb') as f:
                content = f.read()

            # Check if file already exists
            try:
                existing_file = self.repo.get_contents(repo_path, ref=self.branch)
                # Update existing file
                self.repo.update_file(
                    path=repo_path,
                    message=commit_message,
                    content=content,
                    sha=existing_file.sha,
                    branch=self.branch
                )
                logger.info(f"Updated file: {repo_path}")

            except GithubException as e:
                if e.status == 404:
                    # File doesn't exist, create new
                    self.repo.create_file(
                        path=repo_path,
                        message=commit_message,
                        content=content,
                        branch=self.branch
                    )
                    logger.info(f"Created file: {repo_path}")
                else:
                    raise

            return True

        except Exception as e:
            logger.error(f"Failed to upload file {file_path}: {e}")
            return False

    def update_index_html(self, latest_mp3_filename: str, date_str: str) -> bool:
        """
        Create or update index.html with audio player for the latest podcast

        Args:
            latest_mp3_filename: Filename of the latest MP3 (e.g., 'podcast_2024-01-15.mp3')
            date_str: Date string for display

        Returns:
            True if successful
        """
        try:
            # Check if index.html exists
            try:
                existing_file = self.repo.get_contents('index.html', ref=self.branch)
                # Read existing content to preserve archive
                existing_content = existing_file.decoded_content.decode('utf-8')
                # Parse archive (simple approach: keep existing list, add new at top)
                # For simplicity, we'll just replace the whole file
                html_content = self._generate_index_html(latest_mp3_filename, date_str, existing_content)
                self.repo.update_file(
                    path='index.html',
                    message=f"Update index for podcast {date_str}",
                    content=html_content,
                    sha=existing_file.sha,
                    branch=self.branch
                )
            except GithubException as e:
                if e.status == 404:
                    # Create new index.html
                    html_content = self._generate_index_html(latest_mp3_filename, date_str)
                    self.repo.create_file(
                        path='index.html',
                        message=f"Add index for podcast {date_str}",
                        content=html_content,
                        branch=self.branch
                    )
                else:
                    raise

            logger.info("Updated index.html")
            return True

        except Exception as e:
            logger.error(f"Failed to update index.html: {e}")
            return False

    def _generate_index_html(self, latest_filename: str, date_str: str, existing_html: str = None) -> str:
        """Generate HTML content for index page"""
        mp3_url = f"output/{latest_filename}"

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BBC News AI Podcast</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        .container {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 30px;
        }}
        .player {{
            background: #f8f9fa;
            border-radius: 15px;
            padding: 30px;
            margin: 30px 0;
            text-align: center;
        }}
        audio {{
            width: 100%;
            margin: 20px 0;
            border-radius: 10px;
        }}
        .date-badge {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-bottom: 20px;
        }}
        .download-link {{
            display: inline-block;
            margin-top: 15px;
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }}
        .download-link:hover {{
            text-decoration: underline;
        }}
        .archive {{
            margin-top: 40px;
        }}
        .archive h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .archive ul {{
            list-style: none;
            padding: 0;
        }}
        .archive li {{
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }}
        .archive a {{
            color: #667eea;
            text-decoration: none;
        }}
        .archive a:hover {{
            text-decoration: underline;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #95a5a6;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎙️ BBC News AI Podcast</h1>
        <p class="subtitle">Automatically generated daily from BBC News</p>

        <div class="player">
            <div class="date-badge">Latest: {date_str}</div>
            <audio controls>
                <source src="{mp3_url}" type="audio/mpeg">
                Your browser does not support the audio element.
            </audio>
            <br>
            <a href="{mp3_url}" download class="download-link">⬇️ Download MP3</a>
        </div>

        <div class="archive">
            <h2>📜 Previous Episodes</h2>
            <ul>
                <li><strong>{date_str}</strong> - <a href="{mp3_url}">Listen</a> | <a href="{mp3_url}" download>Download</a></li>
'''

        # Try to extract archive from existing HTML
        if existing_html:
            # Simple parsing: extract other episodes (not the one we're adding)
            # This is a simplified approach - in production you might want to query GitHub API
            pass

        html += '''
            </ul>
        </div>

        <div class="footer">
            <p>Made with ❤️ and AI | <a href="https://github.com/vanph/podcast-ai-transformer">View Source</a></p>
        </div>
    </div>
</body>
</html>'''

        return html

    def upload_podcast(self, mp3_path: str, date_str: str) -> Optional[str]:
        """
        Upload podcast MP3 to GitHub Pages

        Args:
            mp3_path: Local path to MP3 file
            date_str: Date string for naming

        Returns:
            Public URL of the uploaded podcast, or None if failed
        """
        logger.info("Uploading podcast to GitHub Pages...")

        try:
            # 1. Upload MP3 file
            mp3_filename = f"podcast_{date_str}.mp3"
            repo_mp3_path = f"output/{mp3_filename}"

            success = self.upload_file(
                file_path=mp3_path,
                repo_path=repo_mp3_path,
                commit_message=f"Add podcast for {date_str}"
            )

            if not success:
                logger.error("Failed to upload MP3")
                return None

            # 2. Update index.html
            success = self.update_index_html(mp3_filename, date_str)
            if not success:
                logger.warning("Failed to update index.html, but MP3 was uploaded")

            # 3. Return public URL
            # GitHub Pages URL format: https://username.github.io/repo-name/path
            username = config.GITHUB_USERNAME
            repo_name = config.GITHUB_REPO_NAME
            public_url = f"https://{username}.github.io/{repo_name}/{repo_mp3_path}"

            logger.info(f"Podcast available at: {public_url}")
            return public_url

        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return None


def upload_podcast(mp3_path: str, date_str: str) -> Optional[str]:
    """Convenience function for external calls"""
    uploader = GitHubUploader()
    return uploader.upload_podcast(mp3_path, date_str)


if __name__ == "__main__":
    # Test the module
    logger = setup_logging()

    # Test with a sample file
    test_file = "output/test.mp3"
    if os.path.exists(test_file):
        date_str = datetime.now().strftime('%Y-%m-%d')
        url = upload_podcast(test_file, date_str)
        if url:
            print(f"Uploaded successfully: {url}")
        else:
            print("Upload failed")
    else:
        print(f"Test file not found: {test_file}")
        print("Please create a test MP3 file first.")