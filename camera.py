# camera.py
import subprocess
import os
import base64
from config import DATA_DIR

def capture_image_base64() -> str:
    temp_path = os.path.join(DATA_DIR, "temp", "snapshot.jpg")
    
    # fswebcam: -r resolución, --no-banner elimina la barra de fecha/hora inferior
    cmd_usb = [
        "fswebcam", "-r", "1024x768", "--no-banner", temp_path
    ]
    
    try:
        subprocess.run(cmd_usb, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if os.path.exists(temp_path):
            with open(temp_path, "rb") as image_file:
                encoded = base64.b64encode(image_file.read()).decode("utf-8")
            os.remove(temp_path)
            return encoded
        else:
            return "Error: fswebcam se ejecutó pero no generó el archivo de imagen."
    except subprocess.CalledProcessError as e:
        return f"Error de proceso V4L2 (USB): {str(e)}"
    except Exception as e:
        return f"Error general al capturar: {str(e)}"

if __name__ == "__main__":
    print("Iniciando prueba de captura de hardware (USB Webcam)...")
    result = capture_image_base64()
    if result.startswith("Error"):
        print(result)
    else:
        print(f"Captura exitosa. Longitud Base64: {len(result)} caracteres.")
