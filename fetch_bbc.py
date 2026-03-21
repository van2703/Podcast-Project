import feedparser
import os
import re # Dùng thư viện này để lọc tên file cho sạch nhất
from dotenv import load_dotenv

# 1. Tải cấu hình từ file .env
load_dotenv()
RSS_URL = os.getenv("BBC_RSS_URL")
# Dùng tên này cho thống nhất
DATA_FOLDER = os.getenv("DATA_FOLDER", "./data")

def download_bbc_news():
    # 2. Tạo folder data nếu chưa có
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        print(f"--- Đã tạo thư mục: {DATA_FOLDER} ---")

    # 3. Lấy tin từ BBC
    print("🚀 Đang kết nối với BBC News...")
    feed = feedparser.parse(RSS_URL)

    if not feed.entries:
        print("❌ Không lấy được tin. Chị check lại mạng hoặc link RSS nhé!")
        return

    # 4. Lưu 5 bài mới nhất
    print(f"📥 Bắt đầu copy bài báo về máy...")
    for i, entry in enumerate(feed.entries[:5]):
        # Lấy tiêu đề và biến nó thành chuỗi (string) thuần túy
        title_str = str(entry.title)
        
        # Dùng Regex để chỉ giữ lại chữ cái và số cho tên file (An toàn tuyệt đối)
        safe_title = re.sub(r'[^a-zA-Z0-9 ]', '', title_str).strip()
        short_title = safe_title[:50] # Cắt ngắn tiêu đề
        
        # Tạo đường dẫn file
        filename = f"news_{i+1}_{short_title}.txt"
        file_path = os.path.join(DATA_FOLDER, filename)

        # Lưu nội dung
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"SOURCE: BBC NEWS\n")
                f.write(f"TITLE: {title_str}\n")
                f.write(f"LINK: {entry.link}\n")
                f.write(f"--- CONTENT ---\n")
                f.write(str(entry.summary)) # Ép kiểu sang string cho chắc chắn
            print(f"✅ Đã lưu file: {filename}")
        except Exception as e:
            print(f"❌ Lỗi khi lưu file {i+1}: {e}")

    print(f"\n✨ Xong rồi! Chị mở folder '{DATA_FOLDER}' kiểm tra kết quả nhé.")

if __name__ == "__main__":
    download_bbc_news()