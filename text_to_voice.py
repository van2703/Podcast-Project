import os
import glob
import numpy as np
import soundfile as sf
from datetime import datetime
from kokoro import KPipeline

def get_latest_script():
    # Tìm tất cả các file .txt trong thư mục scripts
    list_of_files = glob.glob('scripts/*.txt')
    if not list_of_files:
        return None
    # Trả về file được tạo gần đây nhất
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def create_voice():
    # 1. Tự động lấy kịch bản mới nhất (Auto-get latest script)
    input_file = get_latest_script()
    
    if not input_file:
        print("❌ Không tìm thấy kịch bản nào trong thư mục 'scripts/'.")
        return

    print(f"📖 Đang đọc kịch bản mới nhất: {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        script_text = f.read()

    # Tạo thư mục audio nếu chưa có
    if not os.path.exists("audios"):
        os.makedirs("audios")

    print("🎙️ Đang nạp AI Kokoro...")
    try:
        pipeline = KPipeline(lang_code='b')
        generator = pipeline(script_text, voice='bf_emma', speed=1.05, split_pattern=r'\n+')

        print("🎧 Đang thu âm...")
        all_audio_chunks = []
        for i, (graphemes, phonemes, audio) in enumerate(generator):
            if audio is not None:
                all_audio_chunks.append(audio)
                
        if all_audio_chunks:
            final_audio = np.concatenate(all_audio_chunks)
            
            # 2. Lưu audio vào thư mục podcasts/
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"audios/bbc_podcast_{current_time}.wav"
            
            sf.write(audio_filename, final_audio, 24000)
            print(f"✨ Xong! Đã lưu file âm thanh tại: {audio_filename}")
            
            # 3. CẬP NHẬT CHO WEB (Update Web Config)
            # Tạo một file config.js để HTML đọc
            with open("config.js", "w", encoding="utf-8") as f:
                f.write(f'const LATEST_PODCAST = "{audio_filename}";')
            print("🌐 Đã cập nhật config.js cho trang web!")
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    create_voice()