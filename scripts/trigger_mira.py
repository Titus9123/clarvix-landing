"""
trigger_mira.py — Trigger autónomo de MIRA (Social Media & Ads Director)
=========================================================================
Ejecutado por GitHub Actions en los horarios definidos.
Llama a la Anthropic API con el system prompt de MIRA + tools del MCP.
Maneja el loop de tool use hasta que MIRA termina su tarea.

Variables de entorno requeridas:
  ANTHROPIC_API_KEY  — clave de Anthropic
  MCP_URL            — https://mcp.clarvix.net/mcp
  MCP_API_KEY        — X-API-Key del MCP server (si aplica)
  MIRA_MODE          — DAILY | ADS_MANAGER | OPTIMIZE | CAMPAIGN
  MIRA_NOTE          — instrucción adicional (opcional)
"""

import os
import sys
import json
import requests
from datetime import datetime

# ─── CONFIG ──────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
MCP_URL           = os.environ.get('MCP_URL', 'https://mcp.clarvix.net/mcp')
MCP_API_KEY       = os.environ.get('MCP_API_KEY', '')
MIRA_MODE         = os.environ.get('MIRA_MODE', 'DAILY').upper()
MIRA_NOTE         = os.environ.get('MIRA_NOTE', '')
MAX_ITERATIONS    = 10
MODEL             = 'claude-sonnet-4-6'

if not ANTHROPIC_API_KEY:
    print("ERROR: ANTHROPIC_API_KEY no configurada en GitHub Secrets")
    sys.exit(1)

# ─── MIRA SYSTEM PROMPT ──────────────────────────────────────────────────────
MIRA_SYSTEM_PROMPT = """Eres MIRA, la Directora de Social Media y Facebook Ads de Clarvix Digital Agency Israel.

MISIÓN: Convertir las redes sociales de Clarvix en la fuente #1 de leads de calidad para los 4 servicios.

AL RECIBIR ESTE TRIGGER:
1. get_clarvix_profile() → carga servicios, precios, ICP actualizado
2. get_learnings() → carga tu memoria editorial: qué funcionó, qué no
3. read_mailbox() → ¿hay instrucción de ALEX o señal de DROR?
4. get_content_history(14) → últimos 14 posts para no repetir
5. Según el MODO, ejecuta y publica

TUS 4 MODOS:

MODO DAILY (09:00 IL, Dom-Vie):
Genera y publica el contenido del día. Decide si es post o carrusel.
- Lunes: carrusel educativo ("X señales que tu negocio necesita [servicio]")
- Martes: case study o antes/después
- Miércoles: post de dato impactante israelí (stat local)
- Jueves: carrusel de conversión directa o testimonial
- Viernes: post ligero pre-Shabbat (cultura, team, humor profesional)
Siempre: save_content() primero → luego post_to_instagram() + post_to_facebook()
Cierre: store_learning('mira_daily_decision', {fecha, tipo, servicio, hook, plataforma})

MODO ADS_MANAGER (Martes y Viernes):
Lee métricas de ads. Detecta underperformers y winners.
Propuesta estructurada → send_mailbox(to: CEO) si requiere cambio de presupuesto.
Ajustes menores (pausa/escala sin cambio de presupuesto) → ejecuta autónomo.
Cierre: store_learning('mira_ads_optimization', {semana, acciones, justificación})

MODO OPTIMIZE (Sábados):
Análisis profundo semanal completo.
Propuesta de estrategia para la semana siguiente.
send_mailbox(to: CEO) con resumen ejecutivo + recomendaciones claras.
Cierre: store_learning('mira_weekly_optimization', {semana, insights, estrategia_próxima})

REGLAS DE ORO:
- Todo post se guarda con save_content() ANTES de publicar
- NUNCA gastes en ads sin aprobación explícita de ALEX (envía propuesta, no ejecutes)
- IDIOMA DEFAULT: Hebreo (mercado israelí). Árabe si el post es para ese segmento
- UN solo idioma por post — NUNCA mezcles
- COLORES Clarvix hardcodeados: #080d1a (fondo) / #1a6bff (accent) / #f1f5f9 (texto)
- FUENTE: Heebo siempre (Google Fonts)
- PREGUNTA FILTRO antes de publicar: "¿Un dueño de negocio en Beer Sheva dejaría de scrollear?"
- store_learning() siempre al cerrar cada run

CONTACTO CLARVIX:
contact@clarvix.net | +972-53-946-4262 | clarvix.net | Albert es el fundador
"""

# ─── TOOLS (subset relevante para MIRA) ──────────────────────────────────────
MIRA_TOOLS = [
    {
        "name": "get_clarvix_profile",
        "description": "Retorna servicios activos, precios, ICP y upsell matrix de Clarvix.",
        "input_schema": {"type": "object", "properties": {"section": {"type": "string"}}}
    },
    {
        "name": "get_learnings",
        "description": "Recupera aprendizajes guardados — memoria editorial acumulada de MIRA.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_name": {"type": "string"},
                "category":   {"type": "string"},
                "limit":      {"type": "integer"}
            }
        }
    },
    {
        "name": "store_learning",
        "description": "Guarda un aprendizaje al cerrar cada run.",
        "input_schema": {
            "type": "object",
            "required": ["agent_name", "category", "content"],
            "properties": {
                "agent_name": {"type": "string"},
                "category":   {"type": "string"},
                "content":    {"type": "string"},
                "confidence": {"type": "number"}
            }
        }
    },
    {
        "name": "read_mailbox",
        "description": "Lee mensajes no leídos del buzón — instrucciones de ALEX o señales de DROR.",
        "input_schema": {
            "type": "object",
            "properties": {"all": {"type": "boolean"}, "limit": {"type": "integer"}}
        }
    },
    {
        "name": "send_mailbox",
        "description": "Envía mensaje al buzón del CEO (propuestas de ads, reportes).",
        "input_schema": {
            "type": "object",
            "required": ["from_agent", "subject", "body"],
            "properties": {
                "from_agent":   {"type": "string"},
                "to_agent":     {"type": "string"},
                "message_type": {"type": "string"},
                "subject":      {"type": "string"},
                "body":         {"type": "string"},
                "data":         {"type": "object"}
            }
        }
    },
    {
        "name": "get_content_history",
        "description": "Últimos N posts publicados para evitar repetición de temas o hooks.",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit":    {"type": "integer"},
                "platform": {"type": "string"},
                "service":  {"type": "string"}
            }
        }
    },
    {
        "name": "save_content",
        "description": "Guarda el post/carrusel en DB antes de publicarlo. Siempre llamar antes de post_to_*.",
        "input_schema": {
            "type": "object",
            "required": ["agent_name", "platform", "content_type", "caption"],
            "properties": {
                "agent_name":    {"type": "string"},
                "platform":      {"type": "string"},
                "content_type":  {"type": "string"},
                "caption":       {"type": "string"},
                "image_url":     {"type": "string"},
                "hashtags":      {"type": "string"},
                "language":      {"type": "string"},
                "service_focus": {"type": "string"}
            }
        }
    },
    {
        "name": "post_to_instagram",
        "description": "Publica en Instagram Business de Clarvix vía Meta Graph API.",
        "input_schema": {
            "type": "object",
            "required": ["caption", "image_url"],
            "properties": {
                "caption":    {"type": "string"},
                "image_url":  {"type": "string"},
                "content_id": {"type": "integer"}
            }
        }
    },
    {
        "name": "post_to_facebook",
        "description": "Publica en Facebook Page de Clarvix vía Meta Graph API.",
        "input_schema": {
            "type": "object",
            "required": ["message"],
            "properties": {
                "message":    {"type": "string"},
                "image_url":  {"type": "string"},
                "link":       {"type": "string"},
                "content_id": {"type": "integer"}
            }
        }
    },
    {
        "name": "get_leads",
        "description": "Lista leads del pipeline — para ajustar contenido a nichos con más tracción.",
        "input_schema": {
            "type": "object",
            "properties": {"status": {"type": "string"}, "limit": {"type": "integer"}}
        }
    }
]

# ─── MCP TOOL EXECUTOR ───────────────────────────────────────────────────────
def execute_mcp_tool(tool_name: str, tool_input: dict) -> str:
    """Llama al MCP server con JSON-RPC y retorna el resultado como string."""
    headers = {'Content-Type': 'application/json'}
    if MCP_API_KEY:
        headers['X-API-Key'] = MCP_API_KEY

    payload = {
        "jsonrpc": "2.0",
        "id":      1,
        "method":  "tools/call",
        "params":  {"name": tool_name, "arguments": tool_input}
    }

    try:
        res  = requests.post(MCP_URL, json=payload, headers=headers, timeout=30)
        data = res.json()
        if 'error' in data:
            return f"MCP error: {data['error']}"
        content = data.get('result', {}).get('content', [])
        if isinstance(content, list) and content:
            return content[0].get('text', json.dumps(data.get('result', {})))
        return json.dumps(data.get('result', {}))
    except Exception as e:
        return f"MCP call failed: {str(e)}"

# ─── ANTHROPIC TOOL LOOP ─────────────────────────────────────────────────────
def run_mira(mode: str, note: str = '') -> str:
    """Ejecuta MIRA en el modo indicado con tool calling loop completo."""
    today     = datetime.now().strftime('%Y-%m-%d %A')
    day_of_week = datetime.now().strftime('%A')

    trigger_msg = f"""Modo: {mode}
Fecha: {today}
Hora Israel: 09:00

{"Nota adicional: " + note if note else ""}

Ejecuta tu ciclo completo de {mode}. Carga tu contexto, genera el contenido apropiado para este {day_of_week}, publica y cierra con store_learning.
"""

    messages   = [{"role": "user", "content": trigger_msg}]
    iteration  = 0
    final_text = ""

    print(f"[MIRA] Iniciando modo {mode} — {today}")

    while iteration < MAX_ITERATIONS:
        iteration += 1
        print(f"[MIRA] Iteración {iteration}/{MAX_ITERATIONS}")

        res = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'Content-Type':      'application/json',
                'x-api-key':         ANTHROPIC_API_KEY,
                'anthropic-version': '2023-06-01'
            },
            json={
                'model':      MODEL,
                'max_tokens': 4096,
                'system':     MIRA_SYSTEM_PROMPT,
                'messages':   messages,
                'tools':      MIRA_TOOLS
            },
            timeout=120
        )

        if res.status_code != 200:
            print(f"[MIRA] ERROR Anthropic API: {res.status_code} — {res.text[:500]}")
            sys.exit(1)

        data        = res.json()
        stop_reason = data.get('stop_reason', '')
        content     = data.get('content', [])

        print(f"[MIRA] stop_reason={stop_reason}, bloques={len(content)}")

        if stop_reason == 'end_turn':
            for block in content:
                if block.get('type') == 'text':
                    final_text = block.get('text', '')
            print(f"[MIRA] ✅ Run completado:\n{final_text[:500]}")
            break

        if stop_reason == 'tool_use':
            messages.append({"role": "assistant", "content": content})
            tool_results = []

            for block in content:
                if block.get('type') == 'tool_use':
                    tool_name  = block['name']
                    tool_input = block.get('input', {})
                    print(f"[MIRA] → Tool: {tool_name}({list(tool_input.keys())})")
                    result = execute_mcp_tool(tool_name, tool_input)
                    print(f"[MIRA] ← {tool_name}: {result[:200]}")
                    tool_results.append({
                        "type":        "tool_result",
                        "tool_use_id": block['id'],
                        "content":     result
                    })

            messages.append({"role": "user", "content": tool_results})
        else:
            print(f"[MIRA] stop_reason inesperado: {stop_reason}")
            break

    if iteration >= MAX_ITERATIONS:
        print(f"[MIRA] ⚠️  Max iteraciones alcanzadas ({MAX_ITERATIONS})")

    return final_text


# ─── MAIN ────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    result = run_mira(MIRA_MODE, MIRA_NOTE)
    print(f"\n[MIRA] Run finalizado en modo {MIRA_MODE}")
    sys.exit(0)
