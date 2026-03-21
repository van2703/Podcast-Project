# BBC News AI Podcast Transformer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-brightgreen)](https://vanph.github.io/podcast-ai-transformer)
[![OpenAI GPT](https://img.shields.io/badge/OpenAI-GPT--3.5-green)](https://platform.openai.com)
[![ElevenLabs](https://img.shields.io/badge/ElevenLabs-TTS-orange)](https://elevenlabs.io)

> Tự động chuyển tin tức BBC thành podcast hàng ngày bằng AI - Dự án cá nhân đơn giản, dễ triển khai

## 🎯 Tính năng

- ✅ **Tự động thu thập**: Quét và tải bài báo mới từ BBC News mỗi ngày
- ✅ **AI biên tập**: GPT-3.5 Turbo tạo kịch bản podcast tự nhiên, thân thiện
- ✅ **Chất lượng cao**: Text-to-Speech với ElevenLabs hoặc OpenAI TTS
- ✅ **Tự động deploy**: Upload MP3 lên GitHub Pages, có sẵn public URL
- ✅ **Đơn giản**: Code Python cơ bản, dễ hiểu, dễ bảo trì
- ✅ **Chi phí thấp**: Sử dụng free tier, ước tính < $5/tháng

## 🎧 Demo Podcast

Nghe podcast mẫu (tự động update mỗi ngày):

👉 **[BBC News Daily - Latest Episode](https://vanph.github.io/podcast-ai-transformer/output/podcast_latest.mp3)**

*Lưu ý: Podcast được tạo tự động mỗi sáng lúc 8h (UTC+7)*

## 🛠️ Công nghệ sử dụng

| Thành phần | Công nghệ | Mục đích |
|------------|-----------|----------|
| **Backend** | Python 3.9+ | Ngôn ngữ chính |
| **AI Script** | OpenAI GPT-3.5 Turbo | Tạo kịch bản podcast |
| **TTS** | ElevenLabs API / OpenAI TTS | Chuyển text → speech |
| **Data Source** | BBC News RSS | Nguồn tin tức |
| **Scraping** | BeautifulSoup 4 | Lấy nội dung bài báo |
| **GitHub** | PyGithub | Upload file tự động |
| **Hosting** | GitHub Pages | Phát phát miễn phí |

## 📦 Cài đặt nhanh

### 1. Yêu cầu hệ thống
- Python 3.9 hoặc cao hơn
- Git
- Tài khoản GitHub (có quyền tạo repo)
- API Keys:
  - [OpenAI Platform](https://platform.openai.com/api-keys)
  - [ElevenLabs](https://elevenlabs.io) (hoặc dùng OpenAI TTS)
  - [GitHub Personal Access Token](https://github.com/settings/tokens)

### 2. Clone & Cài đặt

```bash
# Clone repository
git clone https://github.com/vanph/podcast-ai-transformer.git
cd podcast-ai-transformer

# Cài đặt dependencies
pip install -r requirements.txt

# Cấu hình API keys
# Tạo file .env với nội dung:
# OPENAI_API_KEY=sk-...
# ELEVENLABS_API_KEY=...
# GITHUB_TOKEN=ghp_...
```

### 3. Chạy thử nghiệm

```bash
# Dry run (không upload) để test
python main.py --dry-run

# Chạy production (tự động upload)
python main.py
```

## ⚙️ Cấu hình

### File cấu hình chính

**`config.py`** - Các thiết lập chính:
```python
# RSS feed sources
RSS_FEEDS = [
    'http://feeds.bbci.co.uk/news/rss.xml',
    'http://feeds.bbci.co.uk/news/world/rss.xml'
]

# AI settings
OPENAI_MODEL = 'gpt-3.5-turbo'
OPENAI_TEMPERATURE = 0.7
MAX_TOKENS = 1000

# TTS settings
TTS_PROVIDER = 'elevenlabs'  # 'elevenlabs' hoặc 'openai'
ELEVENLABS_VOICE_ID = '21m00Tcm4TlvDq8ikWAM'  # Bella (female)
OPENAI_VOICE = 'alloy'  # alloy, echo, fable, onyx, nova, shimmer

# Output settings
PODCAST_DURATION_TARGET = 300  # seconds (5 phút)
OUTPUT_DIR = 'output'
```

**`.env`** - API keys (không commit):
```env
OPENAI_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here
GITHUB_TOKEN=your_github_pat_here
```

## 📁 Cấu trúc dự án

```
podcast-ai-transformer/
├── README.md                    # Tài liệu chính (bạn đang đọc)
├── requirement_spec.md          # Bản đặc tả yêu cầu chi tiết
├── architecture_design.md       # Thiết kế kiến trúc hệ thống
├── main.py                      # Script chính điều phối pipeline
├── config.py                    # Cấu hình chính
├── requirements.txt             # Python dependencies
├── .env.example                 # Template cho environment variables
├── .gitignore
├── src/                         # Source code modules
│   ├── __init__.py
│   ├── data_ingestion.py       # Tải bài báo từ BBC RSS
│   ├── script_generator.py     # Tạo kịch bản bằng GPT
│   ├── tts_converter.py        # Chuyển text-to-speech
│   ├── github_uploader.py      # Upload lên GitHub Pages
│   └── utils.py                # Helper functions (logging, config)
├── data/                       # Dữ liệu trung gian
│   ├── articles/              # Bài báo tải về (JSON)
│   └── processed/             # Kịch bản đã tạo (Markdown)
├── output/                    # File MP3 đầu ra
│   └── podcast_latest.mp3     # File mới nhất (symlink)
├── logs/                      # Log files
│   └── app_2024-01-15.log
└── tests/                     # Unit tests (optional)
```

## 🚀 Workflow hoạt động

```mermaid
graph LR
    A[BBC News RSS] --> B[Data Ingestion]
    B --> C[Local Storage<br/>data/articles/]
    C --> D[Script Generator<br/>GPT-3.5 Turbo]
    D --> E[Script File<br/>data/processed/]
    E --> F[TTS Converter<br/>ElevenLabs/OpenAI]
    F --> G[MP3 File<br/>output/]
    G --> H[GitHub Uploader]
    H --> I[GitHub Pages<br/>Public URL]
```

**Chi tiết từng bước**:

1. **Data Ingestion** (`src/data_ingestion.py`)
   - Fetch RSS feed từ BBC News
   - Lọc bài mới trong 24h
   - Tải nội dung đầy đủ bằng BeautifulSoup
   - Lưu vào `data/articles/*.json`

2. **Script Generation** (`src/script_generator.py`)
   - Đọc các bài báo từ `data/articles/`
   - Gửi prompt đến OpenAI GPT-3.5
   - Tạo kịch bản podcast có cấu trúc (intro, segments, outro)
   - Lưu script vào `data/processed/script_YYYY-MM-DD.md`

3. **Text-to-Speech** (`src/tts_converter.py`)
   - Đọc script từ file
   - Gọi TTS API (ElevenLabs hoặc OpenAI)
   - Chia chunk nếu script quá dài
   - Xuất MP3 vào `output/podcast_YYYY-MM-DD.mp3`

4. **GitHub Upload** (`src/github_uploader.py`)
   - Kết nối GitHub qua PyGithub
   - Upload MP3 lên branch `gh-pages`
   - Tạo/update `index.html` với audio player
   - Commit với message ngày tháng

## 📅 Tự động hóa

### Linux/Mac (cron job)

```bash
# Mở crontab
crontab -e

# Thêm dòng này (chạy mỗi ngày 8h sáng UTC+7)
0 8 * * * cd /path/to/podcast-ai-transformer && /usr/bin/python3 main.py >> logs/cron.log 2>&1
```

### Windows (Task Scheduler)

1. Mở **Task Scheduler**
2. Click **Create Basic Task**
3. Name: `BBC Podcast Generator`
4. Trigger: **Daily**, 8:00 AM
5. Action: **Start a program**
   - Program: `python.exe` (hoặc full path)
   - Arguments: `D:\path\to\podcast-ai-transformer\main.py`
6. Finish

### GitHub Actions (Alternative)

Tạo file `.github/workflows/daily.yml`:
```yaml
name: Daily Podcast Generation
on:
  schedule:
    - cron: '0 1 * * *'  # 1h UTC = 8h UTC+7
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Generate podcast
        run: python main.py
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 📊 Chi phí ước tính

| Dịch vụ | Free Tier | Chi phí thực tế |
|---------|-----------|-----------------|
| OpenAI GPT-3.5 | $18/tháng credits (mới) | ~$2-5/tháng (1 bài/ngày) |
| ElevenLabs TTS | 10k chars/tháng | ~$5/tháng (Starter plan) |
| OpenAI TTS | Không có free tier | ~$1-3/tháng |
| GitHub Pages | Miễn phí | $0 |
| **Tổng ước tính** | | **$5-10/tháng** |

*Lưu ý: Chi phí có thể thay đổi tùy usage. Bạn có thể dùng Google TTS (free) để giảm chi phí về ~$2-3/tháng.*

## 🐛 Xử lý lỗi thường gặp

### Lỗi "API rate limit exceeded"
- **Nguyên nhân**: Gọi API quá nhiều lần
- **Giải pháp**: Thêm `time.sleep(1)` giữa các API calls, hoặc nâng cấp plan

### Lỗi "Article content empty"
- **Nguyên nhân**: BBC thay đổi HTML structure
- **Giải pháp**: Kiểm tra và cập nhật CSS selectors trong `data_ingestion.py`

### Lỗi "GitHub upload failed"
- **Nguyên nhân**: Token không có quyền, hoặc repo không bật Pages
- **Giải pháp**:
  1. Kiểm tra token có quyền `repo` scope
  2. Vào repo Settings → Pages → Source: chọn `gh-pages` branch

### Lỗi "TTS chunk too large"
- **Nguyên nhân**: Script quá dài (>5000 chars với ElevenLabs)
- **Giải pháp**: Tự động chunk script trong `tts_converter.py`

## 📝 License

MIT License - xem file [LICENSE](LICENSE) để biết thêm chi tiết.

Copyright © 2024 [Van Ph](https://github.com/vanph)

## 🙏 Credits & Inspiration

- **BBC News** - Nguồn tin tức chất lượng
- **OpenAI** - GPT-3.5 Turbo cho script generation
- **ElevenLabs** - Voice AI công nghệ cao
- **GitHub** - Miễn phí hosting cho cộng đồng

---

**Made with ❤️ and AI** | [⭐ Star nếu bạn thấy dự án hữu ích](https://github.com/vanph/podcast-ai-transformer/stargazers)