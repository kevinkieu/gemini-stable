import asyncio
from io import BytesIO
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram.error import BadRequest, NetworkError
from gemini_handler import generate_text, analyze_image
from conversation_manager import ConversationManager
from utils import is_user_allowed
from html_format import format_message
from PIL import Image
from config import SYSTEM_INSTRUCTION

conversation_manager = ConversationManager()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Xin chào! Tôi là bot Telegram được hỗ trợ bởi Gemini. Tôi có thể giúp gì cho bạn hôm nay?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_user_allowed(update.effective_user.username):
        await update.message.reply_text("Xin lỗi, bạn không được phép sử dụng bot này.")
        return

    user_id = update.effective_user.id
    user_input = update.message.text

    conversation_manager.add_message(user_id, "user", user_input)
    history = conversation_manager.get_history(user_id)

    init_msg = await update.message.reply_text("Đang suy nghĩ...")

    try:
        response = generate_text(user_input, SYSTEM_INSTRUCTION, history)
        full_response = ""

        for chunk in response:
            if chunk.text:
                full_response += chunk.text
                formatted_response = format_message(full_response)
                try:
                    init_msg = await init_msg.edit_text(
                        text=formatted_response,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True,
                    )
                except BadRequest:
                    init_msg = await update.message.reply_text(
                        text=formatted_response,
                        parse_mode=ParseMode.HTML,
                        reply_to_message_id=init_msg.message_id,
                        disable_web_page_preview=True,
                    )
            await asyncio.sleep(0.1)

        conversation_manager.add_message(user_id, "model", full_response)

    except NetworkError:
        await init_msg.edit_text("Có vẻ như mạng của bạn đang gặp vấn đề. Vui lòng thử lại sau.")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
        await init_msg.edit_text("Đã xảy ra lỗi trong quá trình xử lý. Vui lòng thử lại.")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_user_allowed(update.effective_user.username):
        await update.message.reply_text("Xin lỗi, bạn không được phép sử dụng bot này.")
        return

    init_msg = await update.message.reply_text(
        text="Đang xử lý hình ảnh...",
        reply_to_message_id=update.message.message_id
    )

    file = await update.message.photo[-1].get_file()
    image_bytes = await file.download_as_bytearray()
    image = Image.open(BytesIO(image_bytes))

    prompt = update.message.caption if update.message.caption else "Phân tích hình ảnh này và tạo phản hồi"

    try:
        response = analyze_image(image, prompt)
        full_response = ""

        for chunk in response:
            if chunk.text:
                full_response += chunk.text
                formatted_response = format_message(full_response)
                try:
                    init_msg = await init_msg.edit_text(
                        text=formatted_response,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True,
                    )
                except BadRequest:
                    init_msg = await update.message.reply_text(
                        text=formatted_response,
                        parse_mode=ParseMode.HTML,
                        reply_to_message_id=init_msg.message_id,
                        disable_web_page_preview=True,
                    )
            await asyncio.sleep(0.1)

        user_id = update.effective_user.id
        conversation_manager.add_message(user_id, "user", f"Đã gửi một hình ảnh với prompt: {prompt}")
        conversation_manager.add_message(user_id, "model", full_response)

    except NetworkError:
        await init_msg.edit_text("Có vẻ như mạng của bạn đang gặp vấn đề. Vui lòng thử lại sau.")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
        await init_msg.edit_text("Đã xảy ra lỗi trong quá trình xử lý hình ảnh. Vui lòng thử lại.")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_user_allowed(update.effective_user.username):
        await update.message.reply_text("Xin lỗi, bạn không được phép sử dụng bot này.")
        return

    user_id = update.effective_user.id
    conversation_manager.clear_history(user_id)
    await update.message.reply_text("Lịch sử hội thoại đã được xóa.")