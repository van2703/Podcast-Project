# 🚀 Getting Started - BBC News AI Podcast Transformer

Hướng dẫn nhanh để bắt đầu với dự án trong 15 phút.

## 📋 Yêu cầu trước khi bắt đầu

- [x] Python 3.9+ đã cài đặt
- [x] Tài khoản GitHub (có quyền tạo repo)
- [x] API Key từ [OpenAI](https://platform.openai.com/api-keys)
- [x] API Key từ [ElevenLabs](https://elevenlabs.io) (hoặc dùng OpenAI TTS)
- [x] GitHub Personal Access Token (PAT) - [hướng dẫn](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

## ⚡ Bắt đầu nhanh (5 bước)

### Bước 1: Clone repository

```bash
git clone https://github.com/vanph/podcast-ai-transformer.git
cd podcast-ai-transformer
```

### Bước 2: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 3: Cấu hình API keys

Tạo file `.env` trong thư mục gốc:

```env
OPENAI_API_KEY=sk-your-openai-key-here
ELEVENLABS_API_KEY=your-elevenlabs-key-here
GITHUB_TOKEN=ghp-your-github-pat-here
```

**Lưu ý**: File `.env` sẽ không được commit lên Git. Đây là file chứa secrets.

### Bước 4: Cấu hình GitHub repo

Mở file `config.py` và sửa các dòng sau:

```python
GITHUB_REPO = 'your-username/your-repo-name'  # Thay bằng username và repo của bạn
GITHUB_USERNAME = 'your-username'
GITHUB_REPO_NAME = 'your-repo-name'
```

### Bước 5: Chạy thử nghiệm

```bash
# Dry run - không upload lên GitHub
python main.py --dry-run

# Nếu thành công, chạy production
python main.py
```

Sau khi chạy thành công, bạn sẽ thấy:
- File MP3 trong thư mục `output/`
- File kịch bản trong `data/processed/`
- File bài báo trong `data/articles/`

## 🎯 Test GitHub Pages

1. **Tạo repo trên GitHub** (nếu chưa có):
   - Vào https://github.com/new
   - Đặt tên: `podcast-ai-transformer`
   - Chọn Public (để Pages hoạt động miễn phí)
   - Tạo repo

2. **Push code lên GitHub**:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-username/podcast-ai-transformer.git
git push -u origin main
```

3. **Tạo branch `gh-pages`**:
```bash
git checkout --orphan gh-pages
git rm -rf .
touch .nojekyll
git add .nojekyll
git commit -m "Initial gh-pages"
git push origin gh-pages
git checkout main
```

4. **Bật GitHub Pages**:
   - Vào repo Settings → Pages
   - Source: chọn `gh-pages` branch
   - Save
   - URL sẽ hiển thị: `https://your-username.github.io/podcast-ai-transformer/`

5. **Test upload**:
```bash
python main.py
```
Sau vài phút, truy cập URL GitHub Pages để xem podcast.

## 🔄 Tự động hóa

### Linux/Mac (Cron)

Mở crontab:
```bash
crontab -e
```

Thêm dòng này (chạy mỗi ngày 8h sáng UTC+7):
```bash
0 8 * * * cd /path/to/podcast-ai-transformer && /usr/bin/python3 main.py >> logs/cron.log 2>&1
```

### Windows (Task Scheduler)

1. Mở **Task Scheduler** (tìm trong Start menu)
2. Click **Create Basic Task**
3. Name: `BBC Podcast Generator`
4. Trigger: **Daily**, 8:00 AM
5. Action: **Start a program**
   - Program: `python.exe` (hoặc browse đến Python install path)
   - Arguments: `D:\path\to\podcast-ai-transformer\main.py`
6. Finish

### GitHub Actions (Khuyến nghị)

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

Thêm secrets vào GitHub repo:
- Settings → Secrets and variables → Actions → New repository secret
- `OPENAI_API_KEY`: your OpenAI key
- `ELEVENLABS_API_KEY`: your ElevenLabs key
- `GITHUB_TOKEN`: your GitHub PAT

## 🐛 Xử lý sự cố

### Lỗi "Module not found"
```bash
pip install -r requirements.txt
```

### Lỗi "API key invalid"
- Kiểm tra file `.env` có đúng key không
- Kiểm tra key còn hạn (OpenAI/ElevenLabs dashboard)

### Lỗi "No articles fetched"
- Kiểm tra internet connection
- BBC RSS feed có thể thay đổi structure - xem logs trong `logs/`

### Lỗi "GitHub upload failed"
- Kiểm tra GitHub token có quyền `repo`
- Kiểm tra repo đã bật Pages (Settings → Pages)
- Kiểm tra branch `gh-pages` tồn tại

### Lỗi "TTS chunk too large"
Script quá dài, hệ thống sẽ tự động chia chunk. Nếu vẫn lỗi, giảm số bài báo trong config:
```python
MAX_ARTICLES_PER_PODCAST = 3  # Thay vì 5
```

## 📊 Kiểm tra logs

Logs được lưu trong thư mục `logs/`:
- `app_YYYY-MM-DD.log` - Log chính
- `ingestion_YYYY-MM-DD.log` - Log data ingestion
- `cron.log` - Log từ cron job (nếu dùng)

Xem log realtime:
```bash
tail -f logs/app_$(date +%Y-%m-%d).log
```

Windows:
```cmd
type logs\app_$(date /t).log
```

## 🎧 Nghe podcast

Sau khi upload thành công, podcast có thể nghe tại:
- GitHub Pages: `https://your-username.github.io/podcast-ai-transformer/output/podcast_latest.mp3`
- Hoặc download trực tiếp từ repo: `output/podcast_YYYY-MM-DD.mp3`

## 📚 Tài liệu tham khảo

- [requirement_spec.md](requirement_spec.md) - Bản đặc tả yêu cầu chi tiết
- [architecture_design.md](architecture_design.md) - Thiết kế kiến trúc
- [README.md](README.md) - Tài liệu chính

## 🆘 Cần trợ giúp?

1. Kiểm tra [Issues](https://github.com/vanph/podcast-ai-transformer/issues) xem đã có solution chưa
2. Tạo issue mới với mô tả chi tiết và logs
3. Hoặc liên hệ: [@vanph](https://github.com/vanph)

---

**Chúc bạn thành công với dự án AI podcast đầu tiên!** 🎉