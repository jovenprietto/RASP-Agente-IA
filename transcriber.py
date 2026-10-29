import os
import requests
from faster_whisper import WhisperModel
from config import TELEGRAM_BOT_TOKEN

# Inicializamos el modelo en CPU con precisión INT8 (Optimizado para ARM/Raspberry Pi)
# El modelo 'tiny' pesa ~150MB en RAM y es muy rápido. 
# Si quieres más precisión (y toleras 1-2 segundos más de latencia), cambia a 'base' o 'small'.
print("[SISTEMA] Cargando modelo Whisper (tiny) en memoria...")
model = WhisperModel("tiny", device="cpu", compute_type="int8")

def download_telegram_voice(file_id: str) -> str:
    """Obtiene la ruta del archivo de los servidores de Telegram y lo descarga localmente."""
    url_get_file = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}"
    res = requests.get(url_get_file).json()
    
    if not res.get("ok"):
        raise Exception("Error obteniendo el archivo de Telegram")
        
    file_path_tg = res["result"]["file_path"]
    download_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path_tg}"
    
    # Descargar a disco temporalmente
    local_filename = f"/tmp/{file_id}.ogg"
    audio_data = requests.get(download_url).content
    with open(local_filename, "wb") as f:
        f.write(audio_data)
        
    return local_filename

def transcribe_voice(file_id: str) -> str:
    """Descarga y transcribe la nota de voz a texto."""
    try:
        # 1. Descargar
        audio_path = download_telegram_voice(file_id)
        
        # 2. Transcribir
        print(f"[EDGE AI] Transcribiendo nota de voz...")
        segments, info = model.transcribe(audio_path, beam_size=5, language="es")
        
        texto_transcrito = "".join([segment.text for segment in segments])
        
        # 3. Limpiar archivo temporal para no llenar la SD
        os.remove(audio_path)
        
        return texto_transcrito.strip()
    except Exception as e:
        return f"[Error en transcripción: {str(e)}]"
