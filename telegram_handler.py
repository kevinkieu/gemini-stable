import asyncio
import logging
from io import BytesIO
import os
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram.error import TelegramError, BadRequest, NetworkError, TimedOut
from gemini_handler import generate_text, analyze_image, process_pdf
from conversation_manager import ConversationManager
from utils import is_user_allowed
from html_format import format_message
from PIL import Image
from config import SYSTEM_INSTRUCTION, TELEGRAM_MSG_CHAR_LIMIT

# Thiết lập logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

conversation_manager = ConversationManager()

async def retry_on_timeout(func, max_retries=3, delay=1):
    for attempt in range(max_retries):
        try:
            return await func()
        except TimedOut as e:
            if attempt == max_retries - 1:
                raise e
            logger.warning(f"Request timed out. Retrying in {delay} seconds...")
            await asyncio.sleep(delay)
            delay *= 2

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Xin chào! Tôi là bot Telegram được hỗ trợ bởi Gemini. Tôi có thể giúp gì cho bạn hôm nay?")

async def send_long_message(update: Update, text: str, parse_mode=None):
    parts = []
    current_part = ""

    for line in text.split('\n'):
        if len(current_part) + len(line) + 1 <= TELEGRAM_MSG_CHAR_LIMIT:
            current_part += line + '\n'
        else:
            if current_part:
                parts.append(current_part.strip())
            current_part = line + '\n'
    
    if current_part:
        parts.append(current_part.strip())

    first_message = None
    for i, part in enumerate(parts):
        try:
            if i == 0:
                first_message = await retry_on_timeout(lambda: update.message.reply_text(part, parse_mode=parse_mode))
            else:
                await retry_on_timeout(lambda: update.message.reply_text(part, parse_mode=parse_mode, reply_to_message_id=first_message.message_id))
        except TelegramError as e:
            logger.error(f"Error sending message part {i}: {e}")
        await asyncio.sleep(0.1)

    return first_message

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_user_allowed(update.effective_user.username):
        await update.message.reply_text("Xin lỗi, bạn không được phép sử dụng bot này.")
        return

    user_id = update.effective_user.id
    user_input = update.message.text

    conversation_manager.add_message(user_id, "user", user_input)
    history = conversation_manager.get_history(user_id)

    try:
        init_msg = await retry_on_timeout(lambda: update.message.reply_text("Đang suy nghĩ..."))
    except TimedOut:
        logger.error("Failed to send initial message after multiple retries")
        return

    try:
        response = generate_text(user_input, SYSTEM_INSTRUCTION, history)
        full_response = ""

        for text in response:
            full_response += text
            formatted_response = format_message(full_response)
            
            try:
                if len(formatted_response) > TELEGRAM_MSG_CHAR_LIMIT:
                    await init_msg.delete()
                    init_msg = await send_long_message(update, formatted_response, parse_mode=ParseMode.HTML)
                else:
                    await retry_on_timeout(lambda: init_msg.edit_text(formatted_response, parse_mode=ParseMode.HTML))
            except BadRequest as e:
                if "Message is not modified" not in str(e):
                    logger.warning(f"BadRequest error: {e}")
                    await init_msg.delete()
                    init_msg = await send_long_message(update, formatted_response, parse_mode=ParseMode.HTML)
            except TelegramError as e:
                logger.error(f"Telegram error when updating message: {e}")
                try:
                    await send_long_message(update, formatted_response, parse_mode=ParseMode.HTML)
                except TelegramError as e2:
                    logger.error(f"Failed to send new message after error: {e2}")
                    break

            await asyncio.sleep(0.1)

        conversation_manager.add_message(user_id, "model", full_response)

    except NetworkError as e:
        logger.error(f"Network error: {e}")
        await update.message.reply_text("Có vẻ như mạng đang gặp vấn đề. Vui lòng thử lại sau.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await update.message.reply_text("Đã xảy ra lỗi không mong đợi. Vui lòng thử lại sau.")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_user_allowed(update.effective_user.username):
        await update.message.reply_text("Xin lỗi, bạn không được phép sử dụng bot này.")
        return

    try:
        init_msg = await retry_on_timeout(lambda: update.message.reply_text("Đang xử lý hình ảnh...", reply_to_message_id=update.message.message_id))
    except TimedOut:
        logger.error("Failed to send initial message after multiple retries")
        return

    try:
        file = await update.message.photo[-1].get_file()
        image_bytes = await file.download_as_bytearray()
        image = Image.open(BytesIO(image_bytes))

        prompt = update.message.caption if update.message.caption else "Phân tích hình ảnh này và tạo phản hồi"

        response = analyze_image(image, prompt)
        full_response = ""

        for text in response:
            full_response += text
            formatted_response = format_message(full_response)
            
            try:
                if len(formatted_response) > TELEGRAM_MSG_CHAR_LIMIT:
                    await init_msg.delete()
                    init_msg = await send_long_message(update, formatted_response, parse_mode=ParseMode.HTML)
                else:
                    await retry_on_timeout(lambda: init_msg.edit_text(formatted_response, parse_mode=ParseMode.HTML))
            except BadRequest as e:
                if "Message is not modified" not in str(e):
                    logger.warning(f"BadRequest error: {e}")
                    await init_msg.delete()
                    init_msg = await send_long_message(update, formatted_response, parse_mode=ParseMode.HTML)
            except TelegramError as e:
                logger.error(f"Telegram error when updating message: {e}")
                try:
                    await send_long_message(update, formatted_response, parse_mode=ParseMode.HTML)
                except TelegramError as e2:
                    logger.error(f"Failed to send new message after error: {e2}")
                    break

            await asyncio.sleep(0.1)

        user_id = update.effective_user.id
        conversation_manager.add_message(user_id, "user", f"Đã gửi một hình ảnh với prompt: {prompt}")
        conversation_manager.add_message(user_id, "model", full_response)

    except NetworkError as e:
        logger.error(f"Network error: {e}")
        await update.message.reply_text("Có vẻ như mạng đang gặp vấn đề. Vui lòng thử lại sau.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await update.message.reply_text("Đã xảy ra lỗi không mong đợi khi xử lý hình ảnh. Vui lòng thử lại sau.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_user_allowed(update.effective_user.username):
        await update.message.reply_text("Xin lỗi, bạn không được phép sử dụng bot này.")
        return

    document = update.message.document
    if document.file_name.lower().endswith('.pdf'):
        try:
            init_msg = await retry_on_timeout(lambda: update.message.reply_text("Đang xử lý file PDF..."))
            file = await document.get_file()
            file_path = f"temp_{update.effective_user.id}.pdf"
            await file.download_to_drive(file_path)

            prompt = "Hãy tóm tắt nội dung chính của file PDF này."
            if update.message.caption:
                prompt = update.message.caption

            response = process_pdf(file_path, prompt)
            full_response = ""

            for text in response:
                full_response += text
                formatted_response = format_message(full_response)
                
                try:
                    if len(formatted_response) > TELEGRAM_MSG_CHAR_LIMIT:
                        await init_msg.delete()
                        init_msg = await send_long_message(update, formatted_response, parse_mode=ParseMode.HTML)
                    else:
                        await retry_on_timeout(lambda: init_msg.edit_text(formatted_response, parse_mode=ParseMode.HTML))
                except BadRequest as e:
                    if "Message is not modified" not in str(e):
                        logger.warning(f"BadRequest error: {e}")
                        await init_msg.delete()
                        init_msg = await send_long_message(update, formatted_response, parse_mode=ParseMode.HTML)
                except TelegramError as e:
                    logger.error(f"Telegram error when updating message: {e}")
                    try:
                        await send_long_message(update, formatted_response, parse_mode=ParseMode.HTML)
                    except TelegramError as e2:
                        logger.error(f"Failed to send new message after error: {e2}")
                        break

                await asyncio.sleep(0.1)

            os.remove(file_path)  # Clean up the temporary file

        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            await update.message.reply_text("Có lỗi xảy ra khi xử lý file PDF. Vui lòng thử lại sau.")
    else:
        await update.message.reply_text("Xin lỗi, tôi chỉ có thể xử lý file PDF.")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_user_allowed(update.effective_user.username):
        await update.message.reply_text("Xin lỗi, bạn không được phép sử dụng bot này.")
        return

    user_id = update.effective_user.id
    conversation_manager.clear_history(user_id)
    await update.message.reply_text("Lịch sử hội thoại đã được xóa.")