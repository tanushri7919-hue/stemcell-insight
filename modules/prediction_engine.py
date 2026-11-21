"""
prediction_engine.py - Explainable Rule-Based Cell-Fate Reasoning Engine.
Evaluates biological compatibility between starting stem cells, induction signals,
and developmental trajectories to deduce plausible candidate cell fates.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import streamlit as st
from database.database import (
    get_all_stem_cells, get_differentiation_records,
    get_differentiation_signals, get_markers_for_cell,
    get_all_signals, get_reference
)
from utils.visualizations import create_pathway_diagram


def render_prediction_engine():
    st.markdown("## 🧠 Cell-Fate Prediction Engine")
    st.markdown(
        "An explainable, rule-based biological reasoning system that evaluates starting stem-cell "
        "potency, developmental lineages, and experimental induction conditions to identify "
        "plausible candidate cell fates."
    )

    # Mandatory Scientific Disclaimer
    st.markdown(
        """
        <div style="background: #fffbeb; border: 1px solid #fde68a; border-left: 4px solid #d97706; border-radius: 6px; padding: 0.9rem 1.2rem; margin-bottom: 1.5rem; font-size: 0.88rem; color: #92400e;">
            <b>Scientific Scope & Limitation Notice:</b> This engine is an <i>evidence-based, rule-based biological reasoning system</i> grounded in curated peer-reviewed literature. It is <b>NOT a trained black-box machine learning model</b> and does not report empirical differentiation probabilities. Actual cellular differentiation depends on epigenetic landscape, clone-to-clone heterogeneity, extracellular matrix, and dynamic microenvironmental signaling.
        </div>
        """,
        unsafe_allow_html=True
    )

    # =========================================================================
    # STEP 1: USER INPUTS
    # =========================================================================
    st.markdown("### 1. Configure Experimental Induction Conditions")

    col_in1, col_in2 = st.columns([1, 1])

    with col_in1:
        cells = get_all_stem_cells()
        cell_dict = {c["cell_id"]: f"{c['name']} ({c['cell_id']}) — {c['potency']}" for c in cells}

        selected_source_cell = st.selectbox(
            "Select Starting Stem-Cell Type:",
            options=list(cell_dict.keys()),
            format_func=lambda cid: cell_dict[cid],
            key="pred_source_cell"
        )

        # Retrieve available target lineages for this starting cell
        all_diff_records = get_differentiation_records()
        source_targets = list(set(d["target_cell"] for d in all_diff_records if d["source_cell_id"] == selected_source_cell))
        all_targets = list(set(d["target_cell"] for d in all_diff_records))

        target_options = ["Explore All Compatible Fates"] + sorted(all_targets)

        selected_target = st.selectbox(
            "Select Desired Candidate Fate (or Explore All Compatible):",
            options=target_options,
            key="pred_target_cell"
        )

    with col_in2:
        # Retrieve all available signaling molecules & growth factors
        all_signals = get_all_signals()
        signal_names = sorted(list(set(s["signal_name"] for s in all_signals)))

        # Pre-select common signals if user changes starting cell
        default_signals = []
        if selected_source_cell == "MSC" and selected_target in ("Explore All Compatible Fates", "Osteoblast"):
            default_signals = ["BMP-2", "Dexamethasone", "Ascorbic Acid (Vitamin C)", "beta-Glycerophosphate"]
        elif selected_source_cell in ("ESC", "IPSC") and selected_target in ("Cardiomyocyte", "Explore All Compatible Fates"):
            default_signals = ["CHIR99021", "IWP-2"]
        elif selected_source_cell in ("ESC", "IPSC") and selected_target == "Neural Progenitor Cell":
            default_signals = ["SB431542", "Noggin"]

        selected_signals = st.multiselect(
            "Select Available Induction Signals, Growth Factors & Small Molecules:",
            options=signal_names,
            default=[s for s in default_signals if s in signal_names],
            key="pred_signals"
        )

        culture_matrix = st.selectbox(
            "Culture Matrix / Format:",
            options=[
                "Standard Tissue Culture Polystyrene (Adherent Monolayer)",
                "Extracellular Matrix Coated (Matrigel / Laminin-521)",
                "High-Density 3D Micromass / Centrifuged Pellet",
                "Non-Adherent Suspension / Embryoid Body (EB)"
            ],
            key="pred_matrix"
        )

    # Quick demo buttons
    st.markdown("**⚡ Quick Pre-configured Demos:**")
    dcol1, dcol2, dcol3 = st.columns(3)
    with dcol1:
        if st.button("Demo 1: MSC ➔ Osteoblast Induction", use_container_width=True):
            st.session_state["pred_source_cell"] = "MSC"
            st.session_state["pred_target_cell"] = "Osteoblast"
            st.session_state["pred_signals"] = ["BMP-2", "Dexamethasone", "Ascorbic Acid (Vitamin C)", "beta-Glycerophosphate"]
            st.rerun()

    with dcol2:
        if st.button("Demo 2: MSC ➔ Adipocyte Induction", use_container_width=True):
            st.session_state["pred_source_cell"] = "MSC"
            st.session_state["pred_target_cell"] = "Adipocyte"
            st.session_state["pred_signals"] = ["Dexamethasone", "IBMX", "Indomethacin", "Insulin"]
            st.rerun()

    with dcol3:
        if st.button("Demo 3: HSC ➔ Myeloid Macrophage", use_container_width=True):
            st.session_state["pred_source_cell"] = "HSC"
            st.session_state["pred_target_cell"] = "Macrophage / Monocyte"
            st.session_state["pred_signals"] = ["SCF (Stem Cell Factor)", "FLT3-Ligand", "GM-CSF"]
            st.rerun()

    st.markdown("---")

    # =========================================================================
    # STEP 2: REASONING ENGINE EXECUTION
    # =========================================================================
    st.markdown("### 2. Biological Reasoning & Outcome Evaluation")

    eval_results = evaluate_cell_fate_rules(
        source_cell_id=selected_source_cell,
        target_cell=selected_target if selected_target != "Explore All Compatible Fates" else None,
        available_signals=selected_signals,
        culture_format=culture_matrix
    )

    if not eval_results:
        st.warning(
            f"No compatible differentiation pathways exist in our curated knowledge base for "
            f"**{selected_source_cell}** targeting **{selected_target}**."
        )
        return

    # Check for biologically incompatible starting-cell & target pairs
    incompatible = [r for r in eval_results if r["status"] == "Incompatible Potency"]
    if incompatible:
        for r in incompatible:
            st.error(
                f"❌ **Biologically Unsupported Combination:** {r['reasoning']}"
            )
        st.markdown("---")

    compatible_outcomes = [r for r in eval_results if r["status"] != "Incompatible Potency"]

    if not compatible_outcomes:
        st.info("No supported differentiation fates match this input combination.")
        return

    st.success(f"Identified **{len(compatible_outcomes)}** compatible candidate fate(s) based on curated developmental biology rules.")

    for outcome in compatible_outcomes:
        _render_candidate_fate_card(outcome, selected_source_cell, selected_signals)


def evaluate_cell_fate_rules(
    source_cell_id: str,
    target_cell: Optional[str],
    available_signals: List[str],
    culture_format: str
) -> List[Dict[str, Any]]:
    """Evaluate curated biological rules matching starting cell and induction conditions."""
    all_diffs = get_differentiation_records()
    user_signals_set = set(available_signals)

    results = []

    # Check if user specifically requested an incompatible fate
    if target_cell:
        matching_rules = [d for d in all_diffs if d["target_cell"] == target_cell]
        if matching_rules:
            valid_sources = [d["source_cell_id"] for d in matching_rules]
            if source_cell_id not in valid_sources:
                return [{
                    "status": "Incompatible Potency",
                    "target_cell": target_cell,
                    "reasoning": (
                        f"Starting cell '{source_cell_id}' lacks the developmental potency to directly "
                        f"generate '{target_cell}'. In curated peer-reviewed literature, '{target_cell}' "
                        f"derives from: {', '.join(valid_sources)}. MSCs and adult somatic stem cells "
                        f"cannot cross germ-layer boundaries into lineages reserved for pluripotent "
                        f"cells or distinct adult lineages without genetic transdifferentiation."
                    )
                }]

    # Filter differentiation records applicable to this starting cell
    candidate_diffs = [d for d in all_diffs if d["source_cell_id"] == source_cell_id]
    if target_cell:
        candidate_diffs = [d for d in candidate_diffs if d["target_cell"] == target_cell]

    for diff in candidate_diffs:
        diff_id = diff["differentiation_id"]
        t_cell = diff["target_cell"]
        lineage = diff["lineage"]

        # Retrieve required and optional signals for this path
        ds_records = get_differentiation_signals(diff_id)
        req_signals = [s for s in ds_records if "Required" in s.get("role", "")]
        opt_signals = [s for s in ds_records if "Optional" in s.get("role", "") or "Enhancer" in s.get("role", "")]

        req_names = set(s["signal_name"] for s in req_signals)
        opt_names = set(s["signal_name"] for s in opt_signals)

        # Check signal match
        matched_req = req_names.intersection(user_signals_set)
        missing_req = req_names - user_signals_set
        matched_opt = opt_names.intersection(user_signals_set)

        # Compatibility Status
        if len(req_names) == 0:
            status = "Partially Supported (Default Pathway)"
            compatibility_level = "Moderate"
        elif len(missing_req) == 0:
            status = "Strongly Supported (All Required Signals Present)"
            compatibility_level = "High"
        elif len(matched_req) > 0:
            status = "Incomplete Conditions (Missing Core Signals)"
            compatibility_level = "Partial"
        else:
            status = "Basal Lineage (Signals Not Selected)"
            compatibility_level = "Low"

        # Check special matrix requirements (e.g. 3D pellet for chondrogenesis)
        matrix_notes = None
        if "Chondrocyte" in t_cell and "Pellet" not in culture_format and "3D" not in culture_format:
            matrix_notes = "⚠️ Chondrogenesis requires high-density 3D pellet/micromass culture to simulate precartilage mesenchymal condensation. Monolayer culture is inefficient."

        results.append({
            "status": status,
            "compatibility_level": compatibility_level,
            "diff_record": diff,
            "target_cell": t_cell,
            "lineage": lineage,
            "req_signals": req_signals,
            "opt_signals": opt_signals,
            "matched_req": list(matched_req),
            "missing_req": list(missing_req),
            "matched_opt": list(matched_opt),
            "matrix_notes": matrix_notes
        })

    # Sort results by compatibility level (High > Moderate > Partial > Low)
    level_order = {"High": 1, "Moderate": 2, "Partial": 3, "Low": 4}
    results.sort(key=lambda r: level_order.get(r.get("compatibility_level"), 99))
    return results


def _render_candidate_fate_card(outcome: dict, source_cell_id: str, selected_signals: list):
    """Render a structured explainable result card for a candidate fate."""
    t_cell = outcome["target_cell"]
    lineage = outcome["lineage"]
    status = outcome["status"]
    comp_level = outcome["compatibility_level"]
    diff = outcome["diff_record"]

    color_map = {
        "High": ("#059669", "#ecfdf5", "#065f46"),
        "Moderate": ("#0284c7", "#f0f9ff", "#075985"),
        "Partial": ("#d97706", "#fffbeb", "#92400e"),
        "Low": ("#64748b", "#f8fafc", "#334155")
    }
    border_col, bg_col, text_col = color_map.get(comp_level, ("#64748b", "#f8fafc", "#334155"))

    st.markdown(
        f"""
        <div style="background: {bg_col}; border: 1px solid {border_col}; border-left: 6px solid {border_col}; border-radius: 8px; padding: 1.2rem; margin-bottom: 1.2rem;">
            <div style="display: flex; justify-content: space-between; align-items: baseline;">
                <h3 style="margin: 0; color: {text_col};">Candidate Fate: {t_cell}</h3>
                <span style="background: {border_col}; color: #ffffff; padding: 3px 10px; border-radius: 12px; font-weight: 600; font-size: 0.8rem;">
                    Compatibility: {comp_level}
                </span>
            </div>
            <p style="margin: 0.3rem 0; font-size: 0.92rem; color: #475569;">
                Lineage: <b>{lineage}</b> | Evaluation: <b>{status}</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if outcome.get("matrix_notes"):
        st.warning(outcome["matrix_notes"])

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### 🔬 Induction Signals Analysis")
        if outcome["matched_req"]:
            st.markdown(f"✅ **Supplied Required Signals:** {', '.join(outcome['matched_req'])}")
        if outcome["missing_req"]:
            st.markdown(f"⚠️ **Missing Required Signals:** `{', '.join(outcome['missing_req'])}`")
        if outcome["matched_opt"]:
            st.markdown(f"✨ **Supplied Optional Enhancers:** {', '.join(outcome['matched_opt'])}")

        st.markdown(f"**Documented Induction Summary:**")
        st.info(diff.get("conditions_summary") or "Standard differentiation media.")

    with c2:
        st.markdown("#### 🧪 Expected Molecular Markers & Pathways")
        st.markdown(f"**Biological Rationale & Mechanism:**")
        st.write(diff.get("evidence_notes") or "Curated experimental literature.")

        # Key markers
        markers = get_markers_for_cell(source_cell_id)
        if markers:
            target_markers = [m for m in markers if m.get("differentiation_stage") != "Undifferentiated"]
            if not target_markers:
                target_markers = markers[:4]
            marker_names = [f"**{m.get('gene_symbol') or m.get('marker_name')}** ({m.get('description', '')[:35]}...)" for m in target_markers[:4]]
            st.markdown(f"**Associated Markers:**<br>" + "<br>".join(marker_names), unsafe_allow_html=True)

    # Pathway diagram expander
    with st.expander(f"🕸️ View Molecular Pathway Diagram for {source_cell_id} ➔ {t_cell}", expanded=False):
        fig_p = create_pathway_diagram(
            source_cell=source_cell_id,
            target_cell=t_cell,
            signals=outcome["req_signals"] + outcome["opt_signals"],
            markers=get_markers_for_cell(source_cell_id)
        )
        st.plotly_chart(fig_p, use_container_width=True)

    # Reference citation
    if diff.get("ref_title"):
        st.markdown(
            f"<div style='font-size: 0.85rem; color: #64748b; margin-top: 0.5rem;'>"
            f"<b>Supporting Study:</b> <i>{diff.get('ref_title')}</i> ({diff.get('ref_authors', '')}, {diff.get('ref_year', '')}). "
            f"DOI: <a href='https://doi.org/{diff.get('ref_doi')}' target='_blank'>{diff.get('ref_doi')}</a>"
            f"</div>",
            unsafe_allow_html=True
        )
    st.markdown("---")
