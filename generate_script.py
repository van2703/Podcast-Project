import os
import json
from datetime import datetime
from google import genai
from google.genai import types 
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY1")
DATA_FOLDER = os.getenv("DATA_FOLDER", "./data")

def create_script():
    print(f"📂 Đang đọc báo từ folder {DATA_FOLDER}...")
    news_content = ""
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
    
    prompt = f"""
    You are a podcast host. Read the news below and write a 10-minute podcast script.
    RULES:
    1. NO FAKE NEWS: Use only the text provided.
    2. USE SIMPLE BUT DRAMATIC ENGLISH: Keep the vocabulary simple and non-academic so it's easy to understand. However, use natural idioms, slang, and highly emotional expressive phrasing (e.g., 'mind-blowing', 'devastated') to create drama and excitement. DO NOT use overly complex or formal words.
    3. Avoid dry, overly academic vocabulary. Use natural, highly emotional idioms, slang, and expressive phrasing to create drama or excitement.
    4. Evaluate the vocabulary difficulty of your generated script and assign an estimated IELTS Reading/Listening score (e.g., 5.5, 6.5, 7.5).
    5. Length: About 1000-1200 words for the script.
    6. HASHTAGS: Extract 3 to 5 simple, relevant keywords as hashtags (e.g.#Tech, #Health, #World).
    
    You MUST return the response strictly as a JSON object with this exact structure:
    {{
        "title": "Create a short Title here (6 to 7 words)",
        "summary": "Create a short Headline Summary here (1 sentence)",
        "hashtags": ["#Tag1", "#Tag2", "#Tag3"],
        "ielts_score": "7.0",
        "script": "Your english podcast script here (ONLY the spoken words, no [Music] tags)"
    }}

    NEWS DATA:
    {news_content}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        
        if not os.path.exists("scripts"):
            os.makedirs("scripts")
            
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"scripts/bbc_script_{current_time}.json"
        
        json_data = json.loads(response.text)
        
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
            
        print(f"✅ Đã soạn xong kịch bản và trích xuất JSON! Đã lưu an toàn vào: '{output_filename}'.")
        print(f"🎙️ Title: {json_data.get('title', 'N/A')}")
        print(f"📝 Summary: {json_data.get('summary', 'N/A')}")
        print(f"📈 IELTS Level: {json_data.get('ielts_score', 'N/A')}")
        print(f"🏷️ Hashtags: {', '.join(json_data.get('hashtags', []))}")
        
    except Exception as e:
        print(f"❌ Lỗi AI: {e}")

if __name__ == "__main__":
    create_script()