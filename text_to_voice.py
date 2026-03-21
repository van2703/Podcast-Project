import asyncio
import edge_tts
import os

# Cấu hình giọng đọc (Aria là giọng nữ Mỹ rất tự nhiên, truyền cảm)
VOICE = "en-US-AriaNeural"  
# Mày có thể đổi sang giọng nam bằng cách thay thành: "en-US-ChristopherNeural"

INPUT_FILE = "podcast_script.txt"
OUTPUT_FILE = "bbc_podcast.mp3"

async def create_voice():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Không tìm thấy file {INPUT_FILE}. Mày phải chạy file generate_script.py trước nha fen!")
        return

    print("🎙️ Đang chuẩn bị phòng thu (Microsoft Edge TTS)...")
    
    # Đọc kịch bản
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        script_text = f.read()

    print(f"🎧 Đang thu âm giọng {VOICE} (Chờ tao vài giây)...")
    
    # Chuyển đổi và lưu thành mp3
    communicate = edge_tts.Communicate(script_text, VOICE)
    await communicate.save(OUTPUT_FILE)
    
    print(f"✨ Xuất sắc! File MP3 siêu cảm xúc đã ra lò: {OUTPUT_FILE}")

if __name__ == "__main__":
    # edge_tts sử dụng công nghệ bất đồng bộ (async) để chạy nhanh hơn
    asyncio.run(create_voice())