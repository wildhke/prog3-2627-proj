"""This module provides helper functions for the streamlit application."""
FOOTER_TEXT = "E 308 – Programmieren 3 | D. Wild | WiSe 26/27"

FOOTER_HTML = f"""
<style>
.app-footer {{
    position: fixed; left: 1rem; right: 1rem; bottom: 1rem;
    z-index: 999999;  /* über der Seitenleiste */
    padding: 0.85rem 1.5rem; border-radius: 1rem;
    text-align: center; font-size: 1rem; letter-spacing: 0.02em;
    color: #F5F5F7;
    background: rgba(23, 23, 26, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
    backdrop-filter: blur(16px) saturate(160%);
    -webkit-backdrop-filter: blur(15px) saturate(160%);
}}
[data-testid="stMainBlockContainer"] {{ padding-bottom: 6rem; }}
</style>
<div class="app-footer">{FOOTER_TEXT}</div>
"""

