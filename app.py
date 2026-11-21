"""
app.py - Main Streamlit application entry point for StemCell Insight.
StemCell Insight: An Intelligent Stem Cell Knowledge and Cell-Fate Prediction System.
"""

import os
import sys
import streamlit as st

# Ensure project root is in system path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.database import init_db, get_database_stats
from database.seed_data import seed_database
from modules.home import render_home
from modules.cell_explorer import render_cell_explorer
from modules.chatbot import render_chatbot
from modules.prediction_engine import render_prediction_engine
from modules.protocol_advisor import render_protocol_advisor
from modules.evidence_analyzer import render_evidence_analyzer


# Page Configuration
st.set_page_config(
    page_title="StemCell Insight",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Biotech Research Platform Theme: Clean, Professional, Light background, Teal/Navy accents)
st.markdown(
    """
    <style>
        /* Main background & typography */
        .main {
            background-color: #f8fafc;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #0f172a;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #0f172a;
            color: #f1f5f9;
        }
        section[data-testid="stSidebar"] .stMarkdown h1,
        section[data-testid="stSidebar"] .stMarkdown h2,
        section[data-testid="stSidebar"] .stMarkdown h3 {
            color: #ffffff;
        }
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] .stMarkdown span {
            color: #94a3b8;
        }
        /* Buttons */
        .stButton>button {
            border-radius: 6px;
            font-weight: 500;
        }
        /* Metric cards */
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
            color: #0d9488;
            font-weight: 700;
        }
    </style>
    """,
    unsafe_allow_html=True
)


def main():
    # Initialize database if needed (safe, does not overwrite existing data)
    init_db()

    # Auto-seed on first run or if DB is empty (needed for Streamlit Cloud which resets filesystem)
    stats = get_database_stats()
    if stats.get("total_stem_cells", 0) == 0:
        with st.spinner("🧬 First run detected — building knowledge base from curated scientific data..."):
            seed_database()
            st.rerun()

    # Sidebar Navigation
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 0.5rem 0 1rem 0;">
                <h2 style="color: #ffffff; margin: 0; font-size: 1.5rem; font-weight: 700; letter-spacing: -0.5px;">
                    🧬 STEMCELL INSIGHT
                </h2>
                <p style="color: #5eead4; font-size: 0.8rem; margin: 0.2rem 0 0 0;">
                    Intelligent Stem Cell Knowledge Platform
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")

        nav_options = [
            "🏠 Home Dashboard",
            "🔬 Cell Explorer",
            "💬 Ask StemCell Insight",
            "🧠 Cell-Fate Prediction",
            "📋 Protocol Advisor",
            "🔍 Evidence Analyser"
        ]

        selected_page = st.radio(
            "Navigation:",
            options=nav_options,
            index=0,
            key="navigation_radio"
        )

        st.markdown("---")

        # Live Database Statistics in Sidebar
        stats = get_database_stats()
        st.markdown(
            f"""
            <div style="background: #1e293b; border-radius: 8px; padding: 0.8rem; font-size: 0.8rem; color: #cbd5e1;">
                <strong style="color: #38bdf8;">📊 Live Knowledge Base:</strong><br>
                • Stem-Cell Types: <b>{stats.get('total_stem_cells', 0)}</b><br>
                • Registered Cell Lines: <b>{stats.get('total_cell_lines', 0)}</b><br>
                • Differentiation Fates: <b>{stats.get('total_differentiation', 0)}</b><br>
                • Molecular Markers: <b>{stats.get('total_markers', 0)}</b><br>
                • Published Protocols: <b>{stats.get('total_protocols', 0)}</b><br>
                • Scientific References: <b>{stats.get('total_references', 0)}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.caption("Version 1.0.0 | Academic & Biotech Research Edition")

    # Routing
    if selected_page == "🏠 Home Dashboard":
        render_home()
    elif selected_page == "🔬 Cell Explorer":
        render_cell_explorer()
    elif selected_page == "💬 Ask StemCell Insight":
        render_chatbot()
    elif selected_page == "🧠 Cell-Fate Prediction":
        render_prediction_engine()
    elif selected_page == "📋 Protocol Advisor":
        render_protocol_advisor()
    elif selected_page == "🔍 Evidence Analyser":
        render_evidence_analyzer()


if __name__ == "__main__":
    main()
