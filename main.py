import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN
from telegram_handler import start, handle_message, handle_image, handle_document, clear

# Thiết lập logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Khởi tạo ứng dụng với token bot
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Thêm các handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear", clear))
    
    # Handler cho tin nhắn văn bản
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Handler cho hình ảnh
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    
    # Handler cho file PDF
    application.add_handler(MessageHandler(filters.Document.PDF, handle_document))

    # Log khi bot bắt đầu
    logger.info("Bot is starting...")
    
    # Bắt đầu polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()