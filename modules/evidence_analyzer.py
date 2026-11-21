"""
evidence_analyzer.py - Evidence & Scientific Reporting Completeness Inspector.
Evaluates reporting thoroughness across experimental dimensions,
highlights missing information, and links findings to verifiable literature.
"""

import streamlit as st
import pandas as pd
from database.database import get_protocols, get_differentiation_records
from utils.data_validation import evaluate_evidence_completeness


def render_evidence_analyzer():
    st.markdown("## 🔍 Evidence Analyser")
    st.markdown(
        "Inspect the reporting completeness of published stem-cell differentiation studies. "
        "Review whether critical experimental parameters—such as reagent concentrations, "
        "treatment durations, validation markers, functional assays, and controls—are explicitly documented."
    )

    # Scientific Integrity Alert
    st.markdown(
        """
        <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-left: 4px solid #64748b; border-radius: 6px; padding: 0.9rem 1.2rem; margin-bottom: 1.5rem; font-size: 0.88rem; color: #334155;">
            <b>Important Methodological Distinction:</b> The <b>Evidence Completeness Score</b> assesses whether experimental details were <i>explicitly reported</i> in the publication or database record. A missing field indicates that the parameter was <b>'Not reported'</b>, which must <i>not</i> be interpreted as proof that the assay was not performed. Furthermore, this score is a measure of documentation completeness, not an empirical guarantee of biological reproducibility.
        </div>
        """,
        unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(["📋 Protocol Completeness Audits", "🌿 Differentiation Lineage Audits"])

    # =========================================================================
    # TAB 1: Protocol Completeness
    # =========================================================================
    with tab1:
        protocols = get_protocols()
        p_dict = {p["protocol_id"]: f"{p['protocol_name']}  ({p['source_cell']} ➔ {p['target_cell']})" for p in protocols}

        sel_pid = st.selectbox(
            "Select Protocol to Inspect Evidence Completeness:",
            options=list(p_dict.keys()),
            format_func=lambda pid: p_dict[pid],
            key="ev_proto_select"
        )

        if sel_pid:
            proto = next(p for p in protocols if p["protocol_id"] == sel_pid)
            eval_res = evaluate_evidence_completeness(proto, record_type="protocol")

            _render_completeness_report(proto["protocol_name"], eval_res, proto)

    # =========================================================================
    # TAB 2: Differentiation Completeness
    # =========================================================================
    with tab2:
        diffs = get_differentiation_records()
        d_dict = {d["differentiation_id"]: f"{d['source_cell_name']} ➔ {d['target_cell']} ({d['lineage']})" for d in diffs}

        sel_did = st.selectbox(
            "Select Differentiation Record to Audit:",
            options=list(d_dict.keys()),
            format_func=lambda did: d_dict[did],
            key="ev_diff_select"
        )

        if sel_did:
            diff_rec = next(d for d in diffs if d["differentiation_id"] == sel_did)
            eval_res = evaluate_evidence_completeness(diff_rec, record_type="differentiation")

            _render_completeness_report(f"{diff_rec['source_cell_name']} ➔ {diff_rec['target_cell']}", eval_res, diff_rec)


def _render_completeness_report(title: str, eval_res: dict, source_record: dict):
    """Render a structured completeness audit card with breakdown and progress bar."""
    score = eval_res["score"]
    total = eval_res["total_criteria"]
    satisfied = eval_res["satisfied_criteria"]

    # Color code
    if score >= 80:
        bar_color = "#16a34a"
        rating = "Comprehensive Experimental Documentation"
    elif score >= 60:
        bar_color = "#d97706"
        rating = "Moderate Reporting Completeness"
    else:
        bar_color = "#dc2626"
        rating = "Sparse / Incomplete Reporting"

    st.markdown(
        f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.5rem; margin-top: 1rem; margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: baseline;">
                <h3 style="margin: 0; color: #0f172a;">{title}</h3>
                <span style="font-size: 1.4rem; font-weight: 700; color: {bar_color};">
                    {score}%
                </span>
            </div>
            <div style="margin: 0.5rem 0 0.8rem 0; color: #64748b; font-size: 0.9rem;">
                Status: <b>{rating}</b> ({satisfied} of {total} experimental criteria verified)
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.progress(score / 100.0)

    # Criteria Grid
    st.markdown("#### 📋 Experimental Reporting Dimensions Audit")

    crit_df = pd.DataFrame(eval_res["criteria"])
    crit_df["Status"] = crit_df["present"].apply(lambda p: "✅ Reported" if p else "❌ Not reported")
    crit_df = crit_df.rename(columns={"name": "Reporting Criterion", "value": "Extracted Evidence / Value", "weight": "Weight"})

    st.dataframe(
        crit_df[["Reporting Criterion", "Status", "Extracted Evidence / Value"]],
        use_container_width=True,
        hide_index=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### ✅ Explicitly Documented Parameters")
        if eval_res["present_items"]:
            for item in eval_res["present_items"]:
                st.markdown(f"- **{item}**")
        else:
            st.write("None verified.")

    with col2:
        st.markdown("##### ⚠️ Missing or Incompletely Reported Parameters")
        if eval_res["missing_items"]:
            for item in eval_res["missing_items"]:
                st.markdown(f"- <span style='color: #b91c1c;'><b>{item}</b> (Marked as 'Not reported')</span>", unsafe_allow_html=True)
        else:
            st.success("All standard reporting dimensions are present in this record!")

    # Provenance citation
    st.markdown("---")
    st.markdown("#### 📚 Curated Literature Provenance")
    doi = source_record.get("ref_doi") or source_record.get("DOI")
    doi_link = f"https://doi.org/{doi}" if doi else "#"
    st.markdown(
        f"**Publication:** {source_record.get('ref_title') or 'Curated Protocol Record'}<br>"
        f"**Journal/Source:** {source_record.get('ref_journal') or 'Scientific Peer-Reviewed Literature'}<br>"
        f"**Permanent DOI:** [{doi or 'Not reported'}]({doi_link})",
        unsafe_allow_html=True
    )
