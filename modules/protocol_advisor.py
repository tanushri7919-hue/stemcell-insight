"""
protocol_advisor.py - Searchable Differentiation Protocol Database & Comparison Engine.
Enables retrieval, step-by-step procedure inspection, and side-by-side comparison
of published stem-cell differentiation protocols.
"""

import streamlit as st
from typing import Any, Dict, List, Optional
from database.database import get_protocols, get_protocol_by_id, get_protocol_steps
from utils.visualizations import create_protocol_timeline, create_protocol_comparison_radar
from utils.data_validation import evaluate_evidence_completeness


def render_protocol_advisor():
    st.markdown("## 📋 Protocol Advisor")
    st.markdown(
        "Search, inspect, and benchmark published experimental differentiation protocols. "
        "Review sequential laboratory steps, reagent concentrations, reported efficiencies, "
        "and compare multiple protocols side by side."
    )

    tab1, tab2 = st.tabs(["🔍 Search & Inspect Protocols", "⚖️ Side-by-Side Protocol Comparison"])

    # =========================================================================
    # TAB 1: Search & Inspect
    # =========================================================================
    with tab1:
        _render_protocol_search_tab()

    # =========================================================================
    # TAB 2: Side-by-Side Comparison
    # =========================================================================
    with tab2:
        _render_protocol_comparison_tab()


def _render_protocol_search_tab():
    all_protocols = get_protocols()

    col1, col2 = st.columns(2)
    with col1:
        source_cells = ["All"] + sorted(list(set(p["source_cell"] for p in all_protocols)))
        selected_source = st.selectbox("Filter by Starting Stem Cell:", options=source_cells, key="proto_src_filter")

    with col2:
        target_cells = ["All"] + sorted(list(set(p["target_cell"] for p in all_protocols)))
        selected_target = st.selectbox("Filter by Target Differentiated Cell:", options=target_cells, key="proto_tgt_filter")

    filtered_protocols = get_protocols(source_cell=selected_source, target_cell=selected_target)
    st.caption(f"Found {len(filtered_protocols)} published protocols matching criteria.")

    if not filtered_protocols:
        st.warning("No protocols found for the selected combination.")
        return

    proto_dict = {p["protocol_id"]: f"{p['protocol_name']}  ({p['source_cell']} ➔ {p['target_cell']})" for p in filtered_protocols}

    selected_proto_id = st.selectbox(
        "Select Protocol to Inspect:",
        options=list(proto_dict.keys()),
        format_func=lambda pid: proto_dict[pid],
        key="selected_proto_view"
    )

    if selected_proto_id:
        protocol = get_protocol_by_id(selected_proto_id)
        steps = get_protocol_steps(selected_proto_id)
        completeness = evaluate_evidence_completeness(protocol, record_type="protocol")

        _render_full_protocol_card(protocol, steps, completeness)


def _render_full_protocol_card(protocol: dict, steps: list, completeness: dict):
    """Render a comprehensive protocol card with steps and timeline."""
    p_name = protocol.get("protocol_name")
    s_cell = protocol.get("source_cell")
    t_cell = protocol.get("target_cell")
    duration = protocol.get("duration") or "Not reported"
    efficiency = protocol.get("reported_efficiency") or "Not reported"
    eff_method = protocol.get("efficiency_method") or "Not reported"
    medium = protocol.get("medium") or "Not reported"
    gf = protocol.get("growth_factors") or "None reported"
    sm = protocol.get("small_molecules") or "None reported"
    markers = protocol.get("validation_markers") or "Not reported"
    fval = protocol.get("functional_validation") or "Not reported"

    score = completeness["score"]
    score_color = "#16a34a" if score >= 80 else ("#d97706" if score >= 60 else "#dc2626")

    st.markdown(
        f"""
        <div style="background: #ffffff; border: 1px solid #cbd5e1; border-left: 6px solid #0d9488; border-radius: 8px; padding: 1.5rem; margin-top: 1rem; margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: baseline;">
                <h3 style="margin: 0; color: #0f172a;">{p_name}</h3>
                <span style="background: #f0fdf4; color: {score_color}; border: 1px solid {score_color}; padding: 3px 10px; border-radius: 12px; font-weight: 600; font-size: 0.85rem;">
                    Completeness Score: {score}%
                </span>
            </div>
            <p style="color: #64748b; font-size: 0.95rem; margin: 0.3rem 0 0.8rem 0;">
                <b>{s_cell}</b> ➔ <b>{t_cell}</b> | Total Duration: <b>{duration}</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### 🧪 Medium & Chemical Formulations")
        st.markdown(f"**Basal Medium:** {medium}")
        st.markdown(f"**Growth Factors / Cytokines:** {gf}")
        st.markdown(f"**Small Molecules & Supplements:** {sm}")

    with c2:
        st.markdown("#### 🎯 Reported Outcomes & Validation")
        st.markdown(f"**Reported Efficiency:** {efficiency}")
        st.markdown(f"**Quantification Assay:** {eff_method}")
        st.markdown(f"**Validation Markers:** `{markers}`")
        st.markdown(f"**Functional Validation:** {fval}")

    st.markdown("---")

    # Sequential Protocol Steps
    st.markdown("#### 🔬 Sequential Experimental Procedure")
    if steps:
        for s in steps:
            st.markdown(
                f"""
                <div style="border: 1px solid #e2e8f0; border-radius: 6px; padding: 0.9rem; margin-bottom: 0.8rem; background: #fafafa;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                        <strong style="color: #0284c7;">Step {s['step_number']}</strong>
                        <span style="background: #e0f2fe; color: #0369a1; padding: 1px 8px; border-radius: 10px; font-size: 0.8rem;">
                            Duration: {s.get('duration') or 'Not reported'}
                        </span>
                    </div>
                    <div style="color: #1e293b; font-size: 0.92rem; line-height: 1.5;">
                        {s['procedure']}
                    </div>
                    <div style="color: #64748b; font-size: 0.82rem; margin-top: 0.4rem;">
                        <b>Reagent:</b> {s.get('reagent') or 'Standard medium'} | <b>Concentration:</b> {s.get('concentration') or 'N/A'}<br>
                        <b>Notes:</b> <i>{s.get('notes') or 'Standard sterile tissue-culture handling.'}</i>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with st.expander("📊 View Interactive Protocol Timeline", expanded=False):
            fig_t = create_protocol_timeline(steps, p_name)
            st.plotly_chart(fig_t, use_container_width=True)
    else:
        st.info("No step-by-step breakdown recorded for this protocol.")

    # Reference Citation
    if protocol.get("ref_title"):
        st.markdown("---")
        st.markdown("#### 📚 Original Publication & Provenance")
        doi = protocol.get("ref_doi")
        doi_link = f"https://doi.org/{doi}" if doi else "#"
        st.markdown(
            f"**{protocol.get('ref_title')}**<br>"
            f"Authors: {protocol.get('ref_authors', 'Not reported')}<br>"
            f"Journal: *{protocol.get('ref_journal', 'Not reported')}* ({protocol.get('ref_year', '')})<br>"
            f"DOI: [{doi or 'Not reported'}]({doi_link})",
            unsafe_allow_html=True
        )


def _render_protocol_comparison_tab():
    """Side-by-side comparison of 2 or more differentiation protocols."""
    st.markdown("### ⚖️ Side-by-Side Protocol Comparison")
    st.markdown("Select at least two published protocols to contrast their reagents, durations, steps, and reporting metrics.")

    all_protocols = get_protocols()
    proto_options = {p["protocol_id"]: f"{p['protocol_name']}  ({p['source_cell']} ➔ {p['target_cell']})" for p in all_protocols}

    # Default to first two protocols
    default_selection = list(proto_options.keys())[:2]

    selected_ids = st.multiselect(
        "Choose Protocols to Compare (Select 2 or more):",
        options=list(proto_options.keys()),
        default=default_selection,
        format_func=lambda pid: proto_options[pid],
        key="compare_selector"
    )

    if len(selected_ids) < 2:
        st.info("Please select at least two protocols to enable side-by-side comparison.")
        return

    comp_protocols = [get_protocol_by_id(pid) for pid in selected_ids]
    comp_steps = {pid: get_protocol_steps(pid) for pid in selected_ids}
    comp_scores = {pid: evaluate_evidence_completeness(p, record_type="protocol") for pid, p in zip(selected_ids, comp_protocols)}

    # Comparison Table
    st.markdown("#### 📊 Comparison Criteria Matrix")

    cols = st.columns(len(comp_protocols))
    for idx, p in enumerate(comp_protocols):
        pid = p["protocol_id"]
        score_info = comp_scores[pid]

        with cols[idx]:
            st.markdown(
                f"""
                <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-top: 4px solid #0d9488; border-radius: 6px; padding: 1rem; margin-bottom: 1rem;">
                    <h4 style="margin: 0; color: #0f172a; font-size: 1rem;">{p['protocol_name']}</h4>
                    <span style="color: #64748b; font-size: 0.85rem;">{p['source_cell']} ➔ {p['target_cell']}</span><br>
                    <span style="background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 10px; font-size: 0.8rem; font-weight: 600;">
                        Completeness: {score_info['score']}%
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(f"**Basal Medium:** {p.get('medium') or 'Not reported'}")
            st.markdown(f"**Growth Factors:** {p.get('growth_factors') or 'None reported'}")
            st.markdown(f"**Small Molecules:** {p.get('small_molecules') or 'None reported'}")
            st.markdown(f"**Total Duration:** {p.get('duration') or 'Not reported'}")
            st.markdown(f"**Reported Efficiency:** {p.get('reported_efficiency') or 'Not reported'}")
            st.markdown(f"**Assay Method:** {p.get('efficiency_method') or 'Not reported'}")
            st.markdown(f"**Validation Markers:** `{p.get('validation_markers') or 'Not reported'}`")
            st.markdown(f"**Functional Assay:** {p.get('functional_validation') or 'Not reported'}")
            st.markdown(f"**Total Protocol Steps:** {len(comp_steps[pid])}")
            if p.get("ref_doi"):
                st.markdown(f"**DOI:** [{p.get('ref_doi')}](https://doi.org/{p.get('ref_doi')})")

    st.markdown("---")

    # Radar Comparison Chart if exactly 2 protocols selected
    if len(comp_protocols) == 2:
        st.markdown("#### 🕸️ Reporting Completeness Radar Profile")
        fig_r = create_protocol_comparison_radar(
            comp_protocols[0], comp_protocols[1],
            comp_scores[comp_protocols[0]["protocol_id"]],
            comp_scores[comp_protocols[1]["protocol_id"]]
        )
        st.plotly_chart(fig_r, use_container_width=True)

    # Scientific comparison notice
    st.markdown(
        """
        <div style="background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 6px; padding: 0.8rem 1rem; font-size: 0.84rem; color: #475569;">
            <b>Comparative Caveat:</b> Do not blindly compare differentiation efficiency percentages across protocols that utilized different starting cell lines, distinct passage numbers, or divergent analytical assays (e.g., flow cytometry vs. spectrophotometric dye extraction).
        </div>
        """,
        unsafe_allow_html=True
    )
