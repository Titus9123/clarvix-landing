#!/usr/bin/env python3
"""
Clarvix AdTech AI Agent Service Brief — PDF Generator
Generates professional service documents in EN, ES, HE, AR
Following Clarvix template style (navy/cyan cards)
"""
import os, sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, PageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

W, H = letter
MARGIN = 0.6 * inch
CW = W - 2 * MARGIN

# Colors (Clarvix brand)
NAVY   = colors.HexColor("#0B1120")
NAVY2  = colors.HexColor("#111827")
DARK   = colors.HexColor("#1A1D27")
CYAN   = colors.HexColor("#6366F1")
CYAN_L = colors.HexColor("#818CF8")
WHITE  = colors.HexColor("#FFFFFF")
LIGHT  = colors.HexColor("#F0F4F8")
MID    = colors.HexColor("#2A2D3A")
STEEL  = colors.HexColor("#94A3B8")
GREEN  = colors.HexColor("#10B981")
GREEN_L= colors.HexColor("#D1FAE5")
AMBER  = colors.HexColor("#F59E0B")
AMBER_L= colors.HexColor("#FEF3C7")
RED    = colors.HexColor("#EF4444")
PURPLE = colors.HexColor("#8B5CF6")
ORANGE = colors.HexColor("#F97316")

def mk(name, **kw):
    return ParagraphStyle(name, **kw)

# Styles
S = {
    "title":    mk("title", fontName="Helvetica-Bold", fontSize=24, textColor=WHITE, alignment=TA_CENTER, leading=30),
    "subtitle": mk("subtitle", fontName="Helvetica", fontSize=12, textColor=CYAN_L, alignment=TA_CENTER, leading=16),
    "h1":       mk("h1", fontName="Helvetica-Bold", fontSize=18, textColor=CYAN, leading=24, spaceBefore=16, spaceAfter=8),
    "h2":       mk("h2", fontName="Helvetica-Bold", fontSize=14, textColor=WHITE, leading=18, spaceBefore=12, spaceAfter=6),
    "h3":       mk("h3", fontName="Helvetica-Bold", fontSize=11, textColor=CYAN_L, leading=14, spaceBefore=8, spaceAfter=4),
    "body":     mk("body", fontName="Helvetica", fontSize=10, textColor=colors.HexColor("#CBD5E1"), leading=14, spaceAfter=6),
    "body_w":   mk("body_w", fontName="Helvetica", fontSize=10, textColor=WHITE, leading=14, spaceAfter=6),
    "body_dk":  mk("body_dk", fontName="Helvetica", fontSize=10, textColor=NAVY, leading=14, spaceAfter=4),
    "small":    mk("small", fontName="Helvetica", fontSize=8, textColor=STEEL, leading=10),
    "price":    mk("price", fontName="Helvetica-Bold", fontSize=28, textColor=WHITE, alignment=TA_CENTER, leading=34),
    "tier":     mk("tier", fontName="Helvetica-Bold", fontSize=14, textColor=WHITE, alignment=TA_CENTER, leading=18),
    "bullet":   mk("bullet", fontName="Helvetica", fontSize=9.5, textColor=colors.HexColor("#CBD5E1"), leading=13, leftIndent=12, spaceAfter=3),
    "kpi_n":    mk("kpi_n", fontName="Helvetica-Bold", fontSize=14, textColor=WHITE, alignment=TA_CENTER),
    "kpi_l":    mk("kpi_l", fontName="Helvetica", fontSize=7.5, textColor=STEEL, alignment=TA_CENTER),
}

sp = lambda h: Spacer(1, h)

# ══════════════════════════════════════════════════════════════
# TRANSLATIONS
# ══════════════════════════════════════════════════════════════
LANGS = {
  "en": {
    "doc_title": "AdTech AI Agent Systems",
    "doc_sub": "Autonomous Optimization for Programmatic Advertising",
    "prepared": "Prepared by Clarvix AI Architecture",
    "tagline": "Facts. Clarity. Action.",
    "email": "contact@clarvix.net",
    "web": "clarvix.net",
    "overview_title": "1. Service Overview",
    "overview_p1": "Clarvix deploys autonomous AI agents that continuously monitor, analyze, and optimize your programmatic advertising stack. Our multi-agent architecture operates 24/7, making real-time decisions on floor pricing, fraud detection, and inventory management — reducing manual AdOps workload by up to 80%.",
    "overview_p2": "Each agent follows the OBSERVE-THINK-ACT-REPORT cycle: it ingests live data from your SSPs and ad exchanges, analyzes patterns using machine learning, executes optimizations (or recommends them), and reports findings via Slack, email, or dashboard.",
    "agents_title": "2. The AI Agent Roster",
    "agent1_name": "Revenue Optimization Agent",
    "agent1_desc": "Dynamic floor pricing and yield curve optimization using gradient boosting. Adjusts bid floors per geo, device, and time-of-day. Runs every 15 minutes.",
    "agent2_name": "Anomaly Detection Agent",
    "agent2_desc": "Detects IVT (Invalid Traffic), revenue anomalies, traffic quality drops, and latency spikes using statistical models (z-score, IQR) and ML classifiers. Alerts via Slack.",
    "agent3_name": "Inventory Optimization Agent",
    "agent3_desc": "Maximizes fill rates through placement scoring, demand forecasting, and unfilled impression recovery. Identifies underperforming ad units and recommends reconfigurations.",
    "tiers_title": "3. Service Tiers",
    "tier1_name": "Discovery", "tier1_price": "$1,500", "tier1_sub": "One-time blueprint",
    "tier1_items": ["Full AdTech stack audit and gap analysis", "AI agent architecture blueprint customized to your stack", "Revenue opportunity mapping with projected ROI", "Competitive benchmarking against industry leaders", "30-day implementation roadmap", "Delivered as a professional HTML/PDF report"],
    "tier2_name": "Build & Test", "tier2_price": "$3,500", "tier2_sub": "Dry-run deployment",
    "tier2_items": ["Everything in Discovery, plus:", "3 AI agents deployed in dry-run mode", "Agents analyze your real data but only recommend (no auto-execution)", "2-week observation period with daily Slack reports", "Performance projections based on real data", "Go/no-go recommendation for production deployment"],
    "tier3_name": "Production", "tier3_price": "$7,500/mo", "tier3_sub": "Full autonomous operation",
    "tier3_items": ["Everything in Build & Test, plus:", "3 AI agents running live with auto-execution authority", "Real-time floor pricing adjustments", "24/7 anomaly monitoring with instant Slack alerts", "Weekly trend analysis and monthly performance reviews", "99.9% uptime SLA with dedicated support channel", "Dashboard access with full agent activity history"],
    "how_title": "4. How It Works",
    "how_steps": [
        ("You close a deal", "Client signs for Discovery, Build, or Production tier."),
        ("We audit the stack", "We analyze their SSPs, header bidding setup, ad server config, and data infrastructure."),
        ("Blueprint delivery", "Custom AI agent architecture document with specific recommendations for their stack."),
        ("Agent deployment", "For Build/Production: agents connect to their programmatic data feeds via MCP protocol."),
        ("Continuous optimization", "Production agents run autonomously, reporting via Slack and dashboard."),
    ],
    "results_title": "5. Expected Results",
    "results": [
        ("Revenue increase", "+12-25%", "Through dynamic floor pricing and yield optimization"),
        ("IVT reduction", "-40-60%", "Automated fraud detection catches what manual review misses"),
        ("Fill rate improvement", "+8-15%", "Demand forecasting and placement optimization"),
        ("AdOps time saved", "80%", "Agents handle monitoring, alerting, and routine optimizations"),
    ],
    "cta_title": "Ready to Deploy AI Agents?",
    "cta_text": "Contact us to schedule a discovery call and learn how autonomous AI agents can transform your programmatic advertising operation.",
    "footer_conf": "CONFIDENTIAL",
  },
  "es": {
    "doc_title": "Sistemas de Agentes IA para AdTech",
    "doc_sub": "Optimizacion Autonoma para Publicidad Programatica",
    "prepared": "Preparado por Clarvix AI Architecture",
    "tagline": "Datos. Claridad. Accion.",
    "email": "contact@clarvix.net", "web": "clarvix.net",
    "overview_title": "1. Vision General del Servicio",
    "overview_p1": "Clarvix despliega agentes de IA autonomos que monitorean, analizan y optimizan continuamente tu stack de publicidad programatica. Nuestra arquitectura multi-agente opera 24/7, tomando decisiones en tiempo real sobre precios minimos, deteccion de fraude y gestion de inventario, reduciendo la carga manual de AdOps hasta un 80%.",
    "overview_p2": "Cada agente sigue el ciclo OBSERVAR-PENSAR-ACTUAR-REPORTAR: ingiere datos en vivo de tus SSPs y ad exchanges, analiza patrones usando machine learning, ejecuta optimizaciones (o las recomienda), y reporta hallazgos via Slack, email o dashboard.",
    "agents_title": "2. Los Agentes de IA",
    "agent1_name": "Agente de Optimizacion de Revenue",
    "agent1_desc": "Precios minimos dinamicos y optimizacion de curvas de rendimiento usando gradient boosting. Ajusta bid floors por geo, dispositivo y hora del dia. Se ejecuta cada 15 minutos.",
    "agent2_name": "Agente de Deteccion de Anomalias",
    "agent2_desc": "Detecta IVT (Trafico Invalido), anomalias de revenue, caidas de calidad de trafico y picos de latencia usando modelos estadisticos (z-score, IQR) y clasificadores ML. Alerta via Slack.",
    "agent3_name": "Agente de Optimizacion de Inventario",
    "agent3_desc": "Maximiza fill rates mediante scoring de placements, pronostico de demanda y recuperacion de impresiones no servidas. Identifica ad units con bajo rendimiento.",
    "tiers_title": "3. Niveles de Servicio",
    "tier1_name": "Discovery", "tier1_price": "$1,500", "tier1_sub": "Blueprint unico",
    "tier1_items": ["Auditoria completa del stack AdTech", "Blueprint de arquitectura de agentes IA personalizado", "Mapeo de oportunidades de revenue con ROI proyectado", "Benchmarking competitivo contra lideres de la industria", "Hoja de ruta de implementacion a 30 dias", "Entregado como reporte profesional HTML/PDF"],
    "tier2_name": "Build & Test", "tier2_price": "$3,500", "tier2_sub": "Despliegue en modo prueba",
    "tier2_items": ["Todo lo de Discovery, mas:", "3 agentes IA desplegados en modo dry-run", "Los agentes analizan tus datos reales pero solo recomiendan", "Periodo de observacion de 2 semanas con reportes diarios", "Proyecciones de rendimiento basadas en datos reales", "Recomendacion go/no-go para produccion"],
    "tier3_name": "Production", "tier3_price": "$7,500/mes", "tier3_sub": "Operacion autonoma completa",
    "tier3_items": ["Todo lo de Build & Test, mas:", "3 agentes IA corriendo en vivo con ejecucion automatica", "Ajustes de precios minimos en tiempo real", "Monitoreo 24/7 con alertas instantaneas por Slack", "Analisis semanal y revisiones mensuales de rendimiento", "SLA de 99.9% uptime con canal de soporte dedicado", "Acceso al dashboard con historial completo"],
    "how_title": "4. Como Funciona",
    "how_steps": [
        ("Cierras un deal", "El cliente firma por Discovery, Build o Production."),
        ("Auditamos el stack", "Analizamos sus SSPs, header bidding, ad server y data infrastructure."),
        ("Entrega del blueprint", "Documento de arquitectura de agentes IA con recomendaciones especificas."),
        ("Despliegue de agentes", "Para Build/Production: los agentes se conectan via protocolo MCP."),
        ("Optimizacion continua", "Los agentes Production corren autonomamente, reportando via Slack y dashboard."),
    ],
    "results_title": "5. Resultados Esperados",
    "results": [
        ("Aumento de revenue", "+12-25%", "Mediante precios dinamicos y optimizacion de rendimiento"),
        ("Reduccion de IVT", "-40-60%", "Deteccion automatica de fraude que supera la revision manual"),
        ("Mejora de fill rate", "+8-15%", "Pronostico de demanda y optimizacion de placements"),
        ("Tiempo de AdOps ahorrado", "80%", "Los agentes manejan monitoreo, alertas y optimizaciones rutinarias"),
    ],
    "cta_title": "Listo para Desplegar Agentes IA?",
    "cta_text": "Contactanos para agendar una llamada de discovery y descubrir como los agentes autonomos de IA pueden transformar tu operacion de publicidad programatica.",
    "footer_conf": "CONFIDENCIAL",
  },
  "he": {
    "doc_title": "AdTech AI Agent Systems",
    "doc_sub": "Autonomous Optimization for Programmatic Advertising",
    "prepared": "Clarvix AI Architecture",
    "tagline": "Facts. Clarity. Action.",
    "email": "contact@clarvix.net", "web": "clarvix.net",
    "overview_title": "1. Overview",
    "overview_p1": "Clarvix deploys autonomous AI agents that continuously monitor, analyze, and optimize your programmatic advertising stack. Our multi-agent architecture operates 24/7, making real-time decisions on floor pricing, fraud detection, and inventory management — reducing manual AdOps workload by up to 80%.",
    "overview_p2": "Each agent follows the OBSERVE-THINK-ACT-REPORT cycle: it ingests live data from your SSPs and ad exchanges, analyzes patterns using machine learning, executes optimizations (or recommends them), and reports findings via Slack, email, or dashboard.",
    "agents_title": "2. AI Agent Roster",
    "agent1_name": "Revenue Optimization Agent",
    "agent1_desc": "Dynamic floor pricing and yield optimization using gradient boosting. Adjusts bid floors per geo, device, and time-of-day. Runs every 15 minutes.",
    "agent2_name": "Anomaly Detection Agent",
    "agent2_desc": "Detects IVT, revenue anomalies, traffic quality drops, and latency spikes using statistical models and ML classifiers. Alerts via Slack.",
    "agent3_name": "Inventory Optimization Agent",
    "agent3_desc": "Maximizes fill rates through placement scoring, demand forecasting, and unfilled impression recovery.",
    "tiers_title": "3. Service Tiers",
    "tier1_name": "Discovery", "tier1_price": "$1,500", "tier1_sub": "One-time blueprint",
    "tier1_items": ["Full AdTech stack audit", "Custom AI agent architecture blueprint", "Revenue opportunity mapping with ROI projections", "Competitive benchmarking", "30-day implementation roadmap", "Professional HTML/PDF report"],
    "tier2_name": "Build & Test", "tier2_price": "$3,500", "tier2_sub": "Dry-run deployment",
    "tier2_items": ["Everything in Discovery, plus:", "3 AI agents in dry-run mode", "Agents analyze real data, recommend only", "2-week observation with daily Slack reports", "Performance projections from real data", "Go/no-go recommendation"],
    "tier3_name": "Production", "tier3_price": "$7,500/mo", "tier3_sub": "Full autonomous",
    "tier3_items": ["Everything in Build, plus:", "3 live agents with auto-execution", "Real-time floor pricing", "24/7 monitoring + Slack alerts", "Weekly trends + monthly reviews", "99.9% uptime SLA", "Full dashboard access"],
    "how_title": "4. How It Works",
    "how_steps": [("Close a deal","Client signs Discovery/Build/Production."),("Stack audit","We analyze SSPs, header bidding, ad server."),("Blueprint delivery","Custom agent architecture document."),("Agent deployment","Build/Production: agents connect via MCP."),("Continuous optimization","Production agents run autonomously.")],
    "results_title": "5. Expected Results",
    "results": [("Revenue increase","+12-25%","Dynamic floor pricing"),("IVT reduction","-40-60%","Automated fraud detection"),("Fill rate improvement","+8-15%","Demand forecasting"),("AdOps time saved","80%","Automated monitoring")],
    "cta_title": "Ready to Deploy AI Agents?",
    "cta_text": "Contact us to schedule a discovery call.",
    "footer_conf": "CONFIDENTIAL",
  },
  "ar": {
    "doc_title": "AdTech AI Agent Systems",
    "doc_sub": "Autonomous Optimization for Programmatic Advertising",
    "prepared": "Clarvix AI Architecture",
    "tagline": "Facts. Clarity. Action.",
    "email": "contact@clarvix.net", "web": "clarvix.net",
    "overview_title": "1. Service Overview",
    "overview_p1": "Clarvix deploys autonomous AI agents that continuously monitor, analyze, and optimize your programmatic advertising stack. Our multi-agent architecture operates 24/7, making real-time decisions on floor pricing, fraud detection, and inventory management — reducing manual AdOps workload by up to 80%.",
    "overview_p2": "Each agent follows the OBSERVE-THINK-ACT-REPORT cycle: it ingests live data from your SSPs and ad exchanges, analyzes patterns using machine learning, executes optimizations, and reports via Slack or dashboard.",
    "agents_title": "2. AI Agent Roster",
    "agent1_name": "Revenue Optimization Agent",
    "agent1_desc": "Dynamic floor pricing using gradient boosting. Adjusts bid floors per geo, device, time-of-day. Runs every 15 minutes.",
    "agent2_name": "Anomaly Detection Agent",
    "agent2_desc": "Detects IVT, revenue anomalies, traffic quality drops using statistical models and ML. Alerts via Slack.",
    "agent3_name": "Inventory Optimization Agent",
    "agent3_desc": "Maximizes fill rates through placement scoring, demand forecasting, and impression recovery.",
    "tiers_title": "3. Service Tiers",
    "tier1_name": "Discovery", "tier1_price": "$1,500", "tier1_sub": "One-time blueprint",
    "tier1_items": ["Full AdTech stack audit", "Custom AI agent architecture", "Revenue opportunity mapping", "Competitive benchmarking", "30-day roadmap", "HTML/PDF report"],
    "tier2_name": "Build & Test", "tier2_price": "$3,500", "tier2_sub": "Dry-run deployment",
    "tier2_items": ["Everything in Discovery, plus:", "3 agents in dry-run", "Real data analysis, recommend only", "2-week observation", "Performance projections", "Go/no-go recommendation"],
    "tier3_name": "Production", "tier3_price": "$7,500/mo", "tier3_sub": "Full autonomous",
    "tier3_items": ["Everything in Build, plus:", "3 live agents", "Real-time pricing", "24/7 Slack alerts", "Weekly/monthly reviews", "99.9% SLA", "Full dashboard"],
    "how_title": "4. How It Works",
    "how_steps": [("Close deal","Client signs tier."),("Stack audit","Analyze SSPs, bidding, ad server."),("Blueprint","Custom architecture doc."),("Deploy agents","Connect via MCP."),("Optimize","Agents run autonomously.")],
    "results_title": "5. Expected Results",
    "results": [("Revenue","+12-25%","Floor pricing optimization"),("IVT","-40-60%","Fraud detection"),("Fill rate","+8-15%","Demand forecasting"),("Time saved","80%","Automated ops")],
    "cta_title": "Ready to Deploy?",
    "cta_text": "Contact us for a discovery call.",
    "footer_conf": "CONFIDENTIAL",
  },
}

# ══════════════════════════════════════════════════════════════
# PDF GENERATION
# ══════════════════════════════════════════════════════════════

def draw_bg(canvas, doc):
    """Dark background + header/footer for every page."""
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    # Top accent bar
    canvas.setFillColor(CYAN)
    canvas.rect(0, H - 4, W, 4, fill=1, stroke=0)
    # Bottom accent bar
    canvas.rect(0, 0, W, 3, fill=1, stroke=0)
    # Footer
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(STEEL)
    canvas.drawString(MARGIN, 0.25 * inch, "clarvix.net")
    canvas.drawCentredString(W / 2, 0.25 * inch, "CONFIDENTIAL")
    canvas.drawRightString(W - MARGIN, 0.25 * inch, f"p. {doc.page}")
    canvas.restoreState()

def draw_cover(canvas, doc):
    """Cover page."""
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    canvas.setFillColor(CYAN)
    canvas.rect(0, H - 6, W, 6, fill=1, stroke=0)
    canvas.rect(0, 0, W, 4, fill=1, stroke=0)
    canvas.restoreState()

def tier_card(name, price, sub, items, color):
    """Builds a tier pricing card."""
    header = Table([
        [Paragraph(f"<b>{name}</b>", S["tier"])],
        [Paragraph(f"<b>{price}</b>", S["price"])],
        [Paragraph(sub, mk("ts", fontName="Helvetica", fontSize=9, textColor=STEEL, alignment=TA_CENTER))],
    ], colWidths=[CW / 3 - 12])
    header.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), color),
        ("TOPPADDING", (0,0), (-1,0), 12),
        ("BOTTOMPADDING", (0,-1), (-1,-1), 10),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
    ]))
    
    bullet_rows = []
    for item in items:
        bullet_rows.append([Paragraph(f"<b>+</b>  {item}", S["bullet"])])
    
    body = Table(bullet_rows, colWidths=[CW / 3 - 12])
    body.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK),
        ("TOPPADDING", (0,0), (0,0), 8),
        ("BOTTOMPADDING", (0,-1), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ]))
    
    card = Table([[header], [body]], colWidths=[CW / 3 - 12])
    card.setStyle(TableStyle([
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
    ]))
    return card

def agent_card(icon, name, desc):
    """Agent description card."""
    header = Table([[
        Paragraph(f"<b>{icon}  {name}</b>", mk("an", fontName="Helvetica-Bold", fontSize=11, textColor=WHITE)),
    ]], colWidths=[CW])
    header.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), CYAN),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
    ]))
    body = Table([[
        Paragraph(desc, S["body"]),
    ]], colWidths=[CW])
    body.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
    ]))
    card = Table([[header], [body]], colWidths=[CW])
    card.setStyle(TableStyle([
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
    ]))
    return KeepTogether([card, sp(8)])

def generate_pdf(lang_code, output_dir):
    """Generate the full PDF for a given language."""
    L = LANGS[lang_code]
    filename = f"clarvix-adtech-ai-agents-{lang_code}.pdf"
    filepath = os.path.join(output_dir, filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter,
                            leftMargin=MARGIN, rightMargin=MARGIN,
                            topMargin=MARGIN + 0.2*inch, bottomMargin=MARGIN + 0.2*inch)
    story = []
    
    # ── COVER PAGE ──
    story.append(sp(1.5 * inch))
    # Clarvix logo text
    story.append(Paragraph("<b>CLARVIX</b>", mk("logo", fontName="Helvetica-Bold", fontSize=36, textColor=CYAN, alignment=TA_CENTER, leading=44)))
    story.append(sp(6))
    # Badge
    badge = Table([[Paragraph(f"<b>AI AGENT ARCHITECTURE  |  {lang_code.upper()}</b>",
        mk("badge", fontName="Helvetica-Bold", fontSize=8, textColor=NAVY, alignment=TA_CENTER))
    ]], colWidths=[280])
    badge.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), CYAN),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ]))
    story.append(badge)
    story.append(sp(24))
    story.append(Paragraph(L["doc_title"], S["title"]))
    story.append(sp(8))
    story.append(Paragraph(L["doc_sub"], S["subtitle"]))
    story.append(sp(40))
    # Prepared by + contact
    story.append(Paragraph(L["prepared"], mk("prep", fontName="Helvetica", fontSize=10, textColor=STEEL, alignment=TA_CENTER)))
    story.append(sp(6))
    story.append(Paragraph(f'{L["email"]}  |  {L["web"]}', mk("con", fontName="Helvetica", fontSize=9, textColor=CYAN_L, alignment=TA_CENTER)))
    story.append(sp(30))
    story.append(Paragraph(L["tagline"], mk("tag", fontName="Helvetica-Bold", fontSize=11, textColor=WHITE, alignment=TA_CENTER)))

    story.append(PageBreak())

    # ── SECTION 1: OVERVIEW ──
    story.append(Paragraph(L["overview_title"], S["h1"]))
    story.append(sp(4))
    story.append(Paragraph(L["overview_p1"], S["body"]))
    story.append(sp(4))
    story.append(Paragraph(L["overview_p2"], S["body"]))
    story.append(sp(16))

    # ── SECTION 2: AGENTS ──
    story.append(Paragraph(L["agents_title"], S["h1"]))
    story.append(sp(8))
    story.append(agent_card("[R]", L["agent1_name"], L["agent1_desc"]))
    story.append(agent_card("[A]", L["agent2_name"], L["agent2_desc"]))
    story.append(agent_card("[I]", L["agent3_name"], L["agent3_desc"]))
    story.append(sp(8))

    # ── SECTION 3: TIERS ──
    story.append(PageBreak())
    story.append(Paragraph(L["tiers_title"], S["h1"]))
    story.append(sp(10))

    c1 = tier_card(L["tier1_name"], L["tier1_price"], L["tier1_sub"], L["tier1_items"], MID)
    c2 = tier_card(L["tier2_name"], L["tier2_price"], L["tier2_sub"], L["tier2_items"], CYAN)
    c3 = tier_card(L["tier3_name"], L["tier3_price"], L["tier3_sub"], L["tier3_items"], colors.HexColor("#7C3AED"))

    tier_table = Table([[c1, c2, c3]], colWidths=[CW/3 - 4, CW/3 - 4, CW/3 - 4],
                       spaceBefore=0, spaceAfter=0)
    tier_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
    ]))
    story.append(tier_table)
    story.append(sp(20))

    # ── SECTION 4: HOW IT WORKS ──
    story.append(Paragraph(L["how_title"], S["h1"]))
    story.append(sp(8))

    for i, (step_title, step_desc) in enumerate(L["how_steps"], 1):
        num_style = mk(f"num{i}", fontName="Helvetica-Bold", fontSize=18, textColor=CYAN, leading=22)
        title_style = mk(f"st{i}", fontName="Helvetica-Bold", fontSize=11, textColor=WHITE, leading=14)
        desc_style = mk(f"sd{i}", fontName="Helvetica", fontSize=9.5, textColor=STEEL, leading=13)

        step_row = Table([[
            Paragraph(f"<b>{i}</b>", num_style),
            Table([
                [Paragraph(step_title, title_style)],
                [Paragraph(step_desc, desc_style)],
            ], colWidths=[CW - 50])
        ]], colWidths=[40, CW - 50])
        step_row.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), DARK),
            ("VALIGN", (0,0), (0,0), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING", (0,0), (0,0), 12),
            ("LEFTPADDING", (1,0), (1,0), 4),
        ]))
        story.append(KeepTogether([step_row, sp(6)]))

    story.append(sp(10))

    # ── SECTION 5: EXPECTED RESULTS ──
    story.append(Paragraph(L["results_title"], S["h1"]))
    story.append(sp(8))

    # KPI cards row
    kpi_cells = []
    kpi_colors = [GREEN, AMBER, CYAN, PURPLE]
    for idx, (metric, value, detail) in enumerate(L["results"]):
        kpi_inner = Table([
            [Paragraph(f"<b>{value}</b>", S["kpi_n"])],
            [Paragraph(metric, S["kpi_l"])],
            [Paragraph(detail, mk(f"kd{idx}", fontName="Helvetica", fontSize=7, textColor=STEEL, alignment=TA_CENTER, leading=9))],
        ], colWidths=[CW/4 - 16])
        kpi_inner.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), DARK),
            ("TOPPADDING", (0,0), (0,0), 12),
            ("BOTTOMPADDING", (0,-1), (-1,-1), 10),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("RIGHTPADDING", (0,0), (-1,-1), 6),
            ("LINEABOVE", (0,0), (-1,0), 3, kpi_colors[idx]),
        ]))
        kpi_cells.append(kpi_inner)

    kpi_table = Table([kpi_cells], colWidths=[CW/4 - 4]*4)
    kpi_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(kpi_table)
    story.append(sp(30))

    # ── CTA ──
    cta_box = Table([
        [Paragraph(f"<b>{L['cta_title']}</b>", mk("cta_t", fontName="Helvetica-Bold", fontSize=16, textColor=WHITE, alignment=TA_CENTER, leading=20))],
        [sp(4)],
        [Paragraph(L["cta_text"], mk("cta_b", fontName="Helvetica", fontSize=10, textColor=colors.HexColor("#CBD5E1"), alignment=TA_CENTER, leading=14))],
        [sp(8)],
        [Paragraph(f'<b>{L["email"]}</b>', mk("cta_e", fontName="Helvetica-Bold", fontSize=11, textColor=CYAN, alignment=TA_CENTER))],
    ], colWidths=[CW - 40])
    cta_box.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), MID),
        ("TOPPADDING", (0,0), (-1,0), 20),
        ("BOTTOMPADDING", (0,-1), (-1,-1), 20),
        ("LEFTPADDING", (0,0), (-1,-1), 20),
        ("RIGHTPADDING", (0,0), (-1,-1), 20),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("BOX", (0,0), (-1,-1), 1, CYAN),
    ]))
    story.append(KeepTogether([cta_box]))

    # ── BUILD ──
    doc.build(story, onFirstPage=draw_cover, onLaterPages=draw_bg)
    print(f"  [OK] {filename}")
    return filepath


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    print("Generating Clarvix AdTech AI Agent Service Briefs...")
    print(f"Output: {out_dir}\n")
    generated = []
    for lang in ["en", "es", "he", "ar"]:
        path = generate_pdf(lang, out_dir)
        generated.append(path)
    print(f"\nDone! Generated {len(generated)} PDFs.")
