# tool_executor.py
import os
import json
import subprocess
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
import psutil

# Librerías de Google Cloud (OAuth 2.0 y API de Calendar)
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from config import DATA_DIR
from camera import capture_image_base64

def execute_tool(tool_name: str, tool_args: dict) -> dict:
    try:
        if tool_name == "fetch_web_content":
            return fetch_web_content(tool_args["url"])
        elif tool_name == "save_note":
            return save_note(tool_args["title"], tool_args["content"], tool_args["category"])
        elif tool_name == "manage_tasks":
            return manage_tasks(tool_args["action"], tool_args.get("description"), tool_args.get("task_id"))
        elif tool_name == "get_system_metrics":
            return get_system_metrics()
        elif tool_name == "trigger_local_webhook":
            return trigger_local_webhook(tool_args["url"], tool_args.get("payload", "{}"))
        elif tool_name == "capture_and_analyze_image":
            img_b64 = capture_image_base64()
            if img_b64.startswith("Error"):
                return {"error": img_b64}
            return {"_internal_type": "image", "data": img_b64, "instruction": tool_args["instruction"]}
        # --- Integración de Google Calendar ---
        elif tool_name == "get_calendar_events":
            return get_calendar_events(tool_args.get("max_results", 5))
        elif tool_name == "create_calendar_event":
            return create_calendar_event(tool_args["summary"], tool_args["start_time"], tool_args["end_time"])
        else:
            return {"error": f"Herramienta {tool_name} desconocida."}
    except Exception as e:
        return {"error": str(e)}

# --- Funciones de Herramientas Existentes ---

def fetch_web_content(url: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text(separator="\n", strip=True)
    return {"content": text[:8000]} # Limitamos tokens para evitar OOM (Out Of Memory) en inferencia

def save_note(title: str, content: str, category: str) -> dict:
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_str}_{category}_{title}.md"
    filepath = os.path.join(DATA_DIR, "notes", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return {"status": "success", "filepath": filepath}

def manage_tasks(action: str, description: str = None, task_id: int = None) -> dict:
    tasks_file = os.path.join(DATA_DIR, "tasks.json")
    if not os.path.exists(tasks_file):
        with open(tasks_file, "w") as f:
            json.dump({"tasks": []}, f)
            
    with open(tasks_file, "r") as f:
        data = json.load(f)
        
    if action == "add":
        new_id = max([t["id"] for t in data["tasks"]] + [0]) + 1
        data["tasks"].append({"id": new_id, "desc": description, "done": False})
        res = f"Tarea añadida con ID {new_id}"
    elif action == "list":
        res = [t for t in data["tasks"] if not t["done"]]
    elif action == "complete":
        for t in data["tasks"]:
            if t["id"] == task_id:
                t["done"] = True
        res = f"Tarea {task_id} completada."
        
    with open(tasks_file, "w") as f:
        json.dump(data, f)
    return {"result": res}

def get_system_metrics() -> dict:
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        temp_str = subprocess.check_output(["vcgencmd", "measure_temp"]).decode("utf-8").strip()
        return {
            "cpu_percent": cpu,
            "ram_used_mb": ram.used // (1024 * 1024),
            "ram_free_mb": ram.available // (1024 * 1024),
            "temperature": temp_str
        }
    except Exception as e:
        return {"error": str(e)}

def trigger_local_webhook(url: str, payload: str) -> dict:
    try:
        data = json.loads(payload) if payload else {}
        res = requests.post(url, json=data, timeout=5)
        return {"status_code": res.status_code, "response": res.text[:200]}
    except Exception as e:
        return {"error": str(e)}

# --- Funciones Nuevas de Google Calendar ---

def get_calendar_service():
    """Valida el token OAuth y construye el cliente de la API"""
    creds = None
    # Usamos ruta absoluta para garantizar lectura por parte del servicio systemd
    token_path = '/home/lombrix8/pi_assistant/token.json'
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/calendar'])
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("Token inválido o no encontrado. Ejecuta auth_calendar.py.")
    return build('calendar', 'v3', credentials=creds)

def get_calendar_events(max_results: int = 5) -> dict:
    try:
        service = get_calendar_service()
        # Generar timestamp actual en UTC respetando ISO 8601
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=max_results, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        
        if not events:
            return {"resultado": "No tienes próximos eventos agendados."}
            
        lista_eventos = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            lista_eventos.append({"fecha": start, "titulo": event['summary']})
        return {"eventos": lista_eventos}
    except Exception as e:
        return {"error": str(e)}

def create_calendar_event(summary: str, start_time: str, end_time: str) -> dict:
    try:
        service = get_calendar_service()
        event = {
          'summary': summary,
          'start': {'dateTime': start_time, 'timeZone': 'America/Mexico_City'},
          'end': {'dateTime': end_time, 'timeZone': 'America/Mexico_City'},
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        return {"status": "success", "link": event.get('htmlLink')}
    except Exception as e:
        return {"error": str(e)}
