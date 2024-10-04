# Gemini Telegram Bot

Đây là một Telegram bot được hỗ trợ bởi Google's Gemini AI, có khả năng xử lý cả văn bản và hình ảnh. Toàn bộ source code của Dự án này được viết trên ngôn ngữ Python, bởi Claude 3.5 Sonnet theo yêu cầu và workflow mà Huân đưa ra, sau đó chỉnh sửa và thêm thắt các ý tưởng, các chức năng thêm cho hoàn chỉnh.

## Tính năng

- Xử lý tin nhắn văn bản
- Phân tích hình ảnh (với hoặc không có caption)
- Xử lý file PDF
- Giới hạn quyền truy cập cho người dùng cụ thể
- Lưu trữ và sử dụng lịch sử hội thoại
- Định dạng phản hồi bằng HTML

## Yêu cầu

- Python 3.11+ (Huân đang dùng Python 3.11 trên Ubuntu 20.04 nhé). Nếu dùng phiên bản thấp hơn của Python3 thì khả năng không cập nhật được các thư viện cần thiết cho Dự án này.
- Một Telegram Bot Token (dùng BotFather tạo bot mới và lấy token)
- Một Google API Key cho Gemini.

## Cài đặt
1. Clone repository này:
```
git clone https://github.com/kevinkieu/gemini-stable.git
```
và di chuyển đến thư mục gốc của dự án:
```
cd gemini-stable
```

2. Cài đặt các thư viện cần thiết:
```
pip install python-telegram-bot google-generativeai python-dotenv Pillow pdfplumber
```

3. Tạo file `.env` trong thư mục gốc của dự án và thêm các thông tin sau:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GOOGLE_API_KEY=your_google_api_key_here
ALLOWED_USERS=username1,username2,username3
```
Lưu ý nếu ko có file .env chứa các biến này thì bot không hoạt động nhé.

4. Tạo file `system_instruction.txt` trong thư mục gốc và thêm hướng dẫn hệ thống cho bot:
You are a helpful AI assistant (vân vân, tự bạn thêm vào nhé...).


## Cấu trúc dự án

- `main.py`: File chính để chạy bot
- `telegram_handler.py`: Xử lý các tương tác Telegram
- `gemini_handler.py`: Xử lý tương tác với API Gemini
- `config.py`: Cấu hình và biến môi trường
- `conversation_manager.py`: Quản lý lịch sử hội thoại
- `utils.py`: Các hàm tiện ích
- `html_format.py`: Định dạng tin nhắn HTML
- `system_instruction.txt`: Hướng dẫn hệ thống cho bot

## Sử dụng

1. Chạy bot:
```
python main.py
```
hoặc
```
python3 main.py
```

2. Trong Telegram, bắt đầu một cuộc trò chuyện với bot của bạn.

3. Gửi tin nhắn văn bản hoặc hình ảnh để nhận phản hồi từ bot.

## Lệnh

- `/start`: Bắt đầu cuộc trò chuyện với bot
- `/clear`: Xóa lịch sử hội thoại

## Tùy chỉnh

- Để thay đổi hướng dẫn hệ thống, chỉnh sửa file `system_instruction.txt`.
- Để thêm hoặc xóa người dùng được phép, cập nhật `ALLOWED_USERS` trong file `.env`.

## Đóng góp

Mọi đóng góp đều được hoan nghênh. Vui lòng mở một issue hoặc tạo pull request để đóng góp. Hoặc có thể ping Huân qua Telegram nhé _@huank8895_.

