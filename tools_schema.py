# tools_schema.py

TOOLS = [
        {
        "name": "get_calendar_events",
        "description": "Obtiene los próximos eventos agendados en Google Calendar.",
        "input_schema": {
            "type": "object",
            "properties": {
                "max_results": {"type": "integer", "description": "Número máximo de eventos a devolver (default 5)."}
            }
        }
    },
    {
        "name": "create_calendar_event",
        "description": "Crea un nuevo evento o recordatorio en Google Calendar.",
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "description": "Título del evento o recordatorio"},
                "start_time": {"type": "string", "description": "Fecha y hora de inicio en formato ISO 8601 (ej. 2026-10-25T10:00:00-06:00)"},
                "end_time": {"type": "string", "description": "Fecha y hora de fin en formato ISO 8601 (ej. 2026-10-25T11:00:00-06:00)"}
            },
            "required": ["summary", "start_time", "end_time"]
        }
    },
    {
        "name": "fetch_web_content",
        "description": "Descarga y extrae el texto principal de una URL web. Útil para leer artículos o documentaciones.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "La URL completa a leer"}
            },
            "required": ["url"]
        }
    },
    {
        "name": "get_system_metrics",
        "description": "Obtiene el estado del hardware de la Raspberry Pi (RAM, CPU, Temperatura) para diagnosticar cuellos de botella térmicos o de memoria.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "trigger_local_webhook",
        "description": "Envía una petición POST a un servicio local en la red (ej. Home Assistant, Node-RED) para desencadenar acciones domóticas.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL local del webhook (ej. http://192.168.1.X:8123/api/webhook/id)"},
                "payload": {"type": "string", "description": "Cadena JSON con los datos a enviar"}
            },
            "required": ["url"]
        }
    },
    {
        "name": "save_note",
        "description": "Guarda una nota o resumen estructurado en un archivo Markdown local.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Título breve (usa guiones, sin espacios)"},
                "content": {"type": "string", "description": "Contenido en formato Markdown"},
                "category": {"type": "string", "description": "Categoría (ej. dev, ideas, general)"}
            },
            "required": ["title", "content", "category"]
        }
    },
    {
        "name": "manage_tasks",
        "description": "Gestiona una lista de tareas locales. Permite agregar, listar o completar tareas.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["add", "list", "complete"]},
                "description": {"type": "string", "description": "Descripción de la tarea (solo para 'add')"},
                "task_id": {"type": "integer", "description": "ID de la tarea (solo para 'complete')"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "capture_and_analyze_image",
        "description": "Activa la cámara, toma una foto y la devuelve para análisis visual.",
        "input_schema": {
            "type": "object",
            "properties": {
                "instruction": {"type": "string", "description": "Qué buscar en la imagen (ej. 'describe el entorno')."}
            },
            "required": ["instruction"]
        }
    }
]
