# main.py
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN, ALLOWED_CHAT_ID
from agent import process_user_message
from transcriber import transcribe_voice  # <-- Importamos nuestro motor STT Edge

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ALLOWED_CHAT_ID:
        logging.warning(f"Intento de acceso denegado (ID: {user_id})")
        return

    # 1. Ruteo Multimodal: Texto vs Voz
    if update.message.text:
        user_input = update.message.text
        
    elif update.message.voice:
        # UX: Indicador de procesamiento Edge para mitigar la percepción de latencia
        await context.bot.send_message(
            chat_id=user_id, 
            text="🎙️ *Escuchando y transcribiendo en local...*", 
            parse_mode="Markdown"
        )
        
        file_id = update.message.voice.file_id
        
        try:
            # Inferencia STT (Whisper INT8 en CPU ARM64)
            user_input = transcribe_voice(file_id)
            logging.info(f"[VOZ -> TEXTO]: {user_input}")
        except Exception as e:
            logging.error(f"Error en transcripción STT local: {e}")
            await update.message.reply_text("Fallo al transcribir el audio en la Raspberry.")
            return
    else:
        # Ignoramos silenciosamente stickers, imágenes, etc. (por ahora)
        return

    # 2. Inferencia NLP (Claude Haiku + Tool Use)
    await context.bot.send_chat_action(chat_id=user_id, action="typing")

    try:
        reply = process_user_message(user_input)
        await update.message.reply_text(reply, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Error LLM: {e}")
        await update.message.reply_text("Fallo interno en el pipeline de IA.")

if __name__ == '__main__':
    print("[SYSTEM] Iniciando Daemon del Asistente en Raspberry Pi (Soporte Multimodal activado)...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    # IMPORTANTE: Modificamos el filtro para escuchar Texto (TEXT) y Notas de voz (VOICE)
    app.add_handler(MessageHandler((filters.TEXT | filters.VOICE) & (~filters.COMMAND), handle_message))
    app.run_polling()
