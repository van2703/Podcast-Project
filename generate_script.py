import os
from datetime import datetime
from google import genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATA_FOLDER = os.getenv("DATA_FOLDER", "./data")

def create_script():
    print(f"📂 Đang đọc báo từ folder {DATA_FOLDER}...")
    news_content = ""
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".txt"):
            with open(os.path.join(DATA_FOLDER, filename), "r", encoding="utf-8") as f:
                news_content += f"\n\n--- {filename} ---\n"
                news_content += f.read()

    if not news_content.strip():
        print(f"❌ Chưa có báo trong folder '{DATA_FOLDER}', chị chạy file fetch_bbc.py trước nhé!")
        return

    print("🧠 Đang gọi Gemini soạn kịch bản...")
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Prompt đã được tối ưu để đảm bảo AI viết từ ngữ đơn giản, dễ đọc
    prompt = f"""
    You are a podcast host. Read the news below and write a script for a 5-minute podcast.
    RULES:
    1. NO FAKE NEWS: Use only the text provided.
    2. USE SIMPLE ENGLISH: Use basic, non-academic vocabulary and short sentences. Make it very easy to understand.
    3. Length: About 600-700 words.
    4. ONLY output the spoken words. No sound effect tags like [Music].

    NEWS DATA:
    {news_content}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        # --- 🌟 PHẦN CODE MỚI ĐỂ QUẢN LÝ FILE CHUYÊN NGHIỆP 🌟 ---
        
        # 1. Tạo thư mục 'scripts' nếu chưa có
        if not os.path.exists("scripts"):
            os.makedirs("scripts")
            
        # 2. Lấy mốc thời gian hiện tại để đặt tên file không bao giờ trùng
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"scripts/bbc_script_{current_time}.txt"
        
        # 3. Lưu kịch bản vào đúng thư mục với tên mới
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(response.text)
            
        print(f"✅ Đã soạn xong kịch bản! Đã lưu an toàn vào: '{output_filename}'.")
        print("💡 Chị có thể mở file này ra đọc thử hoặc sửa lại tùy ý trước khi tạo voice.")
        
        # ---------------------------------------------------------

    except Exception as e:
        print(f"❌ Lỗi AI: {e}")

if __name__ == "__main__":
    create_script()