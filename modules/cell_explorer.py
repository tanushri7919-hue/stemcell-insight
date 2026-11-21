"""
cell_explorer.py - Searchable biological interface for exploring stem-cell profiles
and authenticated Cellosaurus cell-line records.
"""

import streamlit as st
from database.database import (
    get_all_stem_cells, get_stem_cell, get_cell_lines,
    get_cell_line_by_accession, search_cell_lines,
    get_markers_for_cell, get_differentiation_records
)
from utils.visualizations import create_marker_profile_chart, create_lineage_network


def render_cell_explorer():
    st.markdown("## 🔬 Cell Explorer")
    st.markdown(
        "Explore biological characteristics, potency, markers, and differentiation capabilities "
        "across the five primary stem-cell categories, or search authenticated cell lines."
    )

    tab1, tab2 = st.tabs(["🧬 Stem Cell Profiles", "🧫 Cell-Line Database (Cellosaurus)"])

    # =========================================================================
    # TAB 1: Stem Cell Profiles
    # =========================================================================
    with tab1:
        cells = get_all_stem_cells()
        cell_options = {c["cell_id"]: f"{c['name']} ({c['cell_id']})" for c in cells}

        selected_cell_id = st.selectbox(
            "Select Stem-Cell Category:",
            options=list(cell_options.keys()),
            format_func=lambda cid: cell_options[cid],
            key="profile_selector"
        )

        if selected_cell_id:
            profile = get_stem_cell(selected_cell_id)
            if profile:
                _render_stem_cell_profile(profile)

    # =========================================================================
    # TAB 2: Cell-Line Database
    # =========================================================================
    with tab2:
        _render_cell_line_explorer()


def _render_stem_cell_profile(profile: dict):
    """Render a comprehensive profile card for a stem-cell category."""
    cid = profile["cell_id"]
    name = profile["name"]
    cat = profile["category"]
    potency = profile["potency"]
    species = profile["species"]

    # Header Card
    st.markdown(
        f"""
        <div style="background: #ffffff; border: 1px solid #cbd5e1; border-left: 6px solid #0284c7; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: baseline;">
                <h3 style="margin: 0; color: #1e3a8a;">{name}</h3>
                <span style="background: #e0f2fe; color: #0369a1; padding: 4px 12px; border-radius: 16px; font-weight: 600; font-size: 0.85rem;">
                    {potency} Potency
                </span>
            </div>
            <p style="color: #64748b; font-size: 0.95rem; margin: 0.2rem 0 0.8rem 0;">
                Category: <b>{cat}</b> | Species: <b>{species}</b> | Primary Source: <i>{profile.get('source') or 'Curated Literature'}</i>
            </p>
            <p style="color: #334155; line-height: 1.6; margin: 0;">
                {profile.get('description') or 'No description recorded.'}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📍 Biological Origin & Tissue")
        st.info(profile.get("origin") or "Origin details not reported.")

    with col2:
        st.markdown("#### 🔄 Self-Renewal & Propagation")
        st.success(profile.get("self_renewal") or "Self-renewal details not reported.")

    st.markdown("---")

    # Molecular Markers Section
    st.markdown("#### 🏷️ Characteristic Molecular Markers")
    markers = get_markers_for_cell(cid)

    if markers:
        m_cols = st.columns(3)
        for idx, m in enumerate(markers):
            with m_cols[idx % 3]:
                assoc = m.get("association", "Positive")
                badge_color = "#dcfce7" if "Positive" in assoc or "Master" in assoc else "#fee2e2"
                text_color = "#166534" if "Positive" in assoc or "Master" in assoc else "#991b1b"

                st.markdown(
                    f"""
                    <div style="border: 1px solid #e2e8f0; border-radius: 6px; padding: 0.8rem; margin-bottom: 0.8rem; background: #fafafa;">
                        <div style="display: flex; justify-content: space-between;">
                            <strong style="color: #0f172a;">{m.get('gene_symbol') or m.get('marker_name')}</strong>
                            <span style="background: {badge_color}; color: {text_color}; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">
                                {assoc}
                            </span>
                        </div>
                        <div style="color: #64748b; font-size: 0.8rem; margin: 0.2rem 0;">
                            Name: {m.get('marker_name')} | Class: {m.get('marker_type') or 'N/A'}
                        </div>
                        <div style="font-size: 0.85rem; color: #334155;">
                            {m.get('description') or ''}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Plot breakdown
        with st.expander("📊 View Marker Class Distribution Chart", expanded=False):
            fig_m = create_marker_profile_chart(markers)
            st.plotly_chart(fig_m, use_container_width=True)
    else:
        st.write("No markers currently mapped for this category.")

    st.markdown("---")

    # Known Differentiation Fates
    st.markdown("#### 🌿 Documented Differentiation Pathways & Cell Fates")
    diff_records = get_differentiation_records(source_cell_id=cid)

    if diff_records:
        for d in diff_records:
            with st.expander(f"➔ {d.get('target_cell')} ({d.get('lineage')})", expanded=False):
                st.markdown(f"**Induction Conditions:** {d.get('conditions_summary') or 'Not reported'}")
                st.markdown(f"**Evidence Details:** {d.get('evidence_notes') or 'Not reported'}")
                if d.get("ref_title"):
                    st.markdown(f"**Supporting Reference:** *{d.get('ref_title')}* ({d.get('ref_authors', '')}, {d.get('ref_year', '')}). DOI: [{d.get('ref_doi')}](https://doi.org/{d.get('ref_doi')})")
    else:
        st.write("No differentiation records currently mapped.")

    # Supporting Reference for Profile
    if profile.get("ref_title"):
        st.markdown("---")
        st.markdown("#### 📚 Foundational Scientific Reference")
        st.markdown(
            f"**{profile.get('ref_title')}**<br>"
            f"Authors: {profile.get('ref_authors', 'Not reported')}<br>"
            f"Journal: *{profile.get('ref_journal', 'Not reported')}* ({profile.get('ref_year', 'N/A')})<br>"
            f"DOI: [{profile.get('ref_doi', 'N/A')}](https://doi.org/{profile.get('ref_doi')})",
            unsafe_allow_html=True
        )


def _render_cell_line_explorer():
    """Render searchable interface for Cellosaurus cell-line records."""
    st.markdown("### 🔍 Cell-Line Registry Search")

    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input(
            "Search by Cell-Line Name, Accession Number (e.g., CVCL_9773), Synonym, or Tissue Origin:",
            placeholder="e.g., H9, WTC-11, CVCL_9771, Bone marrow...",
            key="cell_line_search"
        )
    with col2:
        species_filter = st.selectbox(
            "Species Filter:",
            options=["All", "Homo sapiens", "Mus musculus"],
            key="species_filter"
        )

    # Perform search or retrieve all
    if search_query.strip():
        lines = search_cell_lines(search_query.strip(), species=species_filter)
        st.caption(f"Found {len(lines)} matching cell lines.")
    else:
        lines = get_cell_lines(limit=50)
        st.caption(f"Displaying {len(lines)} registered cell lines.")

    if not lines:
        st.warning("No cell lines matched your search criteria.")
        return

    # Cell lines cards
    for cl in lines:
        name = cl.get("cell_line_name")
        acc = cl.get("accession_number") or "N/A"
        species = cl.get("species") or "Homo sapiens"
        tissue = cl.get("tissue_origin") or "Not reported"
        disease = cl.get("disease") or "None reported"
        synonyms = cl.get("synonyms") or "None reported"
        donor = cl.get("donor_information") or "Not reported"
        derivation = cl.get("derivation_method") or "Not reported"
        characteristics = cl.get("characteristics") or "None recorded"
        stem_type = cl.get("stem_cell_name") or cl.get("cell_id") or "Unclassified"

        with st.expander(f"🧫 {name}  [{acc}]  —  {stem_type} ({species})", expanded=False):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Cell-Line Name:** {name}")
                st.markdown(f"**Cellosaurus Accession:** `{acc}`")
                st.markdown(f"**Stem-Cell Category:** {stem_type}")
                st.markdown(f"**Species of Origin:** {species}")
                st.markdown(f"**Synonyms / Aliases:** {synonyms}")
            with c2:
                st.markdown(f"**Tissue / Anatomical Origin:** {tissue}")
                st.markdown(f"**Disease Annotation:** {disease}")
                st.markdown(f"**Donor Information:** {donor}")
                st.markdown(f"**Derivation Method:** {derivation}")

            st.markdown(f"**Biological Characteristics & External Links:**")
            st.info(characteristics)

            # Cellosaurus official link
            if acc and acc.startswith("CVCL_"):
                st.markdown(
                    f"🔗 **Cellosaurus Record:** [https://www.cellosaurus.org/{acc}](https://www.cellosaurus.org/{acc})"
                )
