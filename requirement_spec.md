# BBC News AI Podcast Transformer - Requirement Specification

## Chương 1: Giới thiệu dự án & Mục tiêu

### 1.1 Tổng quan dự án
Dự án "BBC News AI Podcast Transformer" là một hệ thống tự động chuyển đổi tin tức từ BBC News thành podcast audio. Hệ thống sẽ tự động:
- Quét và tải bài báo mới từ BBC News mỗi ngày
- Biên tập nội dung thành kịch bản podcast
- Chuyển kịch bản thành giọng nói (file MP3)
- Upload tự động lên GitHub Pages

### 1.2 Mục tiêu chính
- **Tự động hóa hoàn toàn**: Chạy hàng ngày mà không cần can thiệp thủ công
- **Đơn giản**: Sử dụng các công cụ có sẵn, API phổ biến, tránh thuật toán phức tạp
- **Dễ bảo trì**: Code rõ ràng, có documentation đầy đủ
- **Chi phí thấp**: Ưu tiên các API có free tier hoặc chi phí hợp lý
- **Tích hợp GitHub**: Kết quả tự động publish lên GitHub Pages

### 1.3 Phạm vi dự án
- **Bao gồm**: Data ingestion từ BBC News, script generation, TTS, deployment lên GitHub
- **Không bao gồm**: Frontend UI, database lưu trữ lịch sử, quản lý user, analytics

---

## Chương 2: Luồng xử lý chi tiết (Workflow)

### 2.1 Workflow tổng thể
```
[BBC News RSS/API] → [Download Articles] → [Local Storage] → [Script Generation] → [TTS Conversion] → [MP3 File] → [GitHub Upload] → [GitHub Pages]
```

### 2.2 Chi tiết từng bước

#### Bước 1: Data Ingestion (Thu thập dữ liệu)
- **Input**: BBC News RSS feed hoặc scraped HTML
- **Process**:
  - Kết nối đến BBC News RSS feed (ví dụ: `http://feeds.bbci.co.uk/news/rss.xml`)
  - Hoặc scrape trang BBC News bằng BeautifulSoup
  - Lọc bài báo mới trong 24h qua
  - Tải nội dung đầy đủ (title, content, summary, date)
- **Output**: Các file `.txt` hoặc `.json` lưu trong folder `data/articles/`
- **Lưu ý**: Thêm metadata (URL, publish date) để tránh duplicate

#### Bước 2: Script Generation (Tạo kịch bản)
- **Input**: Các file bài báo từ folder `data/articles/`
- **Process**:
  - Đọc và phân tích nội dung các bài báo
  - Sử dụng AI (GPT) để:
    - Tóm tắt và chọn tin quan trọng nhất
    - Viết lại thành kịch bản dạng podcast (giọng văn tự nhiên, có intro/outro)
    - Tạo lời dẫn, chuyển đoạn mượt mà
    - Độ dài target: 3-5 phút (khoảng 400-600 từ)
  - Format kịch bản: có speaker notes, nhịp điệu, emphasis
- **Output**: File `script_today.md` hoặc `script_today.txt` trong folder `scripts/`
- **Template mẫu**:
  ```
  [INTRO MUSIC]
  HOST: Xin chào, hôm nay chúng ta có các tin tức nóng...
  [TRANSITION]
  HOST: Tin số một: [tiêu đề]...
  [OUTRO MUSIC]
  ```

#### Bước 3: Text-to-Speech (Chuyển văn bản thành giọng nói)
- **Input**: File kịch bản từ `scripts/`
- **Process**:
  - Gửi nội dung kịch bản đến TTS API
  - Chọn voice phù hợp (giọng Anh, trung tính hoặc nam/nữ)
  - Tối ưu hóa: thêm pauses, điều chỉnh speed
  - Tích hợp nhạc nền (optional)
- **Output**: File `podcast_today.mp3` trong folder `output/`
- **Format**: MP3, bitrate 128kbps, mono hoặc stereo

#### Bước 4: Deployment (Upload lên GitHub)
- **Input**: File MP3 từ `output/`
- **Process**:
  - Sử dụng PyGithub để commit file vào repository
  - Push lên branch `gh-pages` hoặc thư mục `docs/`
  - Tạo/update index.html để hiển thị player
  - Commit message mẫu: "Add podcast for YYYY-MM-DD"
- **Output**: File MP3 và index.html có sẵn trên GitHub Pages
- **URL mẫu**: `https://username.github.io/repo-name/podcast_today.mp3`

### 2.3 Luồng xử lý lỗi
- **Nếu không lấy được bài báo**: Log lỗi, tiếp tục với bài khác
- **Nếu GPT API lỗi**: Retry 3 lần, sau đó dùng template mặc định
- **Nếu TTS API lỗi**: Retry, hoặc dùng Google TTS fallback
- **Nếu GitHub upload lỗi**: Log và lưu local, chờ upload lại lần sau

---

## Chương 3: Lựa chọn công nghệ

### 3.1 Tổng quan công nghệ đề xuất
| Thành phần | Công nghệ đề xuất | Lý do | Chi phí |
|------------|-------------------|-------|---------|
| Data Ingestion | BeautifulSoup + Requests | Đơn giản, không cần API key | Free |
| Script Generation | OpenAI GPT-3.5 Turbo | Chất lượng tốt, giá rẻ | ~$0.002/1k tokens |
| TTS | ElevenLabs API hoặc Google TTS | Chất lượng cao, dễ dùng | ElevenLabs: ~$5/tháng<br>Google TTS: Free tier |
| GitHub Upload | PyGithub | Library chính thức, ổn định | Free |
| Scheduling | Python schedule/cron | Đơn giản, không cần extra tool | Free |

### 3.2 Chi tiết từng thành phần

#### Data Ingestion
**Lựa chọn 1: BBC RSS Feed (Khuyến nghị)**
```python
import feedparser
feed = feedparser.parse('http://feeds.bbci.co.uk/news/rss.xml')
# Lấy entries, filter by date, tải nội dung
```
- **Ưu điểm**: Có sẵn, free, dễ parse
- **Nhược điểm**: Có thể thiếu chi tiết, cần follow link để lấy full content

**Lựa chọn 2: Web Scraping**
```python
import requests
from bs4 import BeautifulSoup
response = requests.get(article_url)
soup = BeautifulSoup(response.content, 'html.parser')
content = soup.find('div', {'class': 'ssrcss-11r1m41-RichText'})
```
- **Ưu điểm**: Lấy được full content
- **Nhược điểm**: Có thể bị block, cần xử lý HTML phức tạp

**Khuyến nghị**: Dùng RSS feed kết hợp follow link để lấy full content từ mỗi bài.

#### Script Generation
**Model: OpenAI GPT-3.5 Turbo (Khuyến nghị)**
- **API Key**: Lấy từ platform.openai.com
- **Prompt mẫu**:
  ```
  Bạn là một biên tập viên podcast chuyên nghiệp.
  Từ bài báo sau, hãy tạo kịch bản podcast 3-5 phút:
  
  Tiêu đề: {title}
  Nội dung: {content}
  
  Yêu cầu:
  - Giọng văn thân thiện, dễ nghe
  - Có intro (30s) và outro (30s)
  - Chia thành 2-3 tin chính
  - Thêm các cụm chuyển đoạn tự nhiên
  - Độ dài ~500 từ
  ```
- **Ưu điểm**: Chất lượng ổn định, giá rẻ (~$0.002 cho 1k tokens)
- **Alternative**: GPT-4o-mini (nhanh hơn, giá tương tự)

**Lưu ý**: Luôn ghi log token usage để kiểm soát chi phí.

#### Text-to-Speech
**Lựa chọn 1: ElevenLabs (Khuyến nghị cho chất lượng cao)**
```python
import requests
CHUNK_SIZE = 1024
url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
headers = {"xi-api-key": ELEVEN_API_KEY}
data = {"text": script, "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}}
response = requests.post(url, json=data, headers=headers)
with open('output.mp3', 'wb') as f:
    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
        if chunk:
            f.write(chunk)
```
- **Voice đề xuất**: "Bella" (nữ, trung tính) hoặc "Antoni" (nam)
- **Ưu điểm**: Chất lượng rất tự nhiên, nhiều voice options
- **Chi phí**: Free tier 10k chars/tháng, Starter $5/tháng

**Lựa chọn 2: Google TTS (Miễn phí)**
```python
from gtts import gTTS
tts = gTTS(text=script, lang='en', slow=False)
tts.save("output.mp3")
```
- **Ưu điểm**: Free, dễ dùng
- **Nhược điểm**: Chất lượng không bằng ElevenLabs, ít customization

**Lựa chọn 3: OpenAI TTS**
```python
from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)
response = client.audio.speech.create(
    model="tts-1",  # hoặc tts-1-hd
    voice="alloy",  # alloy, echo, fable, onyx, nova, shimmer
    input=script
)
response.stream_to_file("output.mp3")
```
- **Ưu điểm**: Cùng API key với GPT, chất lượng tốt
- **Chi phí**: ~$0.015/1k characters (tts-1)

**Khuyến nghị**: Dùng OpenAI TTS nếu bạn đã có API key, tiện nhất. Hoặc ElevenLabs nếu muốn chất lượng tốt nhất.

#### GitHub Upload
**PyGithub (Khuyến nghị)**
```python
from github import Github
g = Github(GITHUB_TOKEN)
repo = g.get_repo("username/repo-name")
with open('podcast_today.mp3', 'rb') as file:
    content = file.read()
    repo.create_file(
        path="output/podcast_today.mp3",
        message="Add podcast for 2024-01-15",
        content=content,
        branch="gh-pages"
    )
```
- **Cần tạo**: Personal Access Token (PAT) từ GitHub Settings
- **Branch**: Dùng `gh-pages` branch cho GitHub Pages
- **Alternative**: Dùng GitHub Actions thay vì script upload (khuyến nghị cho production)

**Lưu ý**: Đảm bảo repo đã bật GitHub Pages trong Settings → Pages → Source: gh-pages branch.

### 3.3 Các thư viện Python cần thiết
```txt
beautifulsoup4==4.12.2
feedparser==6.0.10
requests==2.31.0
openai==1.3.0
gTTS==2.3.2  # nếu dùng Google TTS
PyGithub==2.1.1
python-dotenv==1.0.0  # quản lý environment variables
schedule==1.2.0  # scheduling local
```

---

## Chương 4: Lộ trình triển khai

### 4.1 Giai đoạn 1: Proof of Concept (1-2 ngày)
**Mục tiêu**: Chạy được end-to-end flow thủ công

**Các bước**:
1. Tạo project structure cơ bản
2. Viết script download 1 bài báo từ BBC RSS
3. Viết script gọi GPT để tạo kịch bản (test với 1 bài)
4. Viết script TTS (dùng Google TTS trước vì free)
5. Upload file MP3 lên GitHub thủ công (test xem Pages hoạt động)

**Kết quả**: 1 file MP3 đầu tiên từ 1 bài báo

### 4.2 Giai đoạn 2: Tích hợp API (1-2 ngày)
**Mục tiêu**: Thay thế Google TTS bằng ElevenLabs/OpenAI TTS

**Các bước**:
1. Đăng ký API key ElevenLabs hoặc dùng OpenAI TTS
2. Cập nhật script TTS
3. Test chất lượng âm thanh
4. Tối ưu prompt cho GPT (test nhiều lần để có kịch bản hay)

**Kết quả**: Chất lượng âm thanh tốt hơn, kịch bản tự nhiên hơn

### 4.3 Giai đoạn 3: Tự động hóa (1 ngày)
**Mục tiêu**: Tự động chạy hàng ngày

**Các bước**:
1. Viết script chính `main.py` điều phối toàn bộ flow
2. Thêm logging đầy đủ
3. Tạo file `.env` cho API keys
4. Setup cron job (Linux/Mac) hoặc Task Scheduler (Windows)
   - Linux: `crontab -e` → `0 8 * * * cd /path && python main.py`
   - Windows: Dùng Task Scheduler chạy `python D:\Workspace\Podcast\main.py` mỗi ngày 8h

**Kết quả**: Hệ thống chạy tự động mỗi ngày

### 4.4 Giai đoạn 4: Tối ưu & Error Handling (1-2 ngày)
**Mục tiêu**: Hệ thống ổn định, ít lỗi

**Các bước**:
1. Thêm retry logic cho API calls
2. Thêm validation (kiểm tra file tồn tại, API key hợp lệ)
3. Gửi email/notification khi có lỗi (optional)
4. Logging to file với timestamps
5. Xử lý duplicate articles (tránh tạo podcast trùng)

**Kết quả**: Hệ thống robust, dễ debug

### 4.5 Giai đoạn 5: Deployment & Documentation (1 ngày)
**Mục tiêu**: Publish lên GitHub, tài liệu chuyên nghiệp

**Các bước**:
1. Tạo repo GitHub public
2. Push code, thêm `.gitignore`
3. Tạo README.md chuyên nghiệp (có badges, demo link)
4. Tạo `requirements.txt`
5. Viết `architecture_design.md` mô tả kiến trúc
6. Test GitHub Pages hoạt động

**Kết quả**: Project sẵn sàng chia sẻ, GitHub profile đẹp

---

## Chương 5: Cấu trúc tài liệu dự án

### 5.1 Cấu trúc thư mục đề xuất
```
podcast-project/
├── README.md                    # Main documentation
├── requirement_spec.md          # Bản SRS này
├── architecture_design.md       # Thiết kế kiến trúc chi tiết
├── main.py                      # Script chính điều phối
├── config.py                    # Config, API keys
├── requirements.txt             # Python dependencies
├── .env.example                 # Template cho environment variables
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── data_ingestion.py       # Module tải bài báo
│   ├── script_generator.py     # Module tạo kịch bản
│   ├── tts_converter.py        # Module chuyển text-to-speech
│   ├── github_uploader.py      # Module upload lên GitHub
│   └── utils.py                # Helper functions
├── data/
│   ├── articles/              # Lưu bài báo tải về
│   └── processed/             # Lưu kịch bản đã xử lý
├── output/                    # Lưu file MP3 đầu ra
├── logs/                     # Log files
└── tests/                   # Unit tests (optional)
```

### 5.2 Hướng dẫn viết README.md chuyên nghiệp

**Cấu trúc README.md đề xuất**:
```markdown
# BBC News AI Podcast Transformer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-brightgreen)](https://username.github.io/repo-name)

> Tự động chuyển tin tức BBC thành podcast hàng ngày bằng AI

## 🎯 Tính năng
- ✅ Tự động tải tin tức mới từ BBC News mỗi ngày
- ✅ AI biên tập thành kịch bản podcast tự nhiên
- ✅ Chuyển văn bản thành giọng nói chất lượng cao
- ✅ Tự động upload lên GitHub Pages

## 🚀 Demo
Nghe podcast mẫu: [BBC News Daily - 2024-01-15](https://username.github.io/repo-name/output/podcast_2024-01-15.mp3)

## 📦 Công nghệ sử dụng
- **Python 3.9+**
- **OpenAI GPT-3.5 Turbo** - Tạo kịch bản
- **ElevenLabs TTS** - Text-to-Speech
- **BeautifulSoup** - Web scraping
- **PyGithub** - GitHub integration
- **GitHub Pages** - Hosting

## 🛠️ Cài đặt

### 1. Clone repository
```bash
git clone https://github.com/username/repo-name.git
cd repo-name
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 3. Cấu hình API keys
Tạo file `.env`:
```env
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key
GITHUB_TOKEN=your_github_pat
```

### 4. Chạy thử
```bash
python main.py
```

## ⚙️ Cấu hình
- `config.py`: Thay đổi RSS feed URL, voice ID, target podcast length
- `src/prompt_templates.py`: Tùy chỉnh prompt cho GPT

## 📅 Tự động hóa
### Linux/Mac (cron)
```bash
crontab -e
# Thêm dòng này (chạy mỗi ngày 8h sáng)
0 8 * * * cd /path/to/repo && python main.py >> logs/cron.log 2>&1
```

### Windows (Task Scheduler)
1. Mở Task Scheduler
2. Create Basic Task
3. Trigger: Daily, 8:00 AM
4. Action: Start a program → `python.exe`
5. Arguments: `D:\path\to\main.py`

## 📁 Cấu trúc dự án
```
podcast-project/
├── src/              # Source code modules
├── data/            # Raw articles & processed scripts
├── output/          # Generated MP3 files
├── logs/            # Execution logs
└── tests/           # Unit tests
```

## 📝 License
MIT © [Your Name](https://github.com/username)
```

### 5.3 Hướng dẫn viết architecture_design.md

**Cấu trúc architecture_design.md đề xuất**:
```markdown
# Kiến trúc hệ thống - BBC News AI Podcast Transformer

## 1. Tổng quan kiến trúc
Hệ thống theo mô hình pipeline đơn giản:
```
[Input: BBC RSS] → [Downloader] → [Storage] → [AI Script Gen] → [TTS] → [Uploader] → [Output: GitHub Pages]
```

## 2. Chi tiết từng module

### 2.1 Data Ingestion Module (`src/data_ingestion.py`)
**Trách nhiệm**:
- Fetch RSS feed từ BBC News
- Parse và lọc bài mới (24h)
- Tải nội dung đầy đủ từ URL
- Lưu vào `data/articles/` dạng JSON

**Input**: RSS feed URL
**Output**: List of article objects (title, content, url, date)
**Error Handling**: Retry 3 lần, skip nếu fail

### 2.2 Script Generator Module (`src/script_generator.py`)
**Trách nhiệm**:
- Đọc articles từ `data/articles/`
- Gọi OpenAI API với prompt template
- Parse response thành kịch bản có cấu trúc
- Lưu script vào `data/processed/`

**Input**: Article JSON files
**Output**: Script file (markdown)
**Prompt Strategy**:
- System prompt: "You are a professional podcast host..."
- User prompt: Article content + format requirements
- Temperature: 0.7 (creative but controlled)

### 2.3 TTS Converter Module (`src/tts_converter.py`)
**Trách nhiệm**:
- Đọc script file
- Gọi TTS API (ElevenLabs/OpenAI)
- Tách thành các chunk nếu script dài (ElevenLabs limit 5000 chars)
- Lưu MP3 vào `output/`

**Input**: Script text
**Output**: MP3 file
**Chunking**: Split by sentences, add pauses between chunks

### 2.4 GitHub Uploader Module (`src/github_uploader.py`)
**Trách nhiệm**:
- Connect to GitHub via PyGithub
- Upload MP3 to `gh-pages` branch
- Update `index.html` với podcast player
- Commit với message ngày

**Input**: MP3 file path
**Output**: Public URL trên GitHub Pages

### 3. Data Flow
```
main.py
  ├── data_ingestion.fetch_articles() → data/articles/*.json
  ├── script_generator.generate_script() → data/processed/script_YYYY-MM-DD.md
  ├── tts_converter.convert_to_speech() → output/podcast_YYYY-MM-DD.mp3
  └── github_uploader.upload() → https://username.github.io/repo/output/podcast_YYYY-MM-DD.mp3
```

## 4. Configuration Management
- **`.env` file**: Lưu trữ API keys (không commit)
- **`config.py`**: Các config constant (RSS URL, voice ID, paths)
- **`requirements.txt`**: Dependencies với version cụ thể

## 5. Error Handling Strategy
- **Network errors**: Retry với exponential backoff
- **API rate limits**: Sleep và retry, log warnings
- **File errors**: Validate trước khi đọc/ghi
- **GitHub errors**: Lưu local, retry ở lần chạy tiếp

## 6. Security Considerations
- **API keys**: Không bao giờ commit vào repo, dùng `.env`
- **GitHub token**: Chỉ có quyền `repo` (read/write), không admin
- **Input validation**: Validate RSS feed content trước khi xử lý

## 7. Scalability Notes
Hiện tại design đơn giản, nhưng có thể mở rộng:
- **Multiple sources**: Thêm RSS từ CNN, Reuters
- **Queue system**: Dùng Redis queue nếu cần xử lý nhiều bài
- **Database**: Lưu history vào SQLite/PostgreSQL
- **Monitoring**: Thêm metrics (Prometheus) và alerts
```

---

## Phụ lục: Mẹo & Best Practices

### A. Quản lý API Keys
- Dùng `python-dotenv`:
```python
from dotenv import load_dotenv
import os
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
```
- Tạo file `.env` (add to `.gitignore`):
```env
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...
GITHUB_TOKEN=ghp_...
```

### B. Logging
```python
import logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### C. Testing
- Test từng module riêng biệt trước khi tích hợp
- Dùng sample articles có sẵn để test script generation
- Test TTS với đoạn văn ngắn trước

### D. Cost Monitoring
- Log token usage từ OpenAI
- Log character count từ TTS
- Set monthly budget alerts trên dashboard

### E. Debugging
- Thêm `--dry-run` flag để test mà không gọi API/upload
- Save intermediate files (articles, script) để inspect
- Dùng `python -m pdb script.py` hoặc VSCode debugger

---

**Kết luận**: Bản SRS này cung cấp đầy đủ thông tin để triển khai dự án với chi phí thấp, độ phức tạp tối thiểu. Ưu tiên thực hiện theo từng giai đoạn, test kỹ từng phần trước khi chuyển sang giai đoạn tiếp theo.