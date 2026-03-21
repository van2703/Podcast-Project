import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATA_FOLDER = os.getenv("DATA_FOLDER", "./data")

def create_script():
    print("📂 Đang đọc báo từ folder data...")
    news_content = ""
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".txt"):
            with open(os.path.join(DATA_FOLDER, filename), "r", encoding="utf-8") as f:
                news_content += f"\n\n--- {filename} ---\n"
                news_content += f.read()

    if not news_content.strip():
        print("❌ Chưa có báo trong folder, chị chạy file fetch_bbc.py trước nhé!")
        return

    print("🧠 Đang gọi Gemini soạn kịch bản...")
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    You are a podcast host. Read the news below and write a script for a 3-minute podcast.
    RULES:
    1. NO FAKE NEWS: Use only the text provided.
    2. USE SIMPLE ENGLISH: Use basic vocabulary and short sentences.
    3. Length: About 400-500 words.
    4. ONLY output the spoken words. No sound effect tags like [Music].

    NEWS DATA:
    {news_content}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        # Lưu ra file txt để làm đầu vào cho bước sau
        with open("podcast_script.txt", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("✅ Đã soạn xong kịch bản! Đã lưu vào file 'podcast_script.txt'.")
        print("💡 Chị có thể mở file này ra đọc thử hoặc sửa lại tùy ý trước khi tạo voice.")

    except Exception as e:
        print(f"❌ Lỗi AI: {e}")

if __name__ == "__main__":
    create_script()