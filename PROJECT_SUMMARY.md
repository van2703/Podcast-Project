# 📋 Tóm tắt dự án - BBC News AI Podcast Transformer

## 🎯 Mục đích
Dự án tự động chuyển tin tức BBC thành podcast hàng ngày, sử dụng AI (GPT + TTS) và deploy lên GitHub Pages.

## 📦 Cấu trúc dự án

```
podcast-ai-transformer/
├── README.md                    # Tài liệu chính, demo, badges
├── requirement_spec.md          # SRS chi tiết (5 chương)
├── architecture_design.md       # Kiến trúc hệ thống
├── GETTING_STARTED.md           # Hướng dẫn nhanh 15 phút
├── PROJECT_SUMMARY.md           # Tóm tắt dự án (file này)
├── main.py                      # Script chính điều phối pipeline
├── config.py                    # Cấu hình (API keys, paths, settings)
├── requirements.txt             # Python dependencies
├── .env.example                 # Template cho environment variables
├── .gitignore                   # Bỏ qua file nhạy cảm
├── .nojekyll                    # Cần thiết cho GitHub Pages
├── LICENSE                      # MIT License
├── src/                         # Source code modules
│   ├── __init__.py
│   ├── utils.py                # Helper functions (logging, chunking, etc.)
│   ├── data_ingestion.py       # Tải bài báo từ BBC RSS
│   ├── script_generator.py     # Tạo kịch bản bằng GPT
│   ├── tts_converter.py        # Chuyển text-to-speech
│   └── github_uploader.py      # Upload lên GitHub Pages
├── .github/workflows/
│   └── daily.yml               # GitHub Actions (tự động chạy hàng ngày)
├── data/                       # Dữ liệu trung gian (gitignored)
│   ├── articles/              # Bài báo tải về (JSON)
│   └── processed/             # Kịch bản đã tạo (Markdown)
├── output/                    # File MP3 đầu ra (gitignored)
└── logs/                     # Log files
```

## 🚀 Công nghệ sử dụng

| Thành phần | Công nghệ | Mục đích |
|------------|-----------|----------|
| **Backend** | Python 3.9+ | Ngôn ngữ lập trình |
| **AI Script** | OpenAI GPT-3.5 Turbo | Tạo kịch bản podcast |
| **TTS** | ElevenLabs / OpenAI TTS | Chuyển text → speech |
| **Data Source** | BBC News RSS | Nguồn tin tức |
| **Scraping** | BeautifulSoup 4 | Lấy nội dung bài báo |
| **GitHub** | PyGithub | Upload file tự động |
| **Hosting** | GitHub Pages | Phát phát miễn phí |
| **Automation** | GitHub Actions | Chạy hàng ngày tự động |

## 📝 Các bước triển khai

### 1. Chuẩn bị
- [ ] Cài Python 3.9+
- [ ] Tạo repo GitHub (public)
- [ ] Lấy API keys: OpenAI, ElevenLabs (hoặc dùng OpenAI TTS)
- [ ] Tạo GitHub PAT với quyền `repo`

### 2. Cấu hình
```bash
# Copy template .env
cp .env.example .env

# Edit .env với các API keys của bạn
# OPENAI_API_KEY=sk-...
# ELEVENLABS_API_KEY=...
# GITHUB_TOKEN=ghp-...
```

```python
# Edit config.py
GITHUB_REPO = 'your-username/your-repo-name'
GITHUB_USERNAME = 'your-username'
GITHUB_REPO_NAME = 'your-repo-name'
```

### 3. Test local
```bash
# Cài dependencies
pip install -r requirements.txt

# Tạo thư mục data và output
mkdir -p data/articles data/processed output logs

# Dry run (không upload)
python main.py --dry-run

# Nếu thành công, chạy production
python main.py
```

### 4. Setup GitHub Pages
```bash
# Tạo branch gh-pages
git checkout --orphan gh-pages
git rm -rf .
touch .nojekyll
git add .nojekyll
git commit -m "Initial gh-pages"
git push origin gh-pages
git checkout main

# Bật GitHub Pages:
# Settings → Pages → Source: gh-pages branch
```

### 5. Tự động hóa
- **Option A**: GitHub Actions (khuyến nghị)
  - Thêm secrets vào repo Settings → Secrets
  - Workflow sẽ chạy tự động mỗi ngày 1h UTC (8h Việt Nam)

- **Option B**: Cron job local
  - Linux/Mac: `crontab -e` → `0 8 * * * cd /path && python main.py`
  - Windows: Task Scheduler

## 🎧 Kết quả

Sau khi chạy thành công:
- File MP3 được tạo trong `output/podcast_YYYY-MM-DD.mp3`
- File được upload lên GitHub Pages branch `gh-pages`
- `index.html` được update với audio player
- Podcast có thể nghe tại: `https://username.github.io/repo-name/output/podcast_latest.mp3`

## 📊 Chi phí ước tính

| Dịch vụ | Free Tier | Chi phí thực tế |
|---------|-----------|-----------------|
| OpenAI GPT-3.5 | $18/tháng credits (tài khoản mới) | ~$2-5/tháng |
| ElevenLabs TTS | 10k chars/tháng | ~$5/tháng |
| OpenAI TTS | Không free | ~$1-3/tháng |
| GitHub Pages | Miễn phí | $0 |
| **Tổng** | | **$5-10/tháng** |

*Có thể dùng Google TTS (free) để giảm chi phí về ~$2-3/tháng.*

## 🐛 Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Giải pháp |
|-----|-------------|-----------|
| "No articles fetched" | BBC RSS thay đổi structure | Kiểm tra logs, cập nhật CSS selectors |
| "API rate limit" | Gọi API quá nhiều | Thêm delay, nâng cấp plan |
| "TTS chunk too large" | Script quá dài | Giảm MAX_ARTICLES_PER_PODCAST |
| "GitHub upload failed" | Token không có quyền | Kiểm tra token scope, bật Pages |

## 📚 Tài liệu tham khảo

- **[requirement_spec.md](requirement_spec.md)** - Bản đặc tả yêu cầu đầy đủ (5 chương)
- **[architecture_design.md](architecture_design.md)** - Thiết kế kiến trúc chi tiết
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Hướng dẫn cài đặt nhanh
- **[README.md](README.md)** - Tài liệu chính cho GitHub

## ✅ Checklist trước khi commit

- [ ] Đã copy `.env.example` → `.env` và điền API keys
- [ ] Đã sửa `config.py` với GitHub repo của bạn
- [ ] Đã chạy `python main.py --dry-run` thành công
- [ ] Đã tạo branch `gh-pages` và bật GitHub Pages
- [ ] Đã thêm secrets vào GitHub (nếu dùng Actions)
- [ ] Đã test upload thành công (`python main.py`)

## 🎯 Next Steps

1. **Phase 1**: Chạy được end-to-end với Google TTS (free)
2. **Phase 2**: Thay bằng ElevenLabs/OpenAI TTS để chất lượng tốt hơn
3. **Phase 3**: Tối ưu prompt GPT để kịch bản hay hơn
4. **Phase 4**: Thêm nhiều nguồn tin (CNN, Reuters)
5. **Phase 5**: Thêm background music, ID3 tags

---

**Dự án này được thiết kế để đơn giản, dễ hiểu, dễ bảo trì. Mọi module đều có thể test riêng biệt.**

**Chúc bạn thành công!** 🚀