import os
import json
from datetime import datetime

MUSIC_FOLDER = "tabi_music"
CONFIG_FAV_FILE = "config_fav.js"

def update_fav_config():
    if not os.path.exists(MUSIC_FOLDER):
        os.makedirs(MUSIC_FOLDER)
        
    music_list = []
    files = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith('.mp3')]
    
    for filename in files:
        path = os.path.join(MUSIC_FOLDER, filename).replace('\\', '/')
        # Tách tên bài và tác giả từ tên file: "Attention - Charlie Puth.mp3"
        name_part = os.path.splitext(filename)[0]
        if " - " in name_part:
            title, artist = name_part.split(" - ", 1)
        else:
            title, artist = name_part, "Unknown Artist"
            
        music_list.append({
            "url": path,
            "title": title.strip(),
            "artist": artist.strip(),
            "timestamp": datetime.fromtimestamp(os.path.getctime(os.path.join(MUSIC_FOLDER, filename))).isoformat()
        })

    # Sắp xếp mới nhất lên đầu
    music_list.sort(key=lambda x: x['timestamp'], reverse=True)

    with open(CONFIG_FAV_FILE, "w", encoding="utf-8") as f:
        f.write("const FAV_LIST = ")
        json.dump(music_list, f, indent=4, ensure_ascii=False)
        f.write(";\n")
    print(f"✅ Đã cập nhật danh sách nhạc Tabi's Favorite với {len(music_list)} bài!")

if __name__ == "__main__":
    update_fav_config()