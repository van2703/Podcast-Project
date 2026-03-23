@echo off
echo Đang di chuyển vào thư mục dự án...
cd "D:\Workspace\Podcast"

echo Đang kích hoạt môi trường ảo (nếu có)...
call venv\Scripts\activate

echo Đang chạy file Python chính...
python main.py

echo Đang đẩy code lên GitHub...
git add .
git commit -m "Auto-update daily podcast"
git push origin main

echo Hoàn thành!