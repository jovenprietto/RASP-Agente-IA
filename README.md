# 🤖 RASP-Agente-IA (Edge AI Assistant)

Asistente de Inteligencia Artificial de arquitectura híbrida, desplegado en el borde (Edge) para ejecución continua, monitoreo de hardware e integración con servicios en la nube.

## ⚙️ Arquitectura de Hardware
* **Host:** Raspberry Pi 4 Model B (8GB RAM)
* **OS:** Raspberry Pi OS aarch64 (Bookworm)
* **Refrigeración:** GeeekPi ICE Tower Cooler

## 🛠️ Stack Tecnológico
* **Motor Lógico:** Anthropic Claude 3.5 Haiku (Vía API).
* **Entorno:** Python 3.13 (Entorno virtual PEP 668 aislado).
* **Orquestación de Procesos:** `systemd` (Ejecución en background / Daemon).
* **Canal de Interfaz:** API de Telegram (Bot).
* **Integraciones Cloud:** Google Calendar API v3 (OAuth 2.0 Headless).

## 🚀 Capacidades y Tool Use (Llamada a Funciones)
El motor LLM cuenta con consciencia temporal y ruteo lógico para ejecutar código Python en respuesta a lenguaje natural:
1. **Control de Agenda (CRUD):** Lectura y escritura dinámica en Google Calendar calculando fechas relativas.
2. **Telemetría de Sistema:** Extracción en tiempo real de métricas (Temperatura BCM2711, RAM libre/usada, % CPU) mediante `psutil`.
3. **Gestión de Tareas y Notas:** E/S en disco local para listas de pendientes y resúmenes de texto.
4. **Web Fetching:** Extracción y limpieza de contenido web (BeautifulSoup).

## 🔒 Seguridad
Las API Keys (Anthropic, Telegram) y los tokens criptográficos de Google Identity (`token.json`) se mantienen estrictamente aislados en variables de entorno y archivos locales ignorados por el control de versiones.
