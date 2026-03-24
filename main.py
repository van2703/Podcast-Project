import time
import asyncio
import fetch_bbc
import generate_script
import text_to_voice

def run_pipeline():
    print("🚀 BẮT ĐẦU CHẠY PIPELINE TỰ ĐỘNG (AUTO MODE)...")
    print("=" * 50)
    
    start_time = time.time()

    # Bước 1: Đi săn tin
    print("\n[1/3] Đang tải báo mới nhất...")
    fetch_bbc.download_bbc_news()
    
    # Bước 2: Viết kịch bản
    print("\n[2/3] Đang nhờ AI soạn kịch bản...")
    generate_script.create_script()
    
   # Bước 3: Thu âm
    print("\n[3/3] Đang chuyển kịch bản thành giọng nói...")
    asyncio.run(text_to_voice.create_voice())
    
    end_time = time.time()
    
    print("=" * 50)
    print(f"🎉 HOÀN TẤT TOÀN BỘ QUY TRÌNH!")
    print(f"⏱️ Tổng thời gian chạy: {round(end_time - start_time, 1)} giây.")
    print("🎧 Chị có thể mở file bbc_podcast.mp3 lên nghe được rồi đó fen!")

if __name__ == "__main__":
    run_pipeline()