import os
import glob
import random
import asyncio
import edge_tts
import json
from datetime import datetime
from pydub import AudioSegment

def get_latest_script():
    list_of_files = glob.glob('scripts/*.json') 
    if not list_of_files:
        return None
    return max(list_of_files, key=os.path.getctime)

async def create_voice():
    input_file = get_latest_script()
    if not input_file:
        print("❌ Không tìm thấy kịch bản nào trong 'scripts/'. Chị nhớ chạy file generate_script.py trước!")
        return

    print(f"📖 Đang đọc kịch bản JSON: {input_file}")
    
    # 2. Bóc tách dữ liệu JSON
    with open(input_file, "r", encoding="utf-8") as f:
        try:
            json_data = json.load(f)
            script_text = json_data.get("script", "")
            podcast_title = json_data.get("title", "BBC Daily News")
            podcast_summary = json_data.get("summary", "Your daily news update.")
            
            # 🌟 NEW: Vớt thêm hashtags và ielts_score từ file JSON
            # Dùng .get([], "") để lỡ AI ngáo quên tạo thì code web của mày không bị crash
            hashtags = json_data.get("hashtags", [])
            ielts_score = json_data.get("ielts_score", "")
            
            if not script_text.strip():
                print("❌ File JSON không có nội dung phần 'script'.")
                return
        except json.JSONDecodeError:
            print("❌ Lỗi: File không đúng định dạng chuẩn JSON.")
            return

    if not os.path.exists("audios"):
        os.makedirs("audios")

    print("🎙️ Đang nạp AI Edge-TTS và tạo giọng đọc (Raw Voice)...")
    try:
        temp_mp3_path = "audios/temp_raw_voice.mp3"
        voice = "en-US-AriaNeural" 
        
        communicate = edge_tts.Communicate(script_text, voice)
        await communicate.save(temp_mp3_path)
        print("✅ Đã tạo xong giọng AI. Chuẩn bị mix nhạc nền...")

        # ---------------------------------------------------------
        # 🌟 BẮT ĐẦU MIX NHẠC NỀN (BACKGROUND MUSIC MIXING) 🌟
        # ---------------------------------------------------------
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_output_path = f"audios/bbc_podcast_{current_time}.mp3"
        
        music_files = glob.glob("music/*.*") 
        voice_audio = AudioSegment.from_file(temp_mp3_path)
        
        if not music_files:
            print("⚠️ Không tìm thấy nhạc nền. Xuất file thô...")
            voice_audio.export(final_output_path, format="mp3")
        else:
            random_bgm_path = random.choice(music_files)
            print(f"🎵 Đã chọn nhạc nền: {random_bgm_path}")
            
            bgm_audio = AudioSegment.from_file(random_bgm_path)
            bgm_audio = bgm_audio - 18
            
            if len(bgm_audio) < len(voice_audio):
                loop_count = (len(voice_audio) // len(bgm_audio)) + 1
                bgm_audio = bgm_audio * loop_count
            
            bgm_audio = bgm_audio[:len(voice_audio) + 3000]
            bgm_audio = bgm_audio.fade_out(3000)
            
            print("🎛️ Đang tiến hành trộn âm thanh (Mixing)...")
            final_mixed_audio = bgm_audio.overlay(voice_audio)
            final_mixed_audio.export(final_output_path, format="mp3")
            
        if os.path.exists(temp_mp3_path):
            os.remove(temp_mp3_path)
            
        print(f"✨ XUẤT SẮC! Đã mix xong file siêu phẩm tại: {final_output_path}")

        # ---------------------------------------------------------
        # 🌟 CẬP NHẬT CONFIG.JS 🌟
        # ---------------------------------------------------------
        config_path = "config.js"
        podcast_list = []
        
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    start_idx = content.find('[')
                    end_idx = content.rfind(']') + 1
                    if start_idx != -1 and end_idx != -1:
                        parsed_list = json.loads(content[start_idx:end_idx])
                        podcast_list = [item for item in parsed_list if isinstance(item, dict)]
            except Exception as e:
                print(f"⚠️ Không thể đọc config cũ (có thể sai format), tạo mới hoàn toàn. Lỗi: {e}")
                
        current_iso_time = datetime.now().isoformat()
        
        # 🌟 NEW: Nhét hashtags và ielts_score vào Object để in ra config.js
        new_podcast_entry = {
            "url": final_output_path.replace('\\', '/'),
            "title": podcast_title,
            "summary": podcast_summary,
            "timestamp": current_iso_time,
            "hashtags": hashtags,           # <--- Dữ liệu mới nè chị
            "ielts_score": ielts_score      # <--- Dữ liệu mới nè chị
        }
        
        podcast_list.insert(0, new_podcast_entry)

        with open(config_path, "w", encoding="utf-8") as f:
            f.write("const PODCAST_LIST = ")
            json.dump(podcast_list, f, indent=4, ensure_ascii=False)
            f.write(";\n")
            f.write(f'const LATEST_PODCAST = "{podcast_list[0]["url"]}";\n')
                
        print("🌐 Đã cập nhật file config.js chuẩn Object cho giao diện!")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    asyncio.run(create_voice())