import os
import json
from datetime import datetime
from google import genai
from google.genai import types # Nhập thêm types để cấu hình JSON
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATA_FOLDER = os.getenv("DATA_FOLDER", "./data")

def create_script():
    print(f"📂 Đang đọc báo từ folder {DATA_FOLDER}...")
    news_content = ""
    # Đảm bảo thư mục tồn tại để không báo lỗi
    if os.path.exists(DATA_FOLDER):
        for filename in os.listdir(DATA_FOLDER):
            if filename.endswith(".txt"):
                with open(os.path.join(DATA_FOLDER, filename), "r", encoding="utf-8") as f:
                    news_content += f"\n\n--- {filename} ---\n"
                    news_content += f.read()

    if not news_content.strip():
        print(f"❌ Chưa có báo trong folder '{DATA_FOLDER}', chị chạy file fetch_bbc.py trước nhé!")
        return

    print("🧠 Đang gọi Gemini soạn kịch bản và trích xuất dữ liệu...")
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Prompt mới: Bắt buộc AI trả về chuẩn JSON với 3 trường thông tin
    prompt = f"""
    You are a podcast host. Read the news below and write a 5-minute podcast script.
    RULES:
    1. NO FAKE NEWS: Use only the text provided.
    2. USE SIMPLE ENGLISH: Use basic, non-academic vocabulary and short sentences. Make it very easy to understand.
    3. Length: About 600-700 words for the script.
    
    You MUST return the response strictly as a JSON object with this exact structure:
    {{
        "title": "Create a short Title here (6 to 7 words)",
        "summary": "Create a short Headline Summary here (1 sentence)",
        "script": "Your simple english podcast script here (ONLY the spoken words, no [Music] tags)"
    }}

    NEWS DATA:
    {news_content}
    """

    try:
        # Sử dụng Response Mime Type để ép AI trả về JSON hợp lệ
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        
        # --- 🌟 PHẦN CODE QUẢN LÝ FILE MỚI 🌟 ---
        
        if not os.path.exists("scripts"):
            os.makedirs("scripts")
            
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # LƯU Ý: Đổi đuôi file thành .json thay vì .txt
        output_filename = f"scripts/bbc_script_{current_time}.json"
        
        # Parse chuỗi JSON AI trả về và lưu lại để text_to_voice.py dễ đọc
        json_data = json.loads(response.text)
        
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
            
        print(f"✅ Đã soạn xong kịch bản và trích xuất JSON! Đã lưu an toàn vào: '{output_filename}'.")
        print(f"🎙️ Title: {json_data['title']}")
        print(f"📝 Summary: {json_data['summary']}")
        
    except Exception as e:
        print(f"❌ Lỗi AI: {e}")

if __name__ == "__main__":
    create_script()