import os
import glob
import random
import asyncio
import edge_tts
import json
from datetime import datetime
from pydub import AudioSegment

# ---------------------------------------------------------
# 🛠️ CẤU HÌNH THƯ MỤC VÀ TÊN FILE CHO LUỒNG TRUYỆN
# ---------------------------------------------------------
SCRIPTS_NOVEL_FOLDER = "scripts_novel"
AUDIOS_NOVEL_FOLDER = "audios_novel"
CONFIG_NOVEL_FILE = "config_novel.js"

def get_latest_novel_script():
    list_of_files = glob.glob(f'{SCRIPTS_NOVEL_FOLDER}/*.json') 
    if not list_of_files:
        return None
    return max(list_of_files, key=os.path.getctime)

async def create_novel_voice():
    input_file = get_latest_novel_script()
    if not input_file:
        print(f"❌ Không tìm thấy kịch bản nào. Chị chạy file novel_script.py trước nhé!")
        return

    print(f"📖 Đang đọc kịch bản truyện từ: {input_file}")
    
    with open(input_file, "r", encoding="utf-8") as f:
        try:
            json_data = json.load(f)
            script_text = json_data.get("script", "")
            novel_title = json_data.get("title", "Truyện Đêm Khuya")
            novel_summary = json_data.get("summary", "Mời các bạn cùng lắng nghe.")
            hashtags = json_data.get("hashtags", [])
            
            if not script_text.strip():
                print("❌ File JSON rỗng phần 'script'.")
                return
        except json.JSONDecodeError:
            print("❌ Lỗi: File không đúng định dạng chuẩn JSON.")
            return

    if not os.path.exists(AUDIOS_NOVEL_FOLDER):
        os.makedirs(AUDIOS_NOVEL_FOLDER)

    print("🎙️ Đang nạp AI Edge-TTS và gọi cô MC Hoài My (Tiếng Việt)...")
    try:
        temp_mp3_path = f"{AUDIOS_NOVEL_FOLDER}/temp_raw_voice.mp3"
        
        # 🌟 ĐIỂM SÁNG: Đổi sang giọng Nữ Tiếng Việt (Hoài My) rất ấm và truyền cảm
        # Nếu mày thích giọng Nam trầm ấm, có thể đổi thành "vi-VN-NamMinhNeural"
        voice = "vi-VN-HoaiMyNeural" 
        
        communicate = edge_tts.Communicate(script_text, voice)
        await communicate.save(temp_mp3_path)
        print("✅ Đã thu âm xong giọng AI. Chuẩn bị mix nhạc nền...")

        # ---------------------------------------------------------
        # 🌟 MIX NHẠC NỀN (Dùng chung folder 'music' của News)
        # ---------------------------------------------------------
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_output_path = f"{AUDIOS_NOVEL_FOLDER}/vietnamlove_ep_{current_time}.mp3"
        
        music_files = glob.glob("music/*.*") 
        voice_audio = AudioSegment.from_file(temp_mp3_path)
        
        if not music_files:
            print("⚠️ Không tìm thấy nhạc nền. Xuất file thô...")
            voice_audio.export(final_output_path, format="mp3")
        else:
            random_bgm_path = random.choice(music_files)
            print(f"🎵 Đã chọn nhạc lồng tiếng: {random_bgm_path}")
            
            bgm_audio = AudioSegment.from_file(random_bgm_path)
            
            # 🌟 TINH CHỈNH ÂM LƯỢNG: Kể truyện thì nhạc nền nên nhỏ hơn bản tin một chút
            # Tao trừ đi 22dB để giọng MC nghe rõ ràng, rành mạch hơn
            bgm_audio = bgm_audio - 22 
            
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
            
        print(f"✨ XUẤT SẮC! Tập truyện audio đã lên mâm tại: {final_output_path}")

        # ---------------------------------------------------------
        # 🌟 CẬP NHẬT CONFIG_NOVEL.JS (TÁCH BIỆT HOÀN TOÀN KHỎI NEWS)
        # ---------------------------------------------------------
        novel_list = []
        
        if os.path.exists(CONFIG_NOVEL_FILE):
            try:
                with open(CONFIG_NOVEL_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                    start_idx = content.find('[')
                    end_idx = content.rfind(']') + 1
                    if start_idx != -1 and end_idx != -1:
                        parsed_list = json.loads(content[start_idx:end_idx])
                        novel_list = [item for item in parsed_list if isinstance(item, dict)]
            except Exception as e:
                print(f"⚠️ Không thể đọc config_novel cũ. Lỗi: {e}")
                
        current_iso_time = datetime.now().isoformat()
        
        new_novel_entry = {
            "url": final_output_path.replace('\\', '/'),
            "title": novel_title,
            "summary": novel_summary,
            "timestamp": current_iso_time,
            "hashtags": hashtags
            # Chú ý: Kể truyện không có ielts_score nữa nha chị!
        }
        
        novel_list.insert(0, new_novel_entry)

        with open(CONFIG_NOVEL_FILE, "w", encoding="utf-8") as f:
            # 🌟 ĐỔI TÊN BIẾN JAVASCRIPT THÀNH NOVEL_LIST
            f.write("const NOVEL_LIST = ")
            json.dump(novel_list, f, indent=4, ensure_ascii=False)
            f.write(";\n")
            f.write(f'const LATEST_NOVEL = "{novel_list[0]["url"]}";\n')
                
        print(f"🌐 Đã ghi data vào file '{CONFIG_NOVEL_FILE}'. Giao diện sẵn sàng nghênh chiến!")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    asyncio.run(create_novel_voice())