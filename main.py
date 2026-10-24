# main.py
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN, ALLOWED_CHAT_ID
from agent import process_user_message

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ALLOWED_CHAT_ID:
        logging.warning(f"Intento de acceso denegado (ID: {user_id})")
        return

    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=user_id, action="typing")
    
    try:
        reply = process_user_message(user_text)
        await update.message.reply_text(reply, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Error LLM: {e}")
        await update.message.reply_text("Fallo interno en el pipeline de IA.")

if __name__ == '__main__':
    print("[SYSTEM] Iniciando Daemon del Asistente en Raspberry Pi...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
