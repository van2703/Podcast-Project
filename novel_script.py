import os
import json
import re
from datetime import datetime

DATA_NOVEL_FOLDER = "data_novel"
SCRIPTS_NOVEL_FOLDER = "scripts_novel"

if not os.path.exists(SCRIPTS_NOVEL_FOLDER):
    os.makedirs(SCRIPTS_NOVEL_FOLDER)

def process_novels():
    print(f"📂 Đang quét kho truyện chạy bằng cơm trong '{DATA_NOVEL_FOLDER}'...")
    
    for story_folder in os.listdir(DATA_NOVEL_FOLDER):
        folder_path = os.path.join(DATA_NOVEL_FOLDER, story_folder)
        
        if not os.path.isdir(folder_path):
            continue
            
        meta_path = os.path.join(folder_path, "meta.json")
        if not os.path.exists(meta_path):
            print(f"⚠️ Thư mục '{story_folder}' thiếu file meta.json. Bỏ qua!")
            continue
            
        with open(meta_path, "r", encoding="utf-8") as f:
            try:
                meta_data = json.load(f)
                ten_truyen = meta_data.get("name", "Truyện Ẩn Danh")
                tac_gia = meta_data.get("author", "Đang cập nhật")
                hashtags = meta_data.get("hashtags", ["#KeChuyenDemKhuya"])
            except Exception as e:
                print(f"❌ Lỗi đọc meta.json của '{story_folder}': {e}")
                continue
                
        print(f"\n📚 Bắt đầu xử lý bộ: {ten_truyen} (Tác giả: {tac_gia})")
        
        for filename in os.listdir(folder_path):
            # 🌟 CHỈ XỬ LÝ NHỮNG FILE CÒN ĐUÔI .txt (Những file .txt.done sẽ bị bỏ qua)
            if not filename.endswith(".txt"):
                continue
                
            txt_path = os.path.join(folder_path, filename)
            match = re.search(r'\d+', filename)
            so_chuong = match.group() if match else "X"
            
            with open(txt_path, "r", encoding="utf-8") as f:
                noi_dung_truyen = f.read().strip()
                
            if not noi_dung_truyen:
                print(f"⚠️ File {filename} rỗng, bỏ qua!")
                continue
                
            mo_dau = f"Xin chào các bé ngoan, lên giường mở podcast lên và nhắm mắt nghe chồng kể chuyện nha. Hôm nay chồng sẽ đọc cho các vợ nghe truyện {ten_truyen} của tác giả {tac_gia} chương {so_chuong}."
            ket_thuc = "Vậy là đã hết nội dung chương này rồi đó các vợ. Chúc các vợ ngủ ngoan nhé, anh yêu tất cả các em. Lovely Meo Meo."
            
            kich_ban_hoan_chinh = f"{mo_dau}\n\n{noi_dung_truyen}\n\n{ket_thuc}"
            
            final_title = f"{ten_truyen} - Chương {so_chuong}"
            json_data = {
                "story_id": story_folder,
                "title": final_title,
                "summary": f"Cùng nhắm mắt và lắng nghe chương {so_chuong} của bộ truyện {ten_truyen}.",
                "hashtags": hashtags,
                "script": kich_ban_hoan_chinh
            }
            
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(filename)[0]
            output_filename = f"{SCRIPTS_NOVEL_FOLDER}/{story_folder}_{base_name}_{current_time}.json"
            
            with open(output_filename, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=4, ensure_ascii=False)
                
            print(f"✅ Đã lên khuôn thành công: '{final_title}' -> {output_filename}")
            
            # 🌟 CÚ FIX ĂN TIỀN: Đổi đuôi file để đánh dấu "ĐÃ XỬ LÝ XONG"
            os.rename(txt_path, txt_path + ".done")
            print(f"🔒 Đã khóa file gốc thành: {filename}.done")

if __name__ == "__main__":
    process_novels()