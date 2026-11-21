"""
home.py - Home Dashboard module for StemCell Insight.
Displays dynamic knowledge base metrics, platform architecture,
and direct navigation to application modules.
"""

import streamlit as st
from database.database import get_database_stats, get_differentiation_records
from utils.visualizations import create_lineage_network


def render_home():
    """Render the main landing page dashboard."""
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 2.2rem 2.5rem; border-radius: 12px; margin-bottom: 2rem; border-left: 6px solid #0d9488;">
            <h1 style="color: #ffffff; margin: 0; font-size: 2.4rem; font-weight: 700; letter-spacing: -0.5px;">STEMCELL INSIGHT</h1>
            <p style="color: #5eead4; font-size: 1.15rem; margin: 0.4rem 0 1rem 0; font-weight: 500;">
                Explore Stem Cell Biology. Understand Cell Fate. Discover Differentiation Pathways.
            </p>
            <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.6; margin: 0; max-width: 900px;">
                An intelligent stem-cell knowledge and explainable cell-fate reasoning system connecting starting stem-cell characteristics,
                induction signaling conditions, intermediate pathways, candidate cell fates, molecular markers, published differentiation protocols,
                and peer-reviewed research evidence.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Dynamic metrics from SQLite
    stats = get_database_stats()

    st.markdown("### 📊 Curated Knowledge Base Statistics")
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric(
            label="Stem Cell Types",
            value=stats.get("total_stem_cells", 0),
            help="ESCs, iPSCs, MSCs, HSCs, NSCs"
        )
    with col2:
        st.metric(
            label="Cell-Line Records",
            value=stats.get("total_cell_lines", 0),
            help="Authenticated cell lines from Cellosaurus & registries"
        )
    with col3:
        st.metric(
            label="Differentiation Paths",
            value=stats.get("total_differentiation", 0),
            help="Curated germ-layer and somatic lineage relationships"
        )
    with col4:
        st.metric(
            label="Molecular Markers",
            value=stats.get("total_markers", 0),
            help="Surface antigens, master transcription factors, enzymes"
        )
    with col5:
        st.metric(
            label="Published Protocols",
            value=stats.get("total_protocols", 0),
            help="Peer-reviewed experimental differentiation protocols"
        )
    with col6:
        st.metric(
            label="Scientific References",
            value=stats.get("total_references", 0),
            help="Traceable peer-reviewed papers with DOIs & PMIDs"
        )

    st.markdown("---")

    # Workflow Architecture
    st.markdown("### 🧬 Integrated Biological Reasoning Flow")
    st.markdown(
        """
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.2rem; margin-bottom: 1.5rem; text-align: center;">
            <span style="font-weight: 600; color: #1e3a8a;">Starting Stem Cell</span>
            <span style="color: #94a3b8; margin: 0 8px;">➔</span>
            <span style="font-weight: 600; color: #0284c7;">Biological Origin & Potency</span>
            <span style="color: #94a3b8; margin: 0 8px;">➔</span>
            <span style="font-weight: 600; color: #d97706;">Induction Signals</span>
            <span style="color: #94a3b8; margin: 0 8px;">➔</span>
            <span style="font-weight: 600; color: #6366f1;">Signaling Pathways</span>
            <span style="color: #94a3b8; margin: 0 8px;">➔</span>
            <span style="font-weight: 600; color: #059669;">Candidate Cell Fate</span>
            <span style="color: #94a3b8; margin: 0 8px;">➔</span>
            <span style="font-weight: 600; color: #0d9488;">Molecular Markers</span>
            <span style="color: #94a3b8; margin: 0 8px;">➔</span>
            <span style="font-weight: 600; color: #7c3aed;">Published Protocols</span>
            <span style="color: #94a3b8; margin: 0 8px;">➔</span>
            <span style="font-weight: 600; color: #e11d48;">Evidence & References</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Core Capabilities Grid
    st.markdown("### 🚀 Platform Capabilities & Modules")
    mcol1, mcol2, mcol3 = st.columns(3)

    with mcol1:
        st.markdown(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.2rem; height: 100%; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <h4 style="color: #0d9488; margin-top: 0;">🔬 Cell Explorer</h4>
                <p style="color: #475569; font-size: 0.9rem;">
                    Examine biological profiles of the 5 core stem-cell categories (ESCs, iPSCs, MSCs, HSCs, NSCs).
                    Search authenticated cell lines, inspect accessions (e.g., H9, WTC-11), potency, tissue origins, and surface markers.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with mcol2:
        st.markdown(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.2rem; height: 100%; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <h4 style="color: #1e3a8a; margin-top: 0;">💬 Ask StemCell Insight</h4>
                <p style="color: #475569; font-size: 0.9rem;">
                    Biology chatbot with keyword search, synonym expansion, and TF-IDF similarity.
                    Answers stem-cell questions with traceable citations, avoiding AI hallucinations.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with mcol3:
        st.markdown(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.2rem; height: 100%; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <h4 style="color: #059669; margin-top: 0;">🧠 Cell-Fate Prediction</h4>
                <p style="color: #475569; font-size: 0.9rem;">
                    Rule-based biological reasoning engine. Evaluate compatible differentiation outcomes,
                    identify required vs optional signals, and inspect mechanistic rationales with peer-reviewed literature.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    mcol4, mcol5, mcol6 = st.columns(3)
    with mcol4:
        st.markdown(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.2rem; height: 100%; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-top: 1rem;">
                <h4 style="color: #7c3aed; margin-top: 0;">📋 Protocol Advisor</h4>
                <p style="color: #475569; font-size: 0.9rem;">
                    Retrieve and compare published differentiation protocols.
                    Inspect sequential steps, reagent concentrations, durations, validation markers, and side-by-side radar differences.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with mcol5:
        st.markdown(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.2rem; height: 100%; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-top: 1rem;">
                <h4 style="color: #d97706; margin-top: 0;">🔍 Evidence Analyser</h4>
                <p style="color: #475569; font-size: 0.9rem;">
                    Assess reporting completeness across 10 empirical parameters.
                    Computes an Evidence Completeness Score and flags missing concentrations, controls, or assays.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with mcol6:
        st.markdown(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.2rem; height: 100%; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-top: 1rem;">
                <h4 style="color: #e11d48; margin-top: 0;">🌐 Lineage Visualizer</h4>
                <p style="color: #475569; font-size: 0.9rem;">
                    Interactive NetworkX and Plotly network diagrams of stem cell lineages,
                    differentiation trajectories, and signaling pathways.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # Interactive Overview Lineage Diagram
    st.markdown("### 🕸️ Curated Stem Cell Lineages & Fates Overview")
    diff_records = get_differentiation_records()
    if diff_records:
        fig = create_lineage_network(diff_records)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No differentiation records currently loaded in the database.")
