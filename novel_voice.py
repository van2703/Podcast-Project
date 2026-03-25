import os
import glob
import random
import asyncio
import edge_tts
import json
from datetime import datetime
from pydub import AudioSegment

SCRIPTS_NOVEL_FOLDER = "scripts_novel"
AUDIOS_NOVEL_FOLDER = "audios_novel"
CONFIG_NOVEL_FILE = "config_novel.js"

async def create_novel_voice():
    # 🌟 FIX: Lấy TOÀN BỘ file .json đang có trong thư mục (bỏ qua những file .done)
    list_of_files = glob.glob(f'{SCRIPTS_NOVEL_FOLDER}/*.json') 
    
    if not list_of_files:
        print(f"❌ Không tìm thấy kịch bản JSON nào mới. Có vẻ chồng đã đọc hết truyện rồi!")
        return

    print(f"🔎 Tìm thấy {len(list_of_files)} kịch bản đang chờ thu âm. Bắt đầu lên mic...")

    if not os.path.exists(AUDIOS_NOVEL_FOLDER):
        os.makedirs(AUDIOS_NOVEL_FOLDER)

    # 🌟 VÒNG LẶP: Xử lý từng file JSON một
    for input_file in list_of_files:
        print(f"\n📖 Đang xử lý kịch bản: {input_file}")
        
        with open(input_file, "r", encoding="utf-8") as f:
            try:
                json_data = json.load(f)
                story_id = json_data.get("story_id", "Unknown")
                script_text = json_data.get("script", "")
                novel_title = json_data.get("title", "Truyện Đêm Khuya")
                novel_summary = json_data.get("summary", "Mời các bạn cùng lắng nghe.")
                hashtags = json_data.get("hashtags", [])
                
                if not script_text.strip():
                    print(f"⚠️ File {input_file} rỗng phần 'script'. Bỏ qua!")
                    continue
            except json.JSONDecodeError:
                print(f"⚠️ Lỗi đọc file {input_file}. Bỏ qua!")
                continue

        print(f"🎙️ Gọi 'chồng' Nam Minh lên mic...")
        try:
            temp_mp3_path = f"{AUDIOS_NOVEL_FOLDER}/temp_raw_voice.mp3"
            voice = "vi-VN-NamMinhNeural" 
            
            communicate = edge_tts.Communicate(script_text, voice)
            await communicate.save(temp_mp3_path)
            
            # --- MIX NHẠC ---
            # --- ĐOẠN SỬA LẠI ĐỂ ĐẶT TÊN FILE THEO TRUYỆN + CHAP ---
            story_audio_folder = f"{AUDIOS_NOVEL_FOLDER}/{story_id}"
            if not os.path.exists(story_audio_folder):
                os.makedirs(story_audio_folder)
            
            # 🌟 CÁCH LẤY TÊN: 
            # Giả sử input_file là "scripts_novel/KTCVE_chap1_20260325_170000.json"
            # Bước 1: Lấy tên file kèm đuôi (KTCVE_chap1_20260325_170000.json)
            raw_filename = os.path.basename(input_file)
            
            # Bước 2: Tách lấy phần tên truyện và chap (KTCVE_chap1) 
            # Tao dùng split('_202') để cắt bỏ phần ngày tháng bắt đầu từ năm 202x
            clean_name = raw_filename.split('_202')[0]
            
            # Bước 3: Ghép vào đường dẫn mới
            final_output_path = f"{story_audio_folder}/{clean_name}.mp3"
            
            print(f"🎯 Tên file audio mới: {clean_name}.mp3")            
            music_files = glob.glob("music/*.*") 
            voice_audio = AudioSegment.from_file(temp_mp3_path)
            
            if not music_files:
                voice_audio.export(final_output_path, format="mp3")
            else:
                random_bgm_path = random.choice(music_files)
                bgm_audio = AudioSegment.from_file(random_bgm_path)
                bgm_audio = bgm_audio - 22 
                
                if len(bgm_audio) < len(voice_audio):
                    loop_count = (len(voice_audio) // len(bgm_audio)) + 1
                    bgm_audio = bgm_audio * loop_count
                
                bgm_audio = bgm_audio[:len(voice_audio) + 3000]
                bgm_audio = bgm_audio.fade_out(3000)
                
                final_mixed_audio = bgm_audio.overlay(voice_audio)
                final_mixed_audio.export(final_output_path, format="mp3", bitrate="64k")
                
            if os.path.exists(temp_mp3_path):
                os.remove(temp_mp3_path)
                
            print(f"✨ Xuất mp3 thành công: {final_output_path}")

            # --- CẬP NHẬT CONFIG JS ---
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
                    pass
                    
            new_novel_entry = {
                "story_id": story_id,
                "url": final_output_path.replace('\\', '/'),
                "title": novel_title,
                "summary": novel_summary,
                "timestamp": datetime.now().isoformat(),
                "hashtags": hashtags
            }
            
            novel_list.insert(0, new_novel_entry)

            with open(CONFIG_NOVEL_FILE, "w", encoding="utf-8") as f:
                f.write("const NOVEL_LIST = ")
                json.dump(novel_list, f, indent=4, ensure_ascii=False)
                f.write(";\n")
                f.write(f'const LATEST_NOVEL = "{novel_list[0]["url"]}";\n')
            
            # 🌟 CÚ FIX ĂN TIỀN: Đổi đuôi JSON thành .done để máy biết là đã đọc xong
            os.rename(input_file, input_file + ".done")
            print(f"🔒 Đã khóa kịch bản thành: {os.path.basename(input_file)}.done")
            
        except Exception as e:
            print(f"❌ Lỗi khi xử lý {input_file}: {e}")

    print("\n🎉 TOÀN BỘ KỊCH BẢN ĐÃ ĐƯỢC CHỒNG THU ÂM XONG!")

if __name__ == "__main__":
    asyncio.run(create_novel_voice())