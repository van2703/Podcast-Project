# Kiến trúc hệ thống - BBC News AI Podcast Transformer

## 1. Tổng quan kiến trúc

Hệ thống được thiết kế theo mô hình **pipeline đơn giản** (sequential processing), mỗi module thực hiện một nhiệm vụ cụ thể và truyền kết quả cho module tiếp theo.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MAIN PIPELINE                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────┐         │
│  │ BBC RSS     │───▶│ Data          │───▶│ Script       │         │
│  │ Feed        │    │ Ingestion     │    │ Generator    │         │
│  └─────────────┘    └──────────────┘    └──────────────┘         │
│                          │                     │                   │
│                          ▼                     ▼                   │
│                 data/articles/        data/processed/             │
│                          │                     │                   │
│                          ▼                     ▼                   │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────┐         │
│  │ TTS         │◀───│ TTS          │◀───│ Converter    │         │
│  │ Converter   │    │              │    │              │         │
│  └─────────────┘    └──────────────┘    └──────────────┘         │
│                          │                                         │
│                          ▼                                         │
│                    output/                                        │
│                          │                                         │
│                          ▼                                         │
│  ┌─────────────┐    ┌──────────────┐                            │
│  │ GitHub      │◀───│ GitHub       │                            │
│  │ Pages       │    │ Uploader     │                            │
│  └─────────────┘    └──────────────┘                            │
│                          │                                         │
│                          ▼                                         │
│              https://username.github.io/repo/podcast_latest.mp3  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Nguyên lý thiết kế**:
- **Đơn giản**: Mỗi module độc lập, ít phụ thuộc
- **Dễ test**: Có thể test từng module riêng biệt
- **Dễ debug**: Log rõ ràng, file output trung gian lưu lại
- **Dễ mở rộng**: Thêm source mới, TTS mới, deploy target mới

---

## 2. Chi tiết từng module

### 2.1 Data Ingestion Module (`src/data_ingestion.py`)

**Trách nhiệm**:
- Fetch RSS feed từ BBC News
- Parse và lọc bài báo mới (published trong 24h qua)
- Tải nội dung đầy đủ từ URL của mỗi bài (scraping)
- Lưu vào `data/articles/` dạng JSON

**Input**: RSS feed URL(s) từ config
**Output**: List of article objects, mỗi article là dict:
```json
{
  "id": "unique_hash",
  "title": "Article title",
  "url": "https://bbc.com/...",
  "published_date": "2024-01-15T10:30:00Z",
  "content": "Full article text...",
  "summary": "Short summary...",
  "source": "BBC News"
}
```

**Algorithm**:
```python
def fetch_articles():
    # 1. Parse RSS feed
    feed = feedparser.parse(RSS_URL)
    articles = []

    # 2. Lọc bài mới (24h)
    for entry in feed.entries:
        if is_recent(entry.published):
            # 3. Tải nội dung đầy đủ
            full_content = scrape_article_content(entry.link)
            if full_content:
                article = {
                    'title': entry.title,
                    'url': entry.link,
                    'published_date': entry.published,
                    'content': full_content,
                    'summary': entry.summary
                }
                articles.append(article)

    # 4. Lưu vào file
    save_articles(articles, 'data/articles/articles_YYYY-MM-DD.json')
    return articles
```

**Error Handling**:
- Retry 3 lần nếu network error
- Skip bài nào không tải được content
- Log tất cả errors vào `logs/ingestion_YYYY-MM-DD.log`

**Dependencies**:
- `feedparser` - Parse RSS
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `python-dateutil` - Date parsing

---

### 2.2 Script Generator Module (`src/script_generator.py`)

**Trách nhiệm**:
- Đọc articles từ `data/articles/`
- Gọi OpenAI API với prompt template
- Parse response thành kịch bản có cấu trúc
- Lưu script vào `data/processed/`

**Input**: Article JSON files
**Output**: Script file (Markdown) với format:
```markdown
# BBC News Podcast - 2024-01-15

[INTRO MUSIC - 10 seconds]

HOST: Welcome to BBC News Daily! I'm your AI host, and today we're covering:
- Story 1: ...
- Story 2: ...
- Story 3: ...

[TRANSITION MUSIC]

HOST: First up, [story title]...

[STORY DETAILS - 60-90 seconds]

HOST: Moving on to our next story...

[OUTRO MUSIC - 15 seconds]

HOST: That's all for today. Thanks for listening, and see you tomorrow!
```

**Prompt Template**:
```python
SYSTEM_PROMPT = """
You are a professional podcast host with 10 years of experience.
Your style is: friendly, engaging, clear, and informative.
You speak at a moderate pace with natural pauses.
"""

USER_PROMPT = """
Create a podcast script from these BBC news articles:

{articles_text}

Requirements:
- Total length: 3-5 minutes (400-600 words)
- Structure: Intro (30s) + 2-3 stories (60-90s each) + Outro (30s)
- Tone: Conversational, professional but friendly
- Include: [MUSIC] cues, speaker labels (HOST:), transitions
- Add brief pauses indicated by "..."
- No complex jargon, explain if needed
- End with a friendly sign-off

Format as Markdown with clear sections.
"""

def generate_script(articles):
    # 1. Format articles into text
    articles_text = format_articles_for_prompt(articles)

    # 2. Call OpenAI API
    response = openai.ChatCompletion.create(
        model=config.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT.format(articles_text)}
        ],
        temperature=config.OPENAI_TEMPERATURE,
        max_tokens=config.MAX_TOKENS
    )

    # 3. Extract script
    script = response.choices[0].message.content

    # 4. Save
    filename = f"script_{date.today()}.md"
    save_script(script, f"data/processed/{filename}")

    return script
```

**Error Handling**:
- Retry 3 lần nếu API fails
- Fallback: Dùng template mặc định nếu hết token/error
- Log token usage: `prompt_tokens`, `completion_tokens`, `total_tokens`

**Dependencies**:
- `openai` - OpenAI API client
- `tiktoken` - Token counting (optional)

---

### 2.3 TTS Converter Module (`src/tts_converter.py`)

**Trách nhiệm**:
- Đọc script từ `data/processed/`
- Gọi TTS API (ElevenLabs hoặc OpenAI)
- Chia chunk nếu script quá dài (ElevenLabs limit: 5000 chars)
- Lưu MP3 vào `output/`

**Input**: Script text (Markdown)
**Output**: MP3 file

**Chunking Strategy** (ElevenLabs):
```python
def chunk_script(script, max_chars=5000):
    # Split by paragraphs or sentences
    paragraphs = script.split('\n\n')
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) > max_chars:
            chunks.append(current_chunk)
            current_chunk = para
        else:
            current_chunk += "\n\n" + para if current_chunk else para

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def convert_to_speech(script, output_path):
    if config.TTS_PROVIDER == 'elevenlabs':
        chunks = chunk_script(script)
        audio_chunks = []

        for chunk in chunks:
            audio = call_elevenlabs(chunk)
            audio_chunks.append(audio)

        # Concatenate audio chunks
        final_audio = b''.join(audio_chunks)
        save_mp3(final_audio, output_path)

    elif config.TTS_PROVIDER == 'openai':
        response = openai.audio.speech.create(
            model='tts-1',  # or 'tts-1-hd'
            voice=config.OPENAI_VOICE,
            input=script
        )
        response.stream_to_file(output_path)

    elif config.TTS_PROVIDER == 'gtts':
        tts = gTTS(text=script, lang='en', slow=False)
        tts.save(output_path)
```

**API Calls**:

**ElevenLabs**:
```python
def call_elevenlabs(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{config.ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": config.ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    response = requests.post(url, json=data, headers=headers, stream=True)

    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"ElevenLabs API error: {response.text}")
```

**OpenAI TTS**:
```python
from openai import OpenAI

client = OpenAI(api_key=config.OPENAI_API_KEY)

response = client.audio.speech.create(
    model='tts-1',  # 'tts-1' (standard) or 'tts-1-hd' (high quality)
    voice=config.OPENAI_VOICE,  # 'alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'
    input=text,
    response_format='mp3'
)
```

**Error Handling**:
- Retry 3 lần với exponential backoff
- Validate script không rỗng trước khi gọi API
- Log file size, duration estimate

**Dependencies**:
- `requests` - HTTP calls
- `openai` - OpenAI TTS
- `gTTS` - Google TTS (optional)
- `pydub` - Audio manipulation (optional, để concatenate chunks)

---

### 2.4 GitHub Uploader Module (`src/github_uploader.py`)

**Trách nhiệm**:
- Connect to GitHub qua PyGithub
- Upload MP3 lên branch `gh-pages`
- Tạo/update `index.html` với audio player
- Commit với message ngày tháng

**Input**: MP3 file path
**Output**: Public URL trên GitHub Pages

**Implementation**:
```python
from github import Github

def upload_to_github(mp3_path, date_str):
    # 1. Authenticate
    g = Github(config.GITHUB_TOKEN)
    repo = g.get_repo(config.GITHUB_REPO)  # "username/repo-name"

    # 2. Read MP3 file
    with open(mp3_path, 'rb') as f:
        mp3_content = f.read()

    # 3. Upload MP3
    mp3_filename = f"podcast_{date_str}.mp3"
    mp3_path_in_repo = f"output/{mp3_filename}"

    try:
        # Try to create file (first time)
        repo.create_file(
            path=mp3_path_in_repo,
            message=f"Add podcast {date_str}",
            content=mp3_content,
            branch="gh-pages"
        )
    except:
        # File exists, update it
        contents = repo.get_contents(mp3_path_in_repo, ref="gh-pages")
        repo.update_file(
            path=mp3_path_in_repo,
            message=f"Update podcast {date_str}",
            content=mp3_content,
            sha=contents.sha,
            branch="gh-pages"
        )

    # 4. Update index.html with latest podcast
    update_index_html(repo, mp3_filename, date_str)

    # 5. Return public URL
    return f"https://{config.GITHUB_USERNAME}.github.io/{config.GITHUB_REPO_NAME}/{mp3_path_in_repo}"
```

**index.html template**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>BBC News AI Podcast</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .player { background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0; }
        audio { width: 100%; }
        .date { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>🎙️ BBC News AI Podcast</h1>
    <p>Latest episode: <strong id="date">2024-01-15</strong></p>

    <div class="player">
        <audio controls>
            <source src="output/podcast_latest.mp3" type="audio/mpeg">
            Your browser does not support the audio element.
        </audio>
        <p><a href="output/podcast_latest.mp3">Download MP3</a></p>
    </div>

    <h2>📜 Archive</h2>
    <ul id="archive">
        <li><a href="output/podcast_2024-01-14.mp3">2024-01-14</a></li>
        <li><a href="output/podcast_2024-01-13.mp3">2024-01-13</a></li>
    </ul>
</body>
</html>
```

**Error Handling**:
- Validate GitHub token trước khi upload
- Retry 3 lần nếu network error
- Log commit SHA, URL

**Dependencies**:
- `PyGithub` - Official GitHub API library

---

## 3. Data Flow & Control Flow

### 3.1 Main Pipeline (`main.py`)

```python
import logging
from datetime import datetime
from src import data_ingestion, script_generator, tts_converter, github_uploader

def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    date_str = datetime.now().strftime("%Y-%m-%d")

    try:
        # STEP 1: Data Ingestion
        logger.info("Step 1: Fetching articles from BBC News...")
        articles = data_ingestion.fetch_articles()
        if not articles:
            logger.error("No articles fetched. Exiting.")
            return

        logger.info(f"Fetched {len(articles)} articles")

        # STEP 2: Script Generation
        logger.info("Step 2: Generating podcast script...")
        script = script_generator.generate_script(articles)
        script_path = f"data/processed/script_{date_str}.md"

        # STEP 3: TTS Conversion
        logger.info("Step 3: Converting script to speech...")
        mp3_path = f"output/podcast_{date_str}.mp3"
        tts_converter.convert_to_speech(script, mp3_path)

        # STEP 4: GitHub Upload
        logger.info("Step 4: Uploading to GitHub Pages...")
        public_url = github_uploader.upload_to_github(mp3_path, date_str)
        logger.info(f"Podcast published: {public_url}")

        # Create symlink for latest
        create_latest_symlink(mp3_path, "output/podcast_latest.mp3")

        logger.info("Pipeline completed successfully!")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
```

### 3.2 Data Flow Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                         main.py                                 │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ 1. data_ingestion.fetch_articles()                   │    │
│  │    - Read RSS feed                                   │    │
│  │    - Scrape full content                             │    │
│  │    - Save: data/articles/articles_YYYY-MM-DD.json   │    │
│  └──────────────────────────────────────────────────────┘    │
│                          │                                     │
│                          ▼                                     │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ 2. script_generator.generate_script(articles)        │    │
│  │    - Call OpenAI API                                 │    │
│  │    - Format podcast script                          │    │
│  │    - Save: data/processed/script_YYYY-MM-DD.md      │    │
│  └──────────────────────────────────────────────────────┘    │
│                          │                                     │
│                          ▼                                     │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ 3. tts_converter.convert_to_speech(script)          │    │
│  │    - Call TTS API (ElevenLabs/OpenAI)               │    │
│  │    - Chunk if needed                                │    │
│  │    - Save: output/podcast_YYYY-MM-DD.mp3            │    │
│  └──────────────────────────────────────────────────────┘    │
│                          │                                     │
│                          ▼                                     │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ 4. github_uploader.upload_to_github(mp3_path)       │    │
│  │    - Connect to GitHub                              │    │
│  │    - Upload MP3 to gh-pages branch                  │    │
│  │    - Update index.html                              │    │
│  │    - Return: public URL                             │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 4. Configuration Management

### 4.1 Config File (`config.py`)

```python
import os
from dotenv import load_dotenv

load_dotenv()

# ========== RSS FEEDS ==========
RSS_FEEDS = [
    'http://feeds.bbci.co.uk/news/rss.xml',
    'http://feeds.bbci.co.uk/news/world/rss.xml',
    'http://feeds.bbci.co.uk/news/technology/rss.xml'
]

# ========== OPENAI ==========
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = 'gpt-3.5-turbo'
OPENAI_TEMPERATURE = 0.7
MAX_TOKENS = 1000

# ========== TTS ==========
TTS_PROVIDER = os.getenv('TTS_PROVIDER', 'elevenlabs')  # 'elevenlabs', 'openai', 'gtts'

# ElevenLabs
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', '21m00Tcm4TlvDq8ikWAM')  # Bella

# OpenAI TTS
OPENAI_VOICE = os.getenv('OPENAI_VOICE', 'alloy')  # alloy, echo, fable, onyx, nova, shimmer
OPENAI_TTS_MODEL = 'tts-1'  # 'tts-1' or 'tts-1-hd'

# ========== GITHUB ==========
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'username/repo-name')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME', 'username')
GITHUB_REPO_NAME = os.getenv('GITHUB_REPO_NAME', 'repo-name')

# ========== PATHS ==========
DATA_DIR = 'data'
ARTICLES_DIR = f'{DATA_DIR}/articles'
PROCESSED_DIR = f'{DATA_DIR}/processed'
OUTPUT_DIR = 'output'
LOGS_DIR = 'logs'

# ========== SETTINGS ==========
PODCAST_DURATION_TARGET = 300  # seconds (5 minutes)
MAX_ARTICLES_PER_PODCAST = 5
RECENT_HOURS = 24  # Only articles from last 24h
```

### 4.2 Environment Variables (`.env`)

```env
# Required
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
ELEVENLABS_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxx

# Optional (overrides defaults)
TTS_PROVIDER=elevenlabs
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
OPENAI_VOICE=alloy
GITHUB_REPO=vanph/podcast-ai-transformer
```

---

## 5. Error Handling Strategy

### 5.1 Retry Logic

```python
import time
from functools import wraps

def retry(max_attempts=3, delay=1, backoff=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            current_delay = delay

            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise
                    logger.warning(f"Attempt {attempts} failed: {e}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator

# Usage
@retry(max_attempts=3, delay=1)
def call_openai_api(messages):
    return openai.ChatCompletion.create(messages=messages)
```

### 5.2 Error Types & Handling

| Error Type | Cause | Handling Strategy |
|------------|-------|-------------------|
| **NetworkError** | Internet disconnected, timeout | Retry 3x with backoff, log error |
| **API Rate Limit** | Too many API calls | Sleep 60s, retry, log warning |
| **API Auth Error** | Invalid API key | Fail fast, alert user via log |
| **Empty Content** | Article not accessible | Skip article, continue with others |
| **TTS Chunk Too Large** | Script > 5000 chars | Auto-split into chunks |
| **GitHub Upload Fail** | Token invalid, repo not found | Save locally, retry next run |
| **Disk Full** | No storage space | Fail fast, alert user |

### 5.3 Logging Strategy

```python
import logging
from datetime import datetime

def setup_logging():
    log_file = f"logs/app_{datetime.now().strftime('%Y-%m-%d')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Console output
        ]
    )

# Usage in modules
logger = logging.getLogger(__name__)
logger.info("Fetching articles...")
logger.error("Failed to fetch: %s", error_msg)
logger.warning("API rate limit reached, sleeping...")
```

**Log levels**:
- `INFO`: Normal operations, step completions
- `WARNING`: Recoverable issues (rate limit, retry)
- `ERROR`: Failed operations but pipeline continues
- `CRITICAL`: Pipeline abort, needs manual intervention

---

## 6. Security Considerations

### 6.1 API Keys Management
- **Never commit** `.env` file to Git (add to `.gitignore`)
- Use `python-dotenv` to load from `.env`
- Rotate keys periodically (OpenAI/ElevenLabs dashboard)
- Use separate keys for dev vs production (optional)

**.gitignore**:
```
.env
*.mp3
data/
output/
logs/
__pycache__/
*.pyc
.DS_Store
```

### 6.2 GitHub Token Permissions
When creating Personal Access Token (PAT), select only:
- `repo` (Full control of private repositories) - needed for push
- `public_repo` (if using public repo only)

**Do NOT grant**:
- `admin` (unnecessary)
- `delete_repo` (dangerous)
- `workflow` (unless using GitHub Actions)

### 6.3 Input Validation
- Validate RSS feed content before processing
- Check article content length > 100 chars (skip empty)
- Sanitize script text before TTS (remove special chars if needed)
- Limit max articles to prevent excessive API usage

---

## 7. Scalability & Future Enhancements

### 7.1 Current Limitations
- **Single source**: Only BBC News
- **Single article limit**: Max 5 articles per podcast
- **No database**: No history tracking
- **No monitoring**: No alerts if pipeline fails
- **No queue**: Sequential processing only

### 7.2 Potential Enhancements

**Level 1: Simple Improvements**
- [ ] Add more RSS sources (CNN, Reuters, AP)
- [ ] Add article deduplication (hash URL)
- [ ] Add podcast metadata (ID3 tags)
- [ ] Add background music (mix with pydub)
- [ ] Add multiple language support

**Level 2: Infrastructure**
- [ ] Use SQLite to store article history
- [ ] Add email notifications (smtplib) on failure
- [ ] Add metrics tracking (prometheus + grafana)
- [ ] Containerize with Docker
- [ ] Deploy to cloud (AWS Lambda, GCP Cloud Functions)

**Level 3: Advanced**
- [ ] Use message queue (Redis, RabbitMQ) for parallel processing
- [ ] Add frontend UI to browse episodes
- [ ] Add RSS feed for podcast (iTunes compatible)
- [ ] Add transcription (Whisper API)
- [ ] Add multi-voice podcast (different voices for different segments)

---

## 8. Testing Strategy

### 8.1 Unit Tests

```python
# tests/test_data_ingestion.py
def test_fetch_articles():
    articles = data_ingestion.fetch_articles()
    assert len(articles) > 0
    assert 'title' in articles[0]
    assert 'content' in articles[0]

# tests/test_script_generator.py
def test_generate_script():
    sample_articles = [{'title': 'Test', 'content': 'Test content'}]
    script = script_generator.generate_script(sample_articles)
    assert 'HOST:' in script
    assert len(script) > 100

# tests/test_tts_converter.py
def test_convert_to_speech():
    script = "Hello, this is a test."
    tts_converter.convert_to_speech(script, 'test.mp3')
    assert os.path.exists('test.mp3')
    assert os.path.getsize('test.mp3') > 1000
```

### 8.2 Integration Test
```python
def test_full_pipeline():
    # Run all steps end-to-end with mock APIs
    # Verify output MP3 exists and is valid
    pass
```

### 8.3 Manual Testing Checklist
- [ ] RSS feed fetch works (check `data/articles/`)
- [ ] Script generation produces reasonable output (check `data/processed/`)
- [ ] TTS produces audible MP3 (listen to `output/`)
- [ ] GitHub upload works (check repo `gh-pages` branch)
- [ ] GitHub Pages displays correctly (check live URL)
- [ ] Cron job runs successfully (check logs)

---

## 9. Deployment Checklist

### 9.1 Pre-deployment
- [ ] All API keys configured in `.env`
- [ ] GitHub repo created and Pages enabled
- [ ] Test run with `--dry-run` flag successful
- [ ] Logs directory exists and writable
- [ ] `.gitignore` configured correctly

### 9.2 Deployment Steps
1. Push code to GitHub main branch
2. Create `gh-pages` branch (if not exists):
   ```bash
   git checkout --orphan gh-pages
   git rm -rf .
   touch .nojekyll
   git add .nojekyll
   git commit -m "Initial gh-pages"
   git push origin gh-pages
   git checkout main
   ```
3. Enable GitHub Pages: Settings → Pages → Source: `gh-pages` branch
4. Run `python main.py` manually once to verify
5. Setup cron job or GitHub Actions

### 9.3 Post-deployment
- [ ] Verify GitHub Pages URL works
- [ ] Check logs for errors
- [ ] Monitor API usage/costs for first week
- [ ] Set up alerts (optional: email on failure)

---

## 10. Monitoring & Maintenance

### 10.1 Daily Checks
- [ ] Cron job executed (check `logs/app_YYYY-MM-DD.log`)
- [ ] New MP3 file in `output/` and GitHub
- [ ] GitHub Pages URL accessible

### 10.2 Weekly Checks
- [ ] Review API usage/costs (OpenAI dashboard, ElevenLabs dashboard)
- [ ] Check for RSS feed structure changes (BBC may update HTML)
- [ ] Clean up old logs (keep 30 days)

### 10.3 Monthly Checks
- [ ] Rotate API keys if needed
- [ ] Update dependencies (`pip list --outdated`)
- [ ] Review GitHub Pages traffic (GitHub Analytics)

---

## Kết luận

Kiến trúc này được thiết kế để:
- **Đơn giản**: Chỉ 4 module chính, dễ hiểu
- **Dễ triển khai**: Mỗi module có thể code và test riêng
- **Dễ bảo trì**: Code rõ ràng, logging đầy đủ
- **Dễ mở rộng**: Thêm source, TTS, deploy target dễ dàng

**Next step**: Bắt đầu code theo từng module theo thứ tự:
1. `config.py` + `.env`
2. `src/data_ingestion.py`
3. `src/script_generator.py`
4. `src/tts_converter.py`
5. `src/github_uploader.py`
6. `main.py` (integrate all)
7. Test end-to-end
8. Setup automation (cron/GitHub Actions)