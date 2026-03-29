#!/usr/bin/env python3
"""
Clarvix AdTech AI Agent Service Brief — PDF Generator
Uses the EXACT same visual format as CLARVIX_TEMPLATE_MASTER.py
(white background, navy text, cyan accents, professional audit style)
Generates in EN, ES, HE, AR
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, KeepTogether, PageBreak)

# ════════════════════════════════════════════════════════════════
# COLORS — identical to CLARVIX_TEMPLATE_MASTER
# ════════════════════════════════════════════════════════════════
NAVY  = colors.HexColor("#0D1B2A")
CYAN  = colors.HexColor("#0ABFBF")
RED   = colors.HexColor("#C0392B")
AMBER = colors.HexColor("#B7770D")
GREEN = colors.HexColor("#1A7A4A")
LIGHT = colors.HexColor("#EEF2F6")
MID   = colors.HexColor("#D9E1EA")
STEEL = colors.HexColor("#8FA3B8")
SLATE = colors.HexColor("#4A6178")
WHITE = colors.white
RED_L = colors.HexColor("#FDECEA")
AMB_L = colors.HexColor("#FEF9EE")
GRN_L = colors.HexColor("#EAF7EF")
PURPLE = colors.HexColor("#7C3AED")
PURP_L = colors.HexColor("#F3E8FF")

W, H   = letter
MARGIN = 0.65 * inch
CW     = W - 2 * MARGIN

LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clarvix_logo_crop.png")

def mk(name, **kw):
    return ParagraphStyle(name, **kw)

# ════════════════════════════════════════════════════════════════
# STYLES — identical to audit template
# ════════════════════════════════════════════════════════════════
S = {
    "h1":       mk("h1",    fontName="Helvetica-Bold", fontSize=22, textColor=NAVY,  spaceAfter=8,  spaceBefore=18, leading=28),
    "h2":       mk("h2",    fontName="Helvetica-Bold", fontSize=14, textColor=NAVY,  spaceAfter=6,  spaceBefore=12, leading=20),
    "h3":       mk("h3",    fontName="Helvetica-Bold", fontSize=11, textColor=NAVY,  spaceAfter=4,  spaceBefore=8,  leading=16),
    "body":     mk("body",  fontName="Helvetica",      fontSize=10, textColor=NAVY,  leading=16,    spaceAfter=6, alignment=TA_JUSTIFY),
    "bodyC":    mk("bodyC", fontName="Helvetica",      fontSize=10, textColor=NAVY,  leading=16,    spaceAfter=6, alignment=TA_CENTER),
    "small":    mk("small", fontName="Helvetica",      fontSize=8.5,textColor=SLATE, leading=13,    spaceAfter=4),
    "smallC":   mk("smallC",fontName="Helvetica",      fontSize=8.5,textColor=SLATE, leading=13,    spaceAfter=4, alignment=TA_CENTER),
    "cyan":     mk("cyan",  fontName="Helvetica-Bold", fontSize=11, textColor=CYAN,  spaceAfter=4),
    "kpi_n":    mk("kpi_n", fontName="Helvetica-Bold", fontSize=26, textColor=WHITE, alignment=TA_CENTER, leading=30),
    "kpi_l":    mk("kpi_l", fontName="Helvetica",      fontSize=8,  textColor=MID,   alignment=TA_CENTER, leading=12),
    "bench_h":  mk("bh",    fontName="Helvetica-Bold", fontSize=8.5,textColor=WHITE, alignment=TA_CENTER),
    "bench_c":  mk("bc",    fontName="Helvetica",      fontSize=8.5,textColor=NAVY,  alignment=TA_CENTER, leading=13),
    "bench_m":  mk("bm",    fontName="Helvetica",      fontSize=8.5,textColor=NAVY,  leading=13),
    "next_n":   mk("nn",    fontName="Helvetica-Bold", fontSize=22, textColor=CYAN,  leading=26),
    "next_t":   mk("nt",    fontName="Helvetica-Bold", fontSize=12, textColor=NAVY,  leading=16),
    "next_b":   mk("nb",    fontName="Helvetica",      fontSize=10, textColor=NAVY,  leading=15),
    "tier_name":mk("tn",    fontName="Helvetica-Bold", fontSize=14, textColor=WHITE, alignment=TA_CENTER, leading=18),
    "tier_price":mk("tp",   fontName="Helvetica-Bold", fontSize=28, textColor=WHITE, alignment=TA_CENTER, leading=34),
    "tier_sub": mk("ts",    fontName="Helvetica",      fontSize=9,  textColor=MID,   alignment=TA_CENTER),
    "tier_item":mk("ti",    fontName="Helvetica",      fontSize=9,  textColor=NAVY,  leading=13, spaceAfter=3),
    "bullet":   mk("bul",   fontName="Helvetica",      fontSize=9.5,textColor=NAVY,  leading=14, leftIndent=14, spaceAfter=2),
}

def hr():
    return HRFlowable(width="100%", thickness=1.2, color=CYAN, spaceAfter=16, spaceBefore=0)

def sp(n=8):
    return Spacer(1, n)


# ════════════════════════════════════════════════════════════════
# TRANSLATIONS
# ════════════════════════════════════════════════════════════════
LANGS = {
  "en": {
    "doc_title": "AdTech AI Agent Systems",
    "doc_sub": "Autonomous Optimization for Programmatic Advertising",
    "badge": "ADTECH AI AGENT ARCHITECTURE",
    "prepared": "Prepared by Clarvix AI Architecture",
    "tagline": "Facts. Clarity. Action.",
    "email": "contact@clarvix.net",
    "web": "clarvix.net",
    "overview_title": "Service Overview",
    "overview_p1": "Clarvix deploys autonomous AI agents that continuously monitor, analyze, and optimize your programmatic advertising stack. Our multi-agent architecture operates 24/7, making real-time decisions on floor pricing, fraud detection, and inventory management — reducing manual AdOps workload by up to 80%.",
    "overview_p2": "Each agent follows the OBSERVE-THINK-ACT-REPORT cycle: it ingests live data from your SSPs and ad exchanges, analyzes patterns using machine learning, executes optimizations (or recommends them), and reports findings via Slack, email, or dashboard.",
    "agents_title": "The AI Agent Roster",
    "agent1_name": "Revenue Optimization Agent",
    "agent1_desc": "Dynamic floor pricing and yield curve optimization using gradient boosting. Adjusts bid floors per geo, device, and time-of-day. Runs every 15 minutes.",
    "agent2_name": "Anomaly Detection Agent",
    "agent2_desc": "Detects IVT (Invalid Traffic), revenue anomalies, traffic quality drops, and latency spikes using statistical models (z-score, IQR) and ML classifiers. Alerts via Slack.",
    "agent3_name": "Inventory Optimization Agent",
    "agent3_desc": "Maximizes fill rates through placement scoring, demand forecasting, and unfilled impression recovery. Identifies underperforming ad units and recommends reconfigurations.",
    "tiers_title": "Service Tiers",
    "tier1_name": "Discovery", "tier1_price": "$1,500", "tier1_sub": "One-time blueprint",
    "tier1_items": ["Full AdTech stack audit and gap analysis", "AI agent architecture blueprint customized to your stack", "Revenue opportunity mapping with projected ROI", "Competitive benchmarking against industry leaders", "30-day implementation roadmap", "Delivered as a professional HTML/PDF report"],
    "tier2_name": "Build & Test", "tier2_price": "$3,500", "tier2_sub": "Dry-run deployment",
    "tier2_items": ["Everything in Discovery, plus:", "3 AI agents deployed in dry-run mode", "Agents analyze your real data but only recommend (no auto-execution)", "2-week observation period with daily Slack reports", "Performance projections based on real data", "Go/no-go recommendation for production deployment"],
    "tier3_name": "Production", "tier3_price": "$7,500/mo", "tier3_sub": "Full autonomous operation",
    "tier3_items": ["Everything in Build & Test, plus:", "3 AI agents running live with auto-execution authority", "Real-time floor pricing adjustments", "24/7 anomaly monitoring with instant Slack alerts", "Weekly trend analysis and monthly performance reviews", "99.9% uptime SLA with dedicated support channel", "Dashboard access with full agent activity history"],
    "how_title": "How It Works",
    "how_steps": [
        ("You close a deal", "Client signs for Discovery, Build, or Production tier."),
        ("We audit the stack", "We analyze their SSPs, header bidding setup, ad server config, and data infrastructure."),
        ("Blueprint delivery", "Custom AI agent architecture document with specific recommendations for their stack."),
        ("Agent deployment", "For Build/Production: agents connect to their programmatic data feeds via MCP protocol."),
        ("Continuous optimization", "Production agents run autonomously, reporting via Slack and dashboard."),
    ],
    "results_title": "Expected Results",
    "results": [
        ("Revenue increase", "+12-25%", "Through dynamic floor pricing and yield optimization"),
        ("IVT reduction", "-40-60%", "Automated fraud detection catches what manual review misses"),
        ("Fill rate improvement", "+8-15%", "Demand forecasting and placement optimization"),
        ("AdOps time saved", "80%", "Agents handle monitoring, alerting, and routine optimizations"),
    ],
    "cta_title": "Ready to Deploy AI Agents?",
    "cta_text": "Contact us to schedule a discovery call and learn how autonomous AI agents can transform your programmatic advertising operation.",
    "footer_conf": "CONFIDENTIAL — FOR CLIENT USE ONLY",
  },
  "es": {
    "doc_title": "Sistemas de Agentes IA para AdTech",
    "doc_sub": "Optimizacion Autonoma para Publicidad Programatica",
    "badge": "ARQUITECTURA DE AGENTES IA ADTECH",
    "prepared": "Preparado por Clarvix AI Architecture",
    "tagline": "Datos. Claridad. Accion.",
    "email": "contact@clarvix.net", "web": "clarvix.net",
    "overview_title": "Vision General del Servicio",
    "overview_p1": "Clarvix despliega agentes de IA autonomos que monitorean, analizan y optimizan continuamente tu stack de publicidad programatica. Nuestra arquitectura multi-agente opera 24/7, tomando decisiones en tiempo real sobre precios minimos, deteccion de fraude y gestion de inventario, reduciendo la carga manual de AdOps hasta un 80%.",
    "overview_p2": "Cada agente sigue el ciclo OBSERVAR-PENSAR-ACTUAR-REPORTAR: ingiere datos en vivo de tus SSPs y ad exchanges, analiza patrones usando machine learning, ejecuta optimizaciones (o las recomienda), y reporta hallazgos via Slack, email o dashboard.",
    "agents_title": "Los Agentes de IA",
    "agent1_name": "Agente de Optimizacion de Revenue",
    "agent1_desc": "Precios minimos dinamicos y optimizacion de curvas de rendimiento usando gradient boosting. Ajusta bid floors por geo, dispositivo y hora del dia. Se ejecuta cada 15 minutos.",
    "agent2_name": "Agente de Deteccion de Anomalias",
    "agent2_desc": "Detecta IVT (Trafico Invalido), anomalias de revenue, caidas de calidad de trafico y picos de latencia usando modelos estadisticos (z-score, IQR) y clasificadores ML. Alerta via Slack.",
    "agent3_name": "Agente de Optimizacion de Inventario",
    "agent3_desc": "Maximiza fill rates mediante scoring de placements, pronostico de demanda y recuperacion de impresiones no servidas. Identifica ad units con bajo rendimiento.",
    "tiers_title": "Niveles de Servicio",
    "tier1_name": "Discovery", "tier1_price": "$1,500", "tier1_sub": "Blueprint unico",
    "tier1_items": ["Auditoria completa del stack AdTech", "Blueprint de arquitectura de agentes IA personalizado", "Mapeo de oportunidades de revenue con ROI proyectado", "Benchmarking competitivo contra lideres de la industria", "Hoja de ruta de implementacion a 30 dias", "Entregado como reporte profesional HTML/PDF"],
    "tier2_name": "Build & Test", "tier2_price": "$3,500", "tier2_sub": "Despliegue en modo prueba",
    "tier2_items": ["Todo lo de Discovery, mas:", "3 agentes IA desplegados en modo dry-run", "Los agentes analizan tus datos reales pero solo recomiendan", "Periodo de observacion de 2 semanas con reportes diarios", "Proyecciones de rendimiento basadas en datos reales", "Recomendacion go/no-go para produccion"],
    "tier3_name": "Production", "tier3_price": "$7,500/mes", "tier3_sub": "Operacion autonoma completa",
    "tier3_items": ["Todo lo de Build & Test, mas:", "3 agentes IA corriendo en vivo con ejecucion automatica", "Ajustes de precios minimos en tiempo real", "Monitoreo 24/7 con alertas instantaneas por Slack", "Analisis semanal y revisiones mensuales de rendimiento", "SLA de 99.9% uptime con canal de soporte dedicado", "Acceso al dashboard con historial completo"],
    "how_title": "Como Funciona",
    "how_steps": [
        ("Cierras un deal", "El cliente firma por Discovery, Build o Production."),
        ("Auditamos el stack", "Analizamos sus SSPs, header bidding, ad server y data infrastructure."),
        ("Entrega del blueprint", "Documento de arquitectura de agentes IA con recomendaciones especificas."),
        ("Despliegue de agentes", "Para Build/Production: los agentes se conectan via protocolo MCP."),
        ("Optimizacion continua", "Los agentes Production corren autonomamente, reportando via Slack y dashboard."),
    ],
    "results_title": "Resultados Esperados",
    "results": [
        ("Aumento de revenue", "+12-25%", "Mediante precios dinamicos y optimizacion de rendimiento"),
        ("Reduccion de IVT", "-40-60%", "Deteccion automatica de fraude que supera la revision manual"),
        ("Mejora de fill rate", "+8-15%", "Pronostico de demanda y optimizacion de placements"),
        ("Tiempo de AdOps ahorrado", "80%", "Los agentes manejan monitoreo, alertas y optimizaciones rutinarias"),
    ],
    "cta_title": "Listo para Desplegar Agentes IA?",
    "cta_text": "Contactanos para agendar una llamada de discovery y descubrir como los agentes autonomos de IA pueden transformar tu operacion de publicidad programatica.",
    "footer_conf": "CONFIDENCIAL — SOLO PARA USO DEL CLIENTE",
  },
  "he": {
    "doc_title": "AdTech AI Agent Systems",
    "doc_sub": "Autonomous Optimization for Programmatic Advertising",
    "badge": "ADTECH AI AGENT ARCHITECTURE",
    "prepared": "Clarvix AI Architecture",
    "tagline": "Facts. Clarity. Action.",
    "email": "contact@clarvix.net", "web": "clarvix.net",
    "overview_title": "Service Overview",
    "overview_p1": "Clarvix deploys autonomous AI agents that continuously monitor, analyze, and optimize your programmatic advertising stack. Our multi-agent architecture operates 24/7, making real-time decisions on floor pricing, fraud detection, and inventory management — reducing manual AdOps workload by up to 80%.",
    "overview_p2": "Each agent follows the OBSERVE-THINK-ACT-REPORT cycle: it ingests live data from your SSPs and ad exchanges, analyzes patterns using machine learning, executes optimizations (or recommends them), and reports findings via Slack, email, or dashboard.",
    "agents_title": "AI Agent Roster",
    "agent1_name": "Revenue Optimization Agent",
    "agent1_desc": "Dynamic floor pricing and yield optimization using gradient boosting. Adjusts bid floors per geo, device, and time-of-day. Runs every 15 minutes.",
    "agent2_name": "Anomaly Detection Agent",
    "agent2_desc": "Detects IVT, revenue anomalies, traffic quality drops, and latency spikes using statistical models and ML classifiers. Alerts via Slack.",
    "agent3_name": "Inventory Optimization Agent",
    "agent3_desc": "Maximizes fill rates through placement scoring, demand forecasting, and unfilled impression recovery.",
    "tiers_title": "Service Tiers",
    "tier1_name": "Discovery", "tier1_price": "$1,500", "tier1_sub": "One-time blueprint",
    "tier1_items": ["Full AdTech stack audit", "Custom AI agent architecture blueprint", "Revenue opportunity mapping with ROI projections", "Competitive benchmarking", "30-day implementation roadmap", "Professional HTML/PDF report"],
    "tier2_name": "Build & Test", "tier2_price": "$3,500", "tier2_sub": "Dry-run deployment",
    "tier2_items": ["Everything in Discovery, plus:", "3 AI agents in dry-run mode", "Agents analyze real data, recommend only", "2-week observation with daily Slack reports", "Performance projections from real data", "Go/no-go recommendation"],
    "tier3_name": "Production", "tier3_price": "$7,500/mo", "tier3_sub": "Full autonomous",
    "tier3_items": ["Everything in Build, plus:", "3 live agents with auto-execution", "Real-time floor pricing", "24/7 monitoring + Slack alerts", "Weekly trends + monthly reviews", "99.9% uptime SLA", "Full dashboard access"],
    "how_title": "How It Works",
    "how_steps": [("Close a deal","Client signs Discovery/Build/Production."),("Stack audit","We analyze SSPs, header bidding, ad server."),("Blueprint delivery","Custom agent architecture document."),("Agent deployment","Build/Production: agents connect via MCP."),("Continuous optimization","Production agents run autonomously.")],
    "results_title": "Expected Results",
    "results": [("Revenue increase","+12-25%","Dynamic floor pricing"),("IVT reduction","-40-60%","Automated fraud detection"),("Fill rate improvement","+8-15%","Demand forecasting"),("AdOps time saved","80%","Automated monitoring")],
    "cta_title": "Ready to Deploy AI Agents?",
    "cta_text": "Contact us to schedule a discovery call.",
    "footer_conf": "CONFIDENTIAL — FOR CLIENT USE ONLY",
  },
  "ar": {
    "doc_title": "AdTech AI Agent Systems",
    "doc_sub": "Autonomous Optimization for Programmatic Advertising",
    "badge": "ADTECH AI AGENT ARCHITECTURE",
    "prepared": "Clarvix AI Architecture",
    "tagline": "Facts. Clarity. Action.",
    "email": "contact@clarvix.net", "web": "clarvix.net",
    "overview_title": "Service Overview",
    "overview_p1": "Clarvix deploys autonomous AI agents that continuously monitor, analyze, and optimize your programmatic advertising stack. Our multi-agent architecture operates 24/7, making real-time decisions on floor pricing, fraud detection, and inventory management — reducing manual AdOps workload by up to 80%.",
    "overview_p2": "Each agent follows the OBSERVE-THINK-ACT-REPORT cycle: it ingests live data from your SSPs and ad exchanges, analyzes patterns using machine learning, executes optimizations, and reports via Slack or dashboard.",
    "agents_title": "AI Agent Roster",
    "agent1_name": "Revenue Optimization Agent",
    "agent1_desc": "Dynamic floor pricing using gradient boosting. Adjusts bid floors per geo, device, time-of-day. Runs every 15 minutes.",
    "agent2_name": "Anomaly Detection Agent",
    "agent2_desc": "Detects IVT, revenue anomalies, traffic quality drops using statistical models and ML. Alerts via Slack.",
    "agent3_name": "Inventory Optimization Agent",
    "agent3_desc": "Maximizes fill rates through placement scoring, demand forecasting, and impression recovery.",
    "tiers_title": "Service Tiers",
    "tier1_name": "Discovery", "tier1_price": "$1,500", "tier1_sub": "One-time blueprint",
    "tier1_items": ["Full AdTech stack audit", "Custom AI agent architecture", "Revenue opportunity mapping", "Competitive benchmarking", "30-day roadmap", "HTML/PDF report"],
    "tier2_name": "Build & Test", "tier2_price": "$3,500", "tier2_sub": "Dry-run deployment",
    "tier2_items": ["Everything in Discovery, plus:", "3 agents in dry-run", "Real data analysis, recommend only", "2-week observation", "Performance projections", "Go/no-go recommendation"],
    "tier3_name": "Production", "tier3_price": "$7,500/mo", "tier3_sub": "Full autonomous",
    "tier3_items": ["Everything in Build, plus:", "3 live agents", "Real-time pricing", "24/7 Slack alerts", "Weekly/monthly reviews", "99.9% SLA", "Full dashboard"],
    "how_title": "How It Works",
    "how_steps": [("Close deal","Client signs tier."),("Stack audit","Analyze SSPs, bidding, ad server."),("Blueprint","Custom architecture doc."),("Deploy agents","Connect via MCP."),("Optimize","Agents run autonomously.")],
    "results_title": "Expected Results",
    "results": [("Revenue","+12-25%","Floor pricing optimization"),("IVT","-40-60%","Fraud detection"),("Fill rate","+8-15%","Demand forecasting"),("Time saved","80%","Automated ops")],
    "cta_title": "Ready to Deploy?",
    "cta_text": "Contact us for a discovery call.",
    "footer_conf": "CONFIDENTIAL — FOR CLIENT USE ONLY",
  },
}


# ════════════════════════════════════════════════════════════════
# RENDERING — follows CLARVIX_TEMPLATE_MASTER exactly
# ════════════════════════════════════════════════════════════════

def draw_hf(c, doc, lang_data):
    """Header/footer on every page (except cover). Identical to audit template."""
    c.saveState()
    # Top cyan line
    c.setStrokeColor(CYAN); c.setLineWidth(1.5)
    c.line(MARGIN, H - 0.45*inch, W - MARGIN, H - 0.45*inch)
    c.setFont("Helvetica", 7.5); c.setFillColor(STEEL)
    c.drawString(MARGIN, H - 0.38*inch, f"CLARVIX — AdTech AI Agent Systems")
    c.drawRightString(W - MARGIN, H - 0.38*inch, lang_data["tagline"])
    # Bottom cyan line
    c.setStrokeColor(CYAN)
    c.line(MARGIN, 0.55*inch, W - MARGIN, 0.55*inch)
    # Logo attempt
    try:
        c.drawImage(LOGO_PATH, MARGIN, 0.19*inch, width=65, height=22,
                    preserveAspectRatio=True, mask='auto')
    except: pass
    c.setFont("Helvetica", 7.5); c.setFillColor(STEEL)
    c.drawCentredString(W/2, 0.23*inch, lang_data["footer_conf"])
    c.drawRightString(W - MARGIN, 0.23*inch, f"p. {doc.page}")
    c.restoreState()

def draw_cover(c, doc, lang_data):
    """Cover page — navy background, identical to audit template cover."""
    c.saveState()
    c.setFillColor(NAVY); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(CYAN)
    c.rect(0, H - 6, W, 6, fill=1, stroke=0)
    c.rect(0, 0, W, 4, fill=1, stroke=0)
    # Logo
    try:
        c.drawImage(LOGO_PATH, W/2-110, H-2.0*inch, width=220, height=74,
                    preserveAspectRatio=True, mask='auto')
    except:
        c.setFillColor(CYAN); c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(W/2, H - 1.8*inch, "CLARVIX")
    # Badge
    c.setFillColor(CYAN); c.rect(W/2-155, H-2.68*inch, 310, 20, fill=1, stroke=0)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(W/2, H-2.68*inch+5, lang_data["badge"])
    # Title
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(W/2, H - 3.3*inch, lang_data["doc_title"])
    c.setFillColor(CYAN); c.setFont("Helvetica", 11)
    c.drawCentredString(W/2, H - 3.7*inch, lang_data["doc_sub"])
    # Info box — like the score box in audit but for service info
    bw, bh = 260, 80
    c.setFillColor(CYAN)
    c.roundRect(W/2 - bw/2, H - 5.0*inch, bw, bh, 8, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W/2, H - 4.5*inch, "3 AI AGENTS")
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(W/2, H - 4.72*inch, "AUTONOMOUS OPTIMIZATION")
    c.setFont("Helvetica", 9)
    c.drawCentredString(W/2, H - 4.92*inch, "Revenue  |  Anomaly  |  Inventory")
    # Meta
    c.setFillColor(STEEL); c.setFont("Helvetica", 9)
    c.drawCentredString(W/2, H - 5.4*inch, lang_data["prepared"])
    c.setFillColor(CYAN); c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(W/2, H - 5.7*inch, lang_data["tagline"])
    c.setFillColor(STEEL); c.setFont("Helvetica", 8.5)
    c.drawCentredString(W/2, H - 5.9*inch, lang_data["email"])
    c.restoreState()


def kpi_row(items):
    """KPI row — identical to audit template."""
    col_w = CW / len(items)
    cells = []
    for val, label, bg in items:
        inner = Table([
            [Paragraph(str(val), S["kpi_n"])],
            [Paragraph(label, S["kpi_l"])]
        ], colWidths=[col_w - 8])
        inner.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), bg),
            ("TOPPADDING",    (0,0),(-1,-1), 10),
            ("BOTTOMPADDING", (0,0),(-1,-1), 10),
            ("LEFTPADDING",   (0,0),(-1,-1), 4),
            ("RIGHTPADDING",  (0,0),(-1,-1), 4),
        ]))
        cells.append(inner)
    row = Table([cells], colWidths=[col_w]*len(items))
    row.setStyle(TableStyle([
        ("TOPPADDING",    (0,0),(-1,-1), 0),
        ("BOTTOMPADDING", (0,0),(-1,-1), 0),
        ("LEFTPADDING",   (0,0),(-1,-1), 4),
        ("RIGHTPADDING",  (0,0),(-1,-1), 4),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]))
    return row


def agent_card(num, name, desc):
    """Agent card — uses finding_card style from audit template."""
    header = Table([[
        Paragraph(f"<b>{num}</b>", mk("an_num", fontName="Helvetica-Bold", fontSize=13, textColor=CYAN)),
        Paragraph(f"<b>{name}</b>", mk("an_name", fontName="Helvetica-Bold", fontSize=12, textColor=WHITE)),
    ]], colWidths=[44, CW - 44])
    header.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), NAVY),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("LEFTPADDING",   (0,0),(0,0),   14),
        ("LEFTPADDING",   (1,0),(1,0),   6),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]))
    body = Table([[Paragraph(desc, S["body"])]], colWidths=[CW])
    body.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), LIGHT),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("LEFTPADDING",   (0,0),(-1,-1), 14),
        ("RIGHTPADDING",  (0,0),(-1,-1), 14),
    ]))
    wrapper = Table([[header],[body]], colWidths=[CW])
    wrapper.setStyle(TableStyle([
        ("TOPPADDING",    (0,0),(-1,-1), 0),
        ("BOTTOMPADDING", (0,0),(-1,-1), 0),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
        ("LINEBELOW",     (0,-1),(-1,-1), 2, CYAN),
    ]))
    return KeepTogether([wrapper, sp(10)])


def tier_table(L):
    """3-column pricing table — audit template style (navy headers, alternating rows)."""
    # Header row
    headers = []
    for key in ["tier1", "tier2", "tier3"]:
        headers.append(Paragraph(
            f"<b>{L[key+'_name']}</b><br/><font size='18'><b>{L[key+'_price']}</b></font><br/>"
            f"<font size='8' color='#D9E1EA'>{L[key+'_sub']}</font>",
            mk(f"th_{key}", fontName="Helvetica-Bold", fontSize=11, textColor=WHITE,
               alignment=TA_CENTER, leading=24)
        ))

    # Find max items
    max_items = max(len(L["tier1_items"]), len(L["tier2_items"]), len(L["tier3_items"]))

    rows = [headers]
    for i in range(max_items):
        row = []
        for key in ["tier1", "tier2", "tier3"]:
            items = L[key+"_items"]
            if i < len(items):
                row.append(Paragraph(f"<b>+</b>  {items[i]}", S["tier_item"]))
            else:
                row.append(Paragraph("", S["tier_item"]))
        rows.append(row)

    col_w = CW / 3
    tbl = Table(rows, colWidths=[col_w]*3, repeatRows=1)

    # Color the header cells differently per tier
    tbl.setStyle(TableStyle([
        ("BACKGROUND",     (0,0), (0,0),  SLATE),     # Discovery — grey
        ("BACKGROUND",     (1,0), (1,0),  CYAN),      # Build — cyan
        ("BACKGROUND",     (2,0), (2,0),  PURPLE),    # Production — purple
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LIGHT]),
        ("GRID",           (0,0), (-1,-1), 0.4, MID),
        ("TOPPADDING",     (0,0), (-1,0),  14),
        ("BOTTOMPADDING",  (0,0), (-1,0),  14),
        ("TOPPADDING",     (0,1), (-1,-1), 6),
        ("BOTTOMPADDING",  (0,1), (-1,-1), 6),
        ("LEFTPADDING",    (0,0), (-1,-1), 10),
        ("RIGHTPADDING",   (0,0), (-1,-1), 10),
        ("VALIGN",         (0,0), (-1,-1), "TOP"),
    ]))
    return tbl


def step_card(num, title, body):
    """How-it-works step — uses next_card style from audit template."""
    row = Table([[
        Paragraph(f"<b>{num:02d}</b>", S["next_n"]),
        Table([
            [Paragraph(f"<b>{title}</b>", S["next_t"])],
            [Paragraph(body, S["next_b"])],
        ], colWidths=[CW - 60])
    ]], colWidths=[50, CW - 50])
    row.setStyle(TableStyle([
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("RIGHTPADDING",  (0,0),(-1,-1), 8),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ("LINEBELOW",     (0,0),(-1,-1), 0.5, MID),
        ("BACKGROUND",    (0,0),(-1,-1), LIGHT),
    ]))
    return KeepTogether([row, sp(8)])


def results_table(L):
    """Results table — audit template style."""
    headers = [
        Paragraph("<b>Metric</b>", S["bench_h"]),
        Paragraph("<b>Impact</b>", S["bench_h"]),
        Paragraph("<b>Details</b>", S["bench_h"]),
    ]
    rows = [headers]
    for metric, value, detail in L["results"]:
        rows.append([
            Paragraph(metric, S["bench_m"]),
            Paragraph(f"<b><font color='#1A7A4A'>{value}</font></b>",
                      mk("rv", fontName="Helvetica-Bold", fontSize=10, textColor=GREEN,
                         alignment=TA_CENTER, leading=14)),
            Paragraph(detail, S["bench_m"]),
        ])
    cw = [CW*0.30, CW*0.18, CW*0.52]
    tbl = Table(rows, colWidths=cw, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",     (0,0), (-1,0),  NAVY),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LIGHT]),
        ("GRID",           (0,0), (-1,-1), 0.4, MID),
        ("TOPPADDING",     (0,0), (-1,-1), 7),
        ("BOTTOMPADDING",  (0,0), (-1,-1), 7),
        ("LEFTPADDING",    (0,0), (-1,-1), 8),
        ("RIGHTPADDING",   (0,0), (-1,-1), 8),
        ("VALIGN",         (0,0), (-1,-1), "MIDDLE"),
    ]))
    return tbl


# ════════════════════════════════════════════════════════════════
# PDF GENERATION
# ════════════════════════════════════════════════════════════════

def generate_pdf(lang_code, output_dir):
    L = LANGS[lang_code]
    filename = f"clarvix-adtech-ai-agents-{lang_code}.pdf"
    filepath = os.path.join(output_dir, filename)

    doc = SimpleDocTemplate(filepath, pagesize=letter,
                            leftMargin=MARGIN, rightMargin=MARGIN,
                            topMargin=0.75*inch, bottomMargin=0.7*inch)

    # Closures for page drawing
    def on_cover(c, d): draw_cover(c, d, L)
    def on_later(c, d): draw_hf(c, d, L)

    story = [PageBreak()]  # cover on page 1 via onFirstPage

    # ── PAGE 2: Service Overview ──────────────────────────────────
    story += [
        Paragraph(L["overview_title"], S["h1"]), hr(),
        Paragraph(L["overview_p1"], S["body"]),
        sp(6),
        Paragraph(L["overview_p2"], S["body"]),
        sp(14),
        kpi_row([
            ("24/7",  "Autonomous Operation", NAVY),
            ("3",     "AI Agents",            CYAN),
            ("15min", "Optimization Cycle",   GREEN),
            ("<80%",  "AdOps Workload Cut",   RED),
        ]),
        sp(14),
        Paragraph("Built for: SSPs, DSPs, Publisher Networks, Ad Networks, Yield Management Teams.",
                  S["small"]),
        PageBreak(),
    ]

    # ── PAGE 3: AI Agent Roster ──────────────────────────────────
    story += [
        Paragraph(L["agents_title"], S["h1"]), hr(),
        Paragraph("Each agent operates in the OBSERVE-THINK-ACT-REPORT cycle. "
                  "All three can run independently or as a coordinated team.",
                  S["small"]),
        sp(10),
        agent_card("01", L["agent1_name"], L["agent1_desc"]),
        agent_card("02", L["agent2_name"], L["agent2_desc"]),
        agent_card("03", L["agent3_name"], L["agent3_desc"]),
        PageBreak(),
    ]

    # ── PAGE 4: Service Tiers ────────────────────────────────────
    story += [
        Paragraph(L["tiers_title"], S["h1"]), hr(),
        Paragraph("Three tiers designed for different stages of AI adoption. "
                  "Start with a Discovery blueprint, validate with Build, scale with Production.",
                  S["small"]),
        sp(10),
        tier_table(L),
        sp(14),
    ]
    # Highlight box
    highlight = Table([[Paragraph(
        "All tiers include a <b>free 30-minute discovery call</b> before engagement. "
        "No commitment required — we diagnose before we prescribe.", S["body"])
    ]], colWidths=[CW])
    highlight.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), GRN_L),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("LEFTPADDING",   (0,0),(-1,-1), 14),
        ("RIGHTPADDING",  (0,0),(-1,-1), 14),
        ("LINEBELOW",     (0,0),(-1,-1), 2, GREEN),
    ]))
    story += [highlight, PageBreak()]

    # ── PAGE 5: How It Works + Results ───────────────────────────
    story += [
        Paragraph(L["how_title"], S["h1"]), hr(),
        Paragraph("From initial contact to autonomous operation in five steps.",
                  S["small"]),
        sp(10),
    ]
    for i, (step_title, step_desc) in enumerate(L["how_steps"], 1):
        story.append(step_card(i, step_title, step_desc))

    story += [sp(10), PageBreak()]

    # ── PAGE 6: Expected Results + CTA ───────────────────────────
    story += [
        Paragraph(L["results_title"], S["h1"]), hr(),
        Paragraph("Based on industry benchmarks for programmatic advertising optimization.",
                  S["small"]),
        sp(10),
        results_table(L),
        sp(20),
    ]

    # CTA — closing box identical to audit template
    close_rows = [
        [Paragraph(f"<b>{L['cta_title']}</b>", S["h2"])],
        [Paragraph(L["cta_text"], S["body"])],
        [Paragraph(f"<b>{L['email']}</b>", S["body"])],
        [Paragraph(L["tagline"], S["cyan"])],
    ]
    close_box = Table(close_rows, colWidths=[CW])
    close_box.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), LIGHT),
        ("TOPPADDING",    (0,0),(-1,-1), 14),
        ("BOTTOMPADDING", (0,0),(-1,-1), 14),
        ("LEFTPADDING",   (0,0),(-1,-1), 20),
        ("RIGHTPADDING",  (0,0),(-1,-1), 20),
        ("LINEBELOW",     (0,-1),(-1,-1), 3, CYAN),
    ]))
    story.append(close_box)

    doc.build(story, onFirstPage=on_cover, onLaterPages=on_later)
    print(f"  [OK] {filename}")
    return filepath


# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    print("Generating Clarvix AdTech AI Agent Service Briefs...")
    print(f"Output: {out_dir}\n")
    generated = []
    for lang in ["en", "es", "he", "ar"]:
        path = generate_pdf(lang, out_dir)
        generated.append(path)
    print(f"\nDone! Generated {len(generated)} PDFs.")
