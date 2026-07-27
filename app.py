import streamlit as st
import time
import re
import os
from datetime import datetime
from dotenv import load_dotenv

from utils.pdf_generator import create_pdf
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ─── Constants ──────────────────────────────────────────────────────────────────
DOWNLOADS_DIR = "downloads"
PDF_FILENAME = "MeetMind_AI_Report.pdf"
PDF_OUTPUT_PATH = os.path.join(DOWNLOADS_DIR, PDF_FILENAME)

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MeetMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─── Icon Library (inline SVG, Feather-style — no emoji) ───────────────────────
_ICON_PATHS = {
    "mic": '<path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/>',
    "brain": '<path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.5A2.5 2.5 0 0 1 4 17.5v-2A2.5 2.5 0 0 1 2 13V9a2.5 2.5 0 0 1 2-2.45V6A2.5 2.5 0 0 1 6.5 3.5 2.5 2.5 0 0 1 9.5 2z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.5A2.5 2.5 0 0 0 20 17.5v-2a2.5 2.5 0 0 0 2-2.45V9a2.5 2.5 0 0 0-2-2.45V6A2.5 2.5 0 0 0 17.5 3.5 2.5 2.5 0 0 0 14.5 2z"/>',
    "file-text": '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/>',
    "message-square": '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>',
    "check-circle": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
    "sparkles": '<path d="M12 3l1.6 4.7L18 9l-4.4 1.3L12 15l-1.6-4.7L6 9l4.4-1.3L12 3z"/><path d="M5 17l.8 2.2L8 20l-2.2.8L5 23l-.8-2.2L2 20l2.2-.8L5 17z"/><path d="M19 15l.7 2 2 .7-2 .7-.7 2-.7-2-2-.7 2-.7.7-2z"/>',
    "search": '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    "video": '<polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>',
    "clipboard": '<path d="M9 4H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-3"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>',
    "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>',
    "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
    "send": '<line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>',
    "trash": '<polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "hash": '<line x1="4" y1="9" x2="20" y2="9"/><line x1="4" y1="15" x2="20" y2="15"/><line x1="10" y1="3" x2="8" y2="21"/><line x1="16" y1="3" x2="14" y2="21"/>',
    "list": '<line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>',
    "key": '<path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0L19 4m-3.5 3.5L19 11"/>',
    "help-circle": '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
    "film": '<rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"/><line x1="7" y1="2" x2="7" y2="22"/><line x1="17" y1="2" x2="17" y2="22"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="2" y1="7" x2="7" y2="7"/><line x1="2" y1="17" x2="7" y2="17"/><line x1="17" y1="17" x2="22" y2="17"/><line x1="17" y1="7" x2="22" y2="7"/>',
    "chevron-down": '<polyline points="6 9 12 15 18 9"/>',
    "user": '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "bot": '<rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><line x1="12" y1="7" x2="12" y2="11"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/>',
    "align-left": '<line x1="17" y1="10" x2="3" y2="10"/><line x1="21" y1="6" x2="3" y2="6"/><line x1="21" y1="14" x2="3" y2="14"/><line x1="17" y1="18" x2="3" y2="18"/>',
    "alert-triangle": '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
    "cpu": '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/>',
}


def icon(name: str, size: int = 16, color: str = "currentColor", stroke_width: float = 1.8) -> str:
    """Return an inline Feather-style SVG icon as an HTML string."""
    path = _ICON_PATHS.get(name, "")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke_width}" '
        f'stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;flex-shrink:0">{path}</svg>'
    )


# ─── Lightweight Markdown → HTML renderer (display only, no backend impact) ────
def render_markdown_content(text: str) -> str:
    """Convert a subset of markdown (headers, bold, italics, bullets, numbered
    lists) coming back from the LLM into styled HTML for premium card display.
    This purely affects presentation — the underlying string from the backend
    is never mutated or re-processed by any pipeline step."""
    if not text:
        return '<span class="muted-empty">No content available.</span>'

    lines = text.strip().split("\n")
    html_parts = []
    in_ul = False
    in_ol = False

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            html_parts.append("</ul>")
            in_ul = False
        if in_ol:
            html_parts.append("</ol>")
            in_ol = False

    def inline(s: str) -> str:
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", s)
        s = re.sub(r"`([^`]+?)`", r"<code>\1</code>", s)
        return s

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped:
            close_lists()
            continue

        h = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if h:
            close_lists()
            level = min(len(h.group(1)) + 3, 6)
            html_parts.append(f"<h{level} class='md-heading'>{inline(h.group(2))}</h{level}>")
            continue

        b = re.match(r"^[-•]\s+(.*)$", stripped)
        if b:
            if not in_ul:
                close_lists()
                html_parts.append("<ul class='md-list'>")
                in_ul = True
            html_parts.append(f"<li>{inline(b.group(1))}</li>")
            continue

        n = re.match(r"^\d+[\.\)]\s+(.*)$", stripped)
        if n:
            if not in_ol:
                close_lists()
                html_parts.append("<ol class='md-list'>")
                in_ol = True
            html_parts.append(f"<li>{inline(n.group(1))}</li>")
            continue

        close_lists()
        html_parts.append(f"<p class='md-p'>{inline(stripped)}</p>")

    close_lists()
    return "".join(html_parts)


def render_transcript_content(text: str) -> str:
    """Render the raw transcript as readable, wrapped HTML paragraphs for the
    collapsible transcript viewer. Purely presentational — never mutates or
    re-processes the transcript string used elsewhere in the pipeline."""
    if not text:
        return '<span class="muted-empty">No transcript available.</span>'

    paragraphs = [p.strip() for p in text.strip().split("\n") if p.strip()]
    if not paragraphs:
        paragraphs = [text.strip()]

    return "".join(f"<p class='transcript-p'>{p}</p>" for p in paragraphs)


# ─── Custom CSS — Premium Dark SaaS Theme (unchanged) ──────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #111111;
    --bg-2: #181818;
    --card: #1F1F1F;
    --card-hover: #242424;
    --accent: #C6A87A;
    --accent-strong: #d8bd93;
    --text: #F8F8F8;
    --text-muted: #B6B6B6;
    --border: rgba(255,255,255,0.08);
    --border-strong: rgba(255,255,255,0.14);
    --success: #7fa87f;
    --danger: #c97b7b;
    --shadow: 0 1px 2px rgba(0,0,0,0.4), 0 8px 24px rgba(0,0,0,0.35);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp { background: var(--bg) !important; }

h1, h2, h3, h4, h5, h6 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--text) !important;
    letter-spacing: -0.01em;
}

/* ── Fade-in for cards ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg-2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.15rem;
}
.sidebar-brand-text {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    line-height: 1.2;
}
.sidebar-brand-sub {
    font-size: 0.68rem;
    color: var(--text-muted);
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 1.1rem;
}
.sidebar-section-label {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.66rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 1.2rem 0 0.6rem 0;
}
.sidebar-helper-text {
    font-size: 0.72rem;
    line-height: 1.9;
    color: var(--text-muted);
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.5rem 0.75rem;
    margin: 0.4rem 0 0.2rem 0;
}

/* ── Pipeline timeline (compact) ── */
.timeline-item {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    padding: 0.4rem 0.1rem;
    font-size: 0.8rem;
    color: var(--text-muted);
}
.timeline-item.done { color: var(--text); }
.timeline-item.active { color: var(--accent); }
.timeline-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
    background: var(--border-strong);
}
.timeline-item.done .timeline-dot { background: var(--success); }
.timeline-item.active .timeline-dot {
    background: var(--accent);
    box-shadow: 0 0 0 3px rgba(198,168,122,0.18);
    animation: pulseDot 1.4s infinite;
}
@keyframes pulseDot {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.45; }
}

/* ── Hero (compact) ── */
.hero-wrap { padding: 0.2rem 0 1rem 0; }
.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.5rem;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(1.7rem, 3.2vw, 2.4rem);
    font-weight: 700;
    line-height: 1.15;
    margin: 0;
    color: var(--text);
}
.hero-sub {
    font-size: 0.92rem;
    color: var(--text-muted);
    margin-top: 0.35rem;
    max-width: 560px;
    line-height: 1.7;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    margin-top: 0.9rem;
    padding: 0.4rem 0.85rem;
    border-radius: 999px;
    background: rgba(198,168,122,0.1);
    border: 1px solid rgba(198,168,122,0.28);
    color: var(--accent-strong);
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
}

/* ── Generic Card ── */
.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.4rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: var(--shadow);
    transition: border-color 0.2s ease, transform 0.2s ease, background 0.2s ease;
    animation: fadeInUp 0.35s ease;
}
.card:hover {
    border-color: var(--border-strong);
    background: var(--card-hover);
}
.card-accent {
    border-left: 2.5px solid var(--accent);
}
.card-header {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.9rem;
}
.card-header svg { color: var(--accent); }
.card-content { font-size: 0.9rem; line-height: 1.75; color: var(--text); }

/* ── Markdown content inside cards ── */
.md-heading { font-size: 1rem !important; margin: 0.9rem 0 0.4rem 0 !important; color: var(--text) !important; }
.md-heading:first-child { margin-top: 0 !important; }
.md-p { margin: 0 0 0.6rem 0; color: var(--text); line-height: 1.75; }
.md-list { margin: 0 0 0.7rem 1.1rem; padding: 0; color: var(--text); }
.md-list li { margin-bottom: 0.35rem; line-height: 1.65; }
.md-p code, .md-list code { background: rgba(255,255,255,0.06); padding: 0.1rem 0.35rem; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-size: 0.82em; }
.muted-empty { color: var(--text-muted); font-style: italic; font-size: 0.85rem; }

/* ── Metric cards ── */
.metric-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.1rem 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    transition: border-color 0.2s ease, transform 0.2s ease;
    animation: fadeInUp 0.35s ease;
}
.metric-card:hover { border-color: var(--accent); transform: translateY(-2px); }
.metric-icon {
    width: 34px; height: 34px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 10px;
    background: rgba(198,168,122,0.12);
    color: var(--accent);
}
.metric-label { font-size: 0.7rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-muted); font-weight: 600; }
.metric-value { font-family: 'Space Grotesk', sans-serif; font-size: 1.55rem; font-weight: 700; color: var(--text); }

/* ── Session title / status card ── */
.title-card {
    background: linear-gradient(135deg, var(--card) 0%, var(--bg-2) 100%);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.5rem 1.7rem;
    margin-bottom: 1.1rem;
    box-shadow: var(--shadow);
    animation: fadeInUp 0.35s ease;
}
.title-card-label {
    display: flex; align-items: center; gap: 0.5rem;
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--text-muted); margin-bottom: 0.5rem;
}
.title-card-label svg { color: var(--accent); }
.title-card-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.5rem; font-weight: 700; color: var(--text);
}
.status-pill {
    display: inline-flex; align-items: center; gap: 0.35rem;
    margin-top: 0.85rem;
    padding: 0.3rem 0.75rem;
    border-radius: 999px;
    background: rgba(127,168,127,0.14);
    border: 1px solid rgba(127,168,127,0.3);
    color: var(--success);
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase;
}

/* ── Badges ── */
.badge {
    display: inline-flex; align-items: center; gap: 0.35rem;
    padding: 0.28rem 0.7rem;
    border-radius: 999px;
    font-size: 0.66rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;
    background: rgba(198,168,122,0.12);
    color: var(--accent);
    border: 1px solid rgba(198,168,122,0.3);
}

/* ── Buttons ── */
.stButton > button {
    background: #000000 !important;
    color: var(--text) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: 12px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.02em !important;
    padding: 0.62rem 1.4rem !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.3) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: var(--accent) !important;
    color: #111111 !important;
    border-color: var(--accent) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 20px rgba(198,168,122,0.28) !important;
}
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    border: 1px solid var(--border) !important;
}
.stButton > button[kind="secondary"]:hover {
    background: var(--card-hover) !important;
    color: var(--text) !important;
    border-color: var(--border-strong) !important;
}

/* ── Download button (used for PDF export) ── */
.stDownloadButton > button {
    background: #000000 !important;
    color: var(--text) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: 12px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.02em !important;
    padding: 0.62rem 1.4rem !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.3) !important;
    transition: all 0.2s ease !important;
}
.stDownloadButton > button:hover {
    background: var(--accent) !important;
    color: #111111 !important;
    border-color: var(--accent) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 20px rgba(198,168,122,0.28) !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(198,168,122,0.15) !important;
}
.stTextInput > div > div > input::placeholder { color: var(--text-muted) !important; opacity: 0.7; }

/* ── Transcript viewer (full width, collapsible) ── */
.transcript-card { padding: 0 !important; overflow: hidden; }
.transcript-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1rem 1.4rem;
    border-bottom: 1px solid var(--border);
    background: rgba(255,255,255,0.02);
}
.transcript-header-left { display: flex; align-items: center; gap: 0.55rem; font-family: 'Space Grotesk', sans-serif; font-size: 0.78rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: var(--text-muted); }
.transcript-header-left svg { color: var(--accent); }
.transcript-body-wrap { padding: 0.6rem 0.2rem 0.4rem 0.2rem; }

[data-testid="stExpander"] .transcript-scroll {
    max-height: 480px;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 0.4rem 0.9rem;
}
.transcript-p {
    font-size: 0.92rem;
    line-height: 2;
    color: var(--text);
    margin: 0 0 0.9rem 0;
    white-space: pre-wrap;
    word-break: break-word;
    overflow-wrap: anywhere;
}
.transcript-p:last-child { margin-bottom: 0; }

/* ── Export card ── */
.export-copy { color: var(--text-muted); font-size: 0.85rem; line-height: 1.7; text-align: center; max-width: 620px; margin: 0 auto 1.1rem auto; }
.export-error-text { color: var(--danger); font-size: 0.85rem; display: flex; align-items: center; justify-content: center; gap: 0.4rem; }
.export-center { display: flex; justify-content: center; }

/* ── Chat ── */
.chat-container {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.3rem;
    max-height: 460px;
    overflow-y: auto;
    margin-bottom: 1rem;
}
.chat-row { display: flex; gap: 0.65rem; margin-bottom: 1.1rem; align-items: flex-start; }
.chat-row.user { flex-direction: row-reverse; }
.chat-avatar {
    width: 30px; height: 30px; border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.chat-avatar.user-avatar { background: rgba(198,168,122,0.16); color: var(--accent); }
.chat-avatar.bot-avatar { background: rgba(255,255,255,0.07); color: var(--text-muted); }
.chat-bubble-wrap { max-width: 78%; display: flex; flex-direction: column; }
.chat-row.user .chat-bubble-wrap { align-items: flex-end; }
.chat-bubble {
    padding: 0.65rem 1rem;
    border-radius: 14px;
    font-size: 0.87rem;
    line-height: 1.65;
}
.chat-row.user .chat-bubble { background: rgba(198,168,122,0.14); border: 1px solid rgba(198,168,122,0.28); border-top-right-radius: 4px; color: var(--text); }
.chat-row.bot .chat-bubble { background: var(--bg-2); border: 1px solid var(--border); border-top-left-radius: 4px; color: var(--text); }

/* ── Empty states ── */
.empty-state {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    padding: 3rem 2rem; text-align: center;
}
.empty-state-icon {
    width: 56px; height: 56px; border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
    background: rgba(198,168,122,0.1);
    color: var(--accent);
    margin-bottom: 1rem;
}
.empty-state-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.2rem; font-weight: 700; color: var(--text); margin-bottom: 0.4rem; }
.empty-state-sub { color: var(--text-muted); font-size: 0.85rem; max-width: 380px; line-height: 1.7; }

/* ── Footer ── */
.app-footer {
    margin-top: 2.5rem;
    padding: 1.4rem 0 1rem 0;
    border-top: 1px solid var(--border);
    text-align: center;
}
.app-footer-label {
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.6rem;
}
.app-footer-badges {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5rem;
}

/* ── Divider ── */
hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.4rem 0 !important; }

/* ── Misc Streamlit overrides ── */
.stProgress > div > div > div { background: var(--accent) !important; }
.stSpinner > div { border-top-color: var(--accent) !important; }
[data-testid="stMarkdownContainer"] p { color: var(--text) !important; }
label { color: var(--text-muted) !important; font-size: 0.8rem !important; }
[data-testid="stExpander"] { background: var(--card); border: 1px solid var(--border); border-radius: 14px; }
div[data-testid="column"] { padding: 0 0.5rem; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-2); }
::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ─────────────────────────────────────────────────────────
# NOTE: "pdf_path", "pdf_error" and "pdf_toast_pending" are the only new keys
# added to support the PDF export feature. Every existing key is untouched.
for key, default in {
    "result": None,
    "chat_history": [],
    "processing": False,
    "pipeline_done": False,
    "pipeline_steps": {},
    "pdf_path": None,
    "pdf_error": None,
    "pdf_toast_pending": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Helpers ────────────────────────────────────────────────────────────────────
def step_status(steps: dict, key: str) -> str:
    """Return the CSS status class ('active' | 'done' | 'pending') for a pipeline step."""
    s = steps.get(key, "pending")
    if s == "active":
        return "active"
    if s == "done":
        return "done"
    return "pending"


def render_timeline_item(label: str, key: str, icon_name: str):
    """Render a single compact timeline row in the sidebar pipeline status list."""
    status = step_status(st.session_state.pipeline_steps, key)
    check = icon("check-circle", 12, "currentColor") if status == "done" else ""
    st.markdown(f"""
    <div class="timeline-item {status}">
        <span class="timeline-dot"></span>
        {icon(icon_name, 14)}
        <span>{label}</span>
        {"<span style='margin-left:auto'>" + check + "</span>" if check else ""}
    </div>""", unsafe_allow_html=True)


def word_count(text: str) -> int:
    """Return the number of whitespace-separated words in a string."""
    return len(text.split()) if text else 0


def reading_time_minutes(text: str) -> int:
    """Estimate reading time in minutes assuming ~200 words per minute."""
    wc = word_count(text)
    return max(1, round(wc / 200))


def ensure_downloads_folder() -> None:
    """Create the downloads/ folder if it doesn't already exist.

    Raises OSError if the folder truly cannot be created (e.g. permissions
    issue) so the caller can surface a graceful, specific error message.
    """
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)


def generate_meeting_pdf(result: dict) -> str:
    """Build the AI Meeting Report PDF from the pipeline result and return
    the path to the generated file.

    Delegates the actual PDF construction to utils.pdf_generator.create_pdf
    (built with reportlab), passing everything needed for a full report:
    meeting title, executive summary, action items, key decisions, open
    questions and full transcript.

    create_pdf() writes the file to `filename` and does not return a path,
    so we return PDF_OUTPUT_PATH ourselves once the call completes.
    """
    create_pdf(
        filename=PDF_OUTPUT_PATH,
        title=result.get("title", "Untitled Meeting"),
        summary=result.get("summary", ""),
        action_items=result.get("action_items", ""),
        decisions=result.get("key_decisions", ""),
        questions=result.get("open_questions", ""),
        transcript=result.get("transcript", ""),
    )
    return PDF_OUTPUT_PATH


def build_pdf_report_if_possible(result: dict) -> None:
    """Generate the PDF report exactly once per successful analysis.

    Populates st.session_state.pdf_path on success or st.session_state.pdf_error
    on failure. This function is only called from inside the pipeline's success
    path, so reruns never trigger regeneration — the existing file is simply
    reused for downloads.
    """
    st.session_state.pdf_path = None
    st.session_state.pdf_error = None

    transcript = result.get("transcript")
    summary = result.get("summary")

    if not transcript or not summary:
        st.session_state.pdf_error = "Cannot generate report: transcript or summary is missing."
        return

    try:
        ensure_downloads_folder()
    except OSError as e:
        st.session_state.pdf_error = f"Could not create downloads folder: {e}"
        return

    try:
        pdf_path = generate_meeting_pdf(result)
        if not pdf_path or not os.path.exists(pdf_path):
            st.session_state.pdf_error = "PDF generation did not produce a valid file."
            return
        st.session_state.pdf_path = pdf_path
        st.session_state.pdf_toast_pending = True
    except Exception as e:
        st.session_state.pdf_error = f"PDF generation failed: {e}"


# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-brand">
        {icon("brain", 26, "var(--accent)", 1.6)}
        <div class="sidebar-brand-text">MeetMind AI</div>
    </div>
    <div class="sidebar-brand-sub">AI Meeting Intelligence</div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown(f'<div class="sidebar-section-label">{icon("upload", 13)} Meeting Source</div>', unsafe_allow_html=True)
    source = st.text_input(
        "YouTube URL or File Path",
        placeholder="Paste YouTube URL or select a local audio/video file",
        label_visibility="collapsed",
    )

    st.markdown("""
    <div class="sidebar-helper-text">
        <strong>Supported</strong><br>
        • YouTube URL<br>
        • MP3<br>
        • WAV<br>
        • M4A<br>
        • MP4<br>
        • MOV<br>
        • MKV
    </div>
    """, unsafe_allow_html=True)

    run_btn = st.button("Analyse", use_container_width=True)

    if st.session_state.pipeline_done:
        st.markdown(f'<div class="sidebar-section-label">{icon("check-circle", 13)} Pipeline Status</div>', unsafe_allow_html=True)
        for step, ic, label in [
            ("audio",      "mic",             "Audio"),
            ("transcript", "file-text",       "Transcript"),
            ("title",      "hash",            "Title"),
            ("summary",    "align-left",      "Summary"),
            ("extract",    "list",            "Extraction"),
            ("rag",        "brain",           "RAG"),
        ]:
            render_timeline_item(label, step, ic)

# ─── Main Area — Hero ───────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-wrap">
    <div class="hero-eyebrow">{icon("sparkles", 13)} AI Meeting Intelligence Platform</div>
    <div class="hero-title">MeetMind AI</div>
    <div class="hero-sub">Transform meeting recordings into searchable knowledge. Transcribe. Summarize. Extract action items. Chat with your meeting using AI.</div>
    <div class="hero-badge">{icon("cpu", 13)} Powered by Whisper • LangChain • Mistral AI • ChromaDB</div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ── Run Pipeline (backend logic unchanged) ──────────────────────────────────────
if run_btn:
    if not source.strip():
        st.error("Please enter a YouTube URL or file path.")
    else:
        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}
        st.session_state.pdf_path = None
        st.session_state.pdf_error = None

        # Clear previous RAG chain
        if "rag_chain" in st.session_state:
            del st.session_state["rag_chain"]

        progress_placeholder = st.empty()

        def update_step(key, state):
            st.session_state.pipeline_steps[key] = state

        try:
            with progress_placeholder.container():
                st.info("Pipeline running — see sidebar for live status…")

            update_step("audio", "active")
            chunks = process_input(source)
            update_step("audio", "done")

            update_step("transcript", "active")
            transcript = transcribe_all(chunks)
            update_step("transcript", "done")

            update_step("title", "active")
            title = generate_title(transcript)
            update_step("title", "done")

            update_step("summary", "active")
            summary = summarize(transcript)
            update_step("summary", "done")

            update_step("extract", "active")
            action_items  = extract_action_items(transcript)
            decisions     = extract_key_decisions(transcript)
            questions     = extract_questions(transcript)
            update_step("extract", "done")

            update_step("rag", "active")

            rag_chain = build_rag_chain(transcript)

            st.session_state.rag_chain = rag_chain

            update_step("rag", "done")

            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
            }
            st.session_state.pipeline_done = True

            # Generate the PDF report once, right after a successful analysis.
            # Failures here are non-fatal: the dashboard still shows all
            # results, only the export card reflects the error.
            build_pdf_report_if_possible(st.session_state.result)

            progress_placeholder.success("Analysis complete!")
            time.sleep(0.5)
            progress_placeholder.empty()
            st.rerun()

        except Exception as e:
            for k in ["audio", "transcript", "title", "summary", "extract", "rag"]:
                if st.session_state.pipeline_steps.get(k) == "active":
                    st.session_state.pipeline_steps[k] = "pending"
            progress_placeholder.error(f"Error: {e}")

# ── Results ──────────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    # Show the "PDF generated" toast exactly once, right after a fresh report
    # was built — it survives the st.rerun() via this session_state flag.
    if st.session_state.pdf_toast_pending:
        st.toast("PDF report generated successfully!", icon="✅")
        st.session_state.pdf_toast_pending = False

    # ── Session title / status card (Meeting Overview) ─────────────────────
    st.markdown(f"""
    <div class="title-card">
        <div class="title-card-label">{icon("video", 14)} Meeting Overview</div>
        <div class="title-card-value">{r['title']}</div>
        <span class="status-pill">{icon("check-circle", 12)} Completed</span>
    </div>""", unsafe_allow_html=True)

    # ── Metrics row ──────────────────────────────────────────────────────────
    words = word_count(r["transcript"])
    rtime = reading_time_minutes(r["transcript"])
    tlen = len(r["transcript"]) if r["transcript"] else 0

    m1, m2, m3, m4 = st.columns(4, gap="medium")
    metrics = [
        (m1, "hash",      "Words",              f"{words:,}"),
        (m2, "clock",     "Reading Time",       f"{rtime} min"),
        (m3, "globe",     "Language",           "English"),
        (m4, "file-text", "Transcript Length",  f"{tlen:,} chars"),
    ]
    for col, ic, label, value in metrics:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">{icon(ic, 17)}</div>
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1.1rem'></div>", unsafe_allow_html=True)

    # ── Summary (full width) ────────────────────────────────────────────────
    st.markdown(f"""
    <div class="card card-accent">
        <div class="card-header">{icon("align-left", 15)} Summary</div>
        <div class="card-content">{render_markdown_content(r['summary'])}</div>
    </div>""", unsafe_allow_html=True)

    # ── Action items | decisions | questions ────────────────────────────────
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(f"""
        <div class="card card-accent">
            <div class="card-header">{icon("check-circle", 15)} Action Items</div>
            <div class="card-content">{render_markdown_content(r['action_items'])}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="card card-accent">
            <div class="card-header">{icon("key", 15)} Key Decisions</div>
            <div class="card-content">{render_markdown_content(r['key_decisions'])}</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="card card-accent">
            <div class="card-header">{icon("help-circle", 15)} Open Questions</div>
            <div class="card-content">{render_markdown_content(r['open_questions'])}</div>
        </div>""", unsafe_allow_html=True)

    # ── Full Transcript (full width, collapsible) ──────────────────────────
    st.markdown(f"""
    <div class="card" style="padding-bottom:0.4rem">
        <div class="card-header" style="margin-bottom:0.4rem">{icon("file-text", 15)} Full Transcript
            <span class="badge" style="margin-left:auto">{words:,} words</span>
        </div>
    """, unsafe_allow_html=True)

    with st.expander("📄 View Full Transcript", expanded=False):
        st.markdown(
            f'<div class="transcript-scroll">{render_transcript_content(r["transcript"])}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Export section ──────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="card card-accent">
        <div class="card-header">{icon("clipboard", 15)} Export Meeting Report</div>
    """, unsafe_allow_html=True)

    if st.session_state.pdf_path and os.path.exists(st.session_state.pdf_path):
        st.markdown(
            '<div class="export-copy">Download a professionally formatted meeting report '
            'including summary, transcript, action items, key decisions and open questions.</div>',
            unsafe_allow_html=True,
        )
        exp_left, exp_center, exp_right = st.columns([1, 2, 1], gap="medium")
        with exp_center:
            try:
                with open(st.session_state.pdf_path, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                st.download_button(
                    label="📥 Download MeetMind Report",
                    data=pdf_bytes,
                    file_name=PDF_FILENAME,
                    mime="application/pdf",
                    use_container_width=True,
                )
            except OSError as e:
                st.markdown(
                    f'<div class="export-error-text">{icon("alert-triangle", 14)} '
                    f'Could not read the generated PDF: {e}</div>',
                    unsafe_allow_html=True,
                )
    elif st.session_state.pdf_error:
        st.markdown(
            f'<div class="export-error-text">{icon("alert-triangle", 14)} '
            f'{st.session_state.pdf_error}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="export-copy">Report export is not available for this session yet.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ── RAG Chat ──────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.5rem;font-family:'Space Grotesk',sans-serif;
    font-size:1.05rem;font-weight:700;margin-bottom:0.9rem">
        {icon("message-square", 18, "var(--accent)")} Chat with your Meeting
    </div>""", unsafe_allow_html=True)

    if st.session_state.chat_history:
        chat_html = '<div class="chat-container">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f"""
                <div class="chat-row user">
                    <div class="chat-avatar user-avatar">{icon("user", 15)}</div>
                    <div class="chat-bubble-wrap">
                        <div class="chat-bubble">{msg['content']}</div>
                    </div>
                </div>"""
            else:
                chat_html += f"""
                <div class="chat-row bot">
                    <div class="chat-avatar bot-avatar">{icon("bot", 15)}</div>
                    <div class="chat-bubble-wrap">
                        <div class="chat-bubble">{msg['content']}</div>
                    </div>
                </div>"""
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="card empty-state" style="margin-bottom:1rem">
            <div class="empty-state-icon">{icon("message-square", 26)}</div>
            <div class="empty-state-title">Ask MeetMind AI</div>
            <div class="empty-state-sub">Ask questions about your meeting, decisions, action items, transcript or any discussed topic.</div>
        </div>""", unsafe_allow_html=True)

    # Chat input
    chat_col1, chat_col2 = st.columns([5, 1], gap="small")
    with chat_col1:
        user_input = st.text_input(
            "Your question",
            placeholder="What were the main decisions made?",
            label_visibility="collapsed",
        )
    with chat_col2:
        send_btn = st.button("Send", use_container_width=True)

    if send_btn and user_input.strip():
        with st.spinner("Thinking…"):
            #answer = ask_question(r["rag_chain"], user_input.strip())
            answer = ask_question(
                st.session_state.rag_chain,
                user_input.strip()
        )
        st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

else:
    # ── Empty state ─────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-state-icon" style="width:64px;height:64px">{icon("film", 30)}</div>
        <div class="empty-state-title" style="font-size:1.4rem">Ready to Analyse</div>
        <div class="empty-state-sub">
            Paste a YouTube URL or upload a meeting recording in the sidebar, choose your language,
            and hit <strong>Analyse</strong> to begin.
        </div>
        <div style="margin-top:1.6rem;display:flex;gap:0.6rem;flex-wrap:wrap;justify-content:center">
            <span class="badge">{icon("mic", 12)} Transcription</span>
            <span class="badge">{icon("sparkles", 12)} Summarisation</span>
            <span class="badge">{icon("message-square", 12)} RAG Chat</span>
        </div>
    </div>""", unsafe_allow_html=True)

# ─── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="app-footer">
    <div class="app-footer-label">Powered by</div>
    <div class="app-footer-badges">
        <span class="badge">Whisper</span>
        <span class="badge">LangChain</span>
        <span class="badge">Mistral AI</span>
        <span class="badge">HuggingFace</span>
        <span class="badge">ChromaDB</span>
        <span class="badge">Streamlit</span>
    </div>
</div>
""", unsafe_allow_html=True)