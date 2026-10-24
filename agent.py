# agent.py
import anthropic
import datetime
from config import ANTHROPIC_API_KEY
from tools_schema import TOOLS
from tool_executor import execute_tool

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
conversation_history = []

def process_user_message(user_text: str) -> str:
    global conversation_history
    conversation_history.append({"role": "user", "content": user_text})

    # Mantenemos el contexto ligero (últimos 10 mensajes) para ahorrar RAM
    if len(conversation_history) > 10:
        conversation_history = conversation_history[-10:]

    while True:
        # Inyección de consciencia temporal para cálculo preciso de fechas relativas
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S (Zona horaria: America/Mexico_City)")
        prompt_sistema = f"Eres un asistente personal avanzado corriendo localmente en una Raspberry Pi vía Telegram. Tienes herramientas de sistema. La fecha y hora actual del sistema es: {fecha_actual}."

        response = client.messages.create(
            model="claude-haiku-5-5",
            max_tokens=2048,
            tools=TOOLS,
            messages=conversation_history,
            system=prompt_sistema
        )

        conversation_history.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "tool_use":
            tool_results_content = []

            for block in response.content:
                if block.type == "tool_use":
                    print(f"[EDGE AI] Ejecutando: {block.name}")
                    result = execute_tool(block.name, block.input)

                    if isinstance(result, dict) and result.get("_internal_type") == "image":
                        tool_results_content.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": [
                                {"type": "text", "text": "Imagen capturada:"},
                                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": result["data"]}}
                            ]
                        })
                    else:
                        # Retorno de texto estándar para el resto de herramientas (Calendar, Notas, SysMetrics)
                        tool_results_content.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result)
                        })
            
            # Devolvemos los resultados al modelo para que genere la respuesta final
            conversation_history.append({"role": "user", "content": tool_results_content})
        
        else:
            # Extracción del bloque de texto final y ruptura del bucle
            final_text = next((block.text for block in response.content if block.type == "text"), "")
            return final_text
