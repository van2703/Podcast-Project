import os
import json
import re
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load môi trường
load_dotenv()

# Lấy Key và kiểm tra
API_KEY = os.getenv("OPENAI_API_KEY")
DATA_FOLDER = os.getenv("DATA_FOLDER", "./data")

def create_script():
    # --- BƯỚC KIỂM TRA QUAN TRỌNG ---
    if not API_KEY:
        print("❌ Lỗi: Không tìm thấy API Key trong file .env!")
        print("💡 Hãy chắc chắn bạn đã đặt tên biến là OPENAI_API_KEY trong file .env")
        return
    else:
        # In ra 10 ký tự đầu để bạn tự kiểm tra (không in hết để bảo mật)
        print(f"🔑 Đã tìm thấy API Key (bắt đầu bằng: {API_KEY[:10]}...)")
    # -------------------------------

    print(f"📂 Đang đọc báo từ folder {DATA_FOLDER}...")
    news_content = ""
    if os.path.exists(DATA_FOLDER):
        for filename in os.listdir(DATA_FOLDER):
            if filename.endswith(".txt"):
                with open(os.path.join(DATA_FOLDER, filename), "r", encoding="utf-8") as f:
                    news_content += f"\n\n--- {filename} ---\n"
                    news_content += f.read()

    if not news_content.strip():
        print(f"❌ Chưa có báo trong folder '{DATA_FOLDER}'!")
        return

    print("🧠 Đang gọi Qwen (OpenRouter) với Reasoning...")
    
    # Khởi tạo client - Đảm bảo api_key được truyền trực tiếp vào đây
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=API_KEY, 
    )
    
    prompt = f"""
    You are a podcast host. Read the news below and write a 10-minute podcast script.
    RULES:
    1. NO FAKE NEWS: Use only the text provided.
    2. USE SIMPLE ENGLISH: Use basic vocabulary.
    3. Evaluate difficulty and assign IELTS score.
    4. Length: 1000-1200 words.
    5. HASHTAGS: 3-5 keywords.
    
    RETURN ONLY JSON:
    {{
        "title": "Title here",
        "summary": "Summary here",
        "hashtags": ["#Tag1"],
        "ielts_score": "7.0",
        "script": "Full script here"
    }}

    NEWS DATA:
    {news_content}
    """

    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.6-plus-preview:free",
            messages=[{"role": "user", "content": prompt}],
            extra_body={"reasoning": {"enabled": True}}
        )
        
        raw_text = response.choices[0].message.content
        
        # Trích xuất JSON bằng Regex để tránh lỗi nếu AI trả về kèm văn bản thừa
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            json_data = json.loads(match.group(0))
        else:
            print("⚠️ AI không trả về đúng định dạng JSON. Nội dung gốc:")
            print(raw_text)
            return

        if not os.path.exists("scripts"):
            os.makedirs("scripts")
            
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"scripts/bbc_script_{current_time}.json"
        
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
            
        print(f"✅ Xong! File lưu tại: {output_filename}")
        
    except Exception as e:
        # Nếu vẫn lỗi 401, lỗi này sẽ in chi tiết tại đây
        print(f"❌ Lỗi API: {e}")

if __name__ == "__main__":
    create_script()