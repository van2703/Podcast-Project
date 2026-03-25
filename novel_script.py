import os
import json
import time
from datetime import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Cấu hình thư mục riêng cho Mode Vietnamlove
DATA_NOVEL_FOLDER = "data_novel"
SCRIPTS_NOVEL_FOLDER = "scripts_novel"

if not os.path.exists(SCRIPTS_NOVEL_FOLDER):
    os.makedirs(SCRIPTS_NOVEL_FOLDER)

# ---------------------------------------------------------
# 🛠️ HÀM: GỌI AI VIẾT KỊCH BẢN TỪ FILE TEXT
# ---------------------------------------------------------
def generate_episode_script(novel_text, filename):
    print(f"🧠 Đang gọi Gemini biến hóa file '{filename}' thành kịch bản MC...")
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    Bạn là một MC Podcast kể chuyện đêm khuya người Việt Nam, giọng điệu cực kỳ duyên dáng, lôi cuốn và truyền cảm.
    Dưới đây là nội dung của một tập/chương truyện.
    
    NHIỆM VỤ:
    Hãy chuyển thể phần truyện này thành một kịch bản Podcast dài khoảng 700 - 1000 chữ.
    
    LUẬT:
    1. Giọng điệu: Đậm chất Việt Nam, lôi cuốn, có cảm xúc (vui, buồn, drama, hồi hộp). KHÔNG dùng từ ngữ khô khan, máy móc hay học thuật.
    2. Nhập vai: Mở đầu bằng lời chào thính giả thân mật, dẫn dắt nhẹ nhàng vào không gian câu chuyện và kể lại diễn biến một cách sinh động.
    3. Kết thúc: Kết thúc bằng một câu mồi nhử gây tò mò cho tập sau, hoặc một lời chào tạm biệt đầy cảm xúc.
    4. Cốt truyện: Chỉ dựa vào nội dung truyện được cấp, bám sát tâm lý nhân vật, tuyệt đối không bịa thêm tình tiết lạ.
    
    BẮT BUỘC TRẢ VỀ CHUẨN JSON VỚI CẤU TRÚC SAU:
    {{
        "title": "Tên tập truyện giật gân (khoảng 7-10 chữ)",
        "summary": "Tóm tắt mồi nhử cực ngắn (1 câu)",
        "hashtags": ["#KeChuyen", "#Drama", "#AudioTruyen"],
        "script": "Toàn bộ lời thoại của MC bằng TIẾNG VIỆT ở đây (chỉ lời nói, không có thẻ [Nhạc])."
    }}

    NỘI DUNG TẬP NÀY:
    {novel_text}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"❌ Lỗi AI khi xử lý file {filename}: {e}")
        return None

# ---------------------------------------------------------
# 🚀 HÀM CHÍNH (MAIN WORKFLOW)
# ---------------------------------------------------------
def create_novel_scripts():
    print(f"📂 Đang quét truyện trong folder '{DATA_NOVEL_FOLDER}'...")
    
    # Lấy danh sách TẤT CẢ các file .txt trong thư mục
    novel_files = [f for f in os.listdir(DATA_NOVEL_FOLDER) if f.endswith(".txt")]
    
    if not novel_files:
        print(f"❌ Chưa có file .txt nào trong '{DATA_NOVEL_FOLDER}'. Chị ném truyện vào nhé!")
        return
        
    print(f"📚 Tìm thấy {len(novel_files)} file truyện. Bắt đầu lên đồ...")

    # Vòng lặp: Xử lý từng file một
    for index, filename in enumerate(novel_files, 1):
        target_file = os.path.join(DATA_NOVEL_FOLDER, filename)
        print(f"\n--- BẮT ĐẦU XỬ LÝ FILE: {filename} ---")
        
        with open(target_file, "r", encoding="utf-8") as f:
            full_text = f.read()
            
        if not full_text.strip():
            print(f"⚠️ File {filename} rỗng không có chữ nào, bỏ qua!")
            continue

        # Ném nguyên cục text của file đó cho AI xử
        json_data = generate_episode_script(full_text, filename)
        
        if json_data:
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Tách tên file gốc (KTCVE_chap1) ra khỏi đuôi (.txt) để đặt tên cho file JSON
            base_name = os.path.splitext(filename)[0]
            output_filename = f"{SCRIPTS_NOVEL_FOLDER}/{base_name}_{current_time}.json"
            
            with open(output_filename, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=4, ensure_ascii=False)
                
            print(f"✅ Đã đóng gói kịch bản thành công vào: '{output_filename}'")
            print(f"🎙️ Tiêu đề: {json_data.get('title')}")
            print(f"🏷️ Hashtags: {', '.join(json_data.get('hashtags', []))}")
            
        # ⚠️ Nhịp nghỉ 5 giây giữa các file (nếu còn file tiếp theo)
        if index < len(novel_files):
            print(f"⏳ Đang cho AI nghỉ mệt 5 giây trước khi nấu file tiếp theo...")
            time.sleep(5)
            
    print("\n🎉 XUẤT SẮC! ĐÃ DỌN SẠCH KHO TRUYỆN!")

if __name__ == "__main__":
    create_novel_scripts()