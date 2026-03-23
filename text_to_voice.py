import os
import glob
import random
import numpy as np
import soundfile as sf
from datetime import datetime
from kokoro import KPipeline
from pydub import AudioSegment

def get_latest_script():
    list_of_files = glob.glob('scripts/*.txt')
    if not list_of_files:
        return None
    return max(list_of_files, key=os.path.getctime)

def create_voice():
    input_file = get_latest_script()
    if not input_file:
        print("❌ Không tìm thấy kịch bản nào trong 'scripts/'.")
        return

    print(f"📖 Đang đọc kịch bản: {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        script_text = f.read()

    # Nhớ là folder của chị tên là 'audios' nha
    if not os.path.exists("audios"):
        os.makedirs("audios")

    print("🎙️ Đang nạp AI Kokoro và tạo giọng đọc (Raw Voice)...")
    try:
        pipeline = KPipeline(lang_code='b')
        generator = pipeline(script_text, voice='bf_emma', speed=1.0, split_pattern=r'\n+')

        all_audio_chunks = []
        for i, (graphemes, phonemes, audio) in enumerate(generator):
            if audio is not None:
                all_audio_chunks.append(audio)
                
        if all_audio_chunks:
            final_audio = np.concatenate(all_audio_chunks)
            
            # 1. Lưu tạm file giọng đọc gốc (chưa ghép nhạc)
            raw_voice_path = "audios/temp_raw_voice.wav"
            sf.write(raw_voice_path, final_audio, 24000)
            print("✅ Đã tạo xong giọng AI. Chuẩn bị mix nhạc nền...")

            # ---------------------------------------------------------
            # 🌟 BẮT ĐẦU MIX NHẠC NỀN (BACKGROUND MUSIC MIXING) 🌟
            # ---------------------------------------------------------
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_output_path = f"audios/bbc_podcast_{current_time}.wav"
            
            # Lấy danh sách tất cả file nhạc trong folder 'music'
            music_files = glob.glob("music/*.*") # Quét cả mp3, wav...
            
            if not music_files:
                print("⚠️ Không tìm thấy file nhạc nào trong folder 'music/'. Sẽ xuất file không có nhạc nền.")
                # Nếu không có nhạc, đổi tên file tạm thành file chính luôn
                os.rename(raw_voice_path, final_output_path)
            else:
                # Bốc đại 1 bài nhạc
                random_bgm_path = random.choice(music_files)
                print(f"🎵 Đã chọn nhạc nền: {random_bgm_path}")
                
                # Load file giọng đọc và file nhạc lên bộ nhớ
                voice_audio = AudioSegment.from_wav(raw_voice_path)
                bgm_audio = AudioSegment.from_file(random_bgm_path)
                
                # Giảm âm lượng nhạc nền đi 18 decibel (để không lấn lướt giọng đọc)
                bgm_audio = bgm_audio - 18
                
                # So sánh độ dài: Nếu nhạc nền ngắn hơn giọng đọc, lặp lại nhạc nền (loop)
                if len(bgm_audio) < len(voice_audio):
                    loop_count = (len(voice_audio) // len(bgm_audio)) + 1
                    bgm_audio = bgm_audio * loop_count
                
                # Cắt bài nhạc nền sao cho dài bằng giọng đọc + dư ra 3 giây cuối (3000 milliseconds)
                bgm_audio = bgm_audio[:len(voice_audio) + 3000]
                
                # Làm hiệu ứng fade_out (nhỏ dần) ở 3 giây cuối cho chuyên nghiệp
                bgm_audio = bgm_audio.fade_out(3000)
                
                # Trộn 2 âm thanh lại với nhau (Overlay)
                print("🎛️ Đang tiến hành trộn âm thanh (Mixing)...")
                final_mixed_audio = bgm_audio.overlay(voice_audio)
                
                # Xuất ra file cuối cùng
                final_mixed_audio.export(final_output_path, format="wav")
                
                # Xóa cái file tạm đi cho sạch ổ cứng
                os.remove(raw_voice_path)
                print(f"✨ XUẤT SẮC! Đã mix xong file siêu phẩm tại: {final_output_path}")

            # ---------------------------------------------------------
            # CẬP NHẬT CONFIG.JS CHO WEB GITHUB PAGES
            # ---------------------------------------------------------
            all_podcasts = glob.glob('audios/*.wav')
            all_podcasts.sort(key=os.path.getctime, reverse=True)
            podcast_list_web = [p.replace('\\', '/') for p in all_podcasts]
            
            with open("config.js", "w", encoding="utf-8") as f:
                f.write(f'const PODCAST_LIST = {podcast_list_web};\n')
                if podcast_list_web:
                    f.write(f'const LATEST_PODCAST = "{podcast_list_web[0]}";\n')
                    
            print("🌐 Đã cập nhật file config.js cho web!")
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    create_voice()