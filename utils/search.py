"""
search.py - Search and information retrieval engine for StemCell Insight.
Provides keyword matching, biological synonym expansion, and TF-IDF text similarity.
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from database.database import get_connection

# Comprehensive biological synonym dictionary for stem cell biology
BIOLOGICAL_SYNONYMS: Dict[str, Set[str]] = {
    "esc": {"embryonic stem cell", "hesc", "embryonic stem cells", "embryonic"},
    "hesc": {"embryonic stem cell", "esc", "human embryonic stem cell"},
    "ipsc": {"induced pluripotent stem cell", "hipsc", "induced pluripotent", "ipscs", "yamanaka factors"},
    "hipsc": {"induced pluripotent stem cell", "ipsc", "human induced pluripotent stem cell"},
    "msc": {"mesenchymal stem cell", "mesenchymal stromal cell", "marrow stromal cell", "multipotent stromal cell", "mscs"},
    "hsc": {"hematopoietic stem cell", "blood stem cell", "hematopoietic progenitor", "cd34+", "hscs"},
    "nsc": {"neural stem cell", "neural progenitor", "neuroepithelial", "nscs", "npc", "neural precursor"},
    "pluripotency": {"pluripotent", "oct4", "sox2", "nanog", "self-renewal", "pou5f1"},
    "oct4": {"pou5f1", "oct-4", "oct3/4"},
    "pou5f1": {"oct4", "oct-4", "oct3/4"},
    "sox2": {"sry-box 2", "sox-2"},
    "nanog": {"homeobox protein nanog"},
    "cd73": {"nt5e", "ecto-5'-nucleotidase"},
    "cd90": {"thy1", "thy-1"},
    "cd105": {"eng", "endoglin"},
    "cd34": {"hematopoietic progenitor cell antigen cd34"},
    "runx2": {"cbfa1", "aml3", "runt-related transcription factor 2"},
    "alpl": {"alkaline phosphatase", "alp", "tnap"},
    "osteocalcin": {"bglap", "bone gamma-carboxyglutamate"},
    "pparg": {"ppar-gamma", "ppargamma", "peroxisome proliferator activated receptor gamma"},
    "cebpa": {"c/ebp-alpha", "c/ebp alpha"},
    "fabp4": {"ap2", "adipocyte protein 2"},
    "sox9": {"sry-box 9", "sox-9"},
    "col2a1": {"collagen type ii", "collagen 2", "type ii collagen"},
    "tuj1": {"tubb3", "beta-iii-tubulin", "beta-3-tubulin"},
    "map2": {"microtubule-associated protein 2"},
    "tnnt2": {"cardiac troponin t", "ctnt", "troponin t"},
    "pdx1": {"ipf1", "pancreatic and duodenal homeobox 1"},
    "bmp": {"bone morphogenetic protein", "bmp2", "bmp4", "smad1/5/8"},
    "wnt": {"beta-catenin", "canonical wnt", "chir99021", "gsk3"},
    "chir99021": {"chir", "gsk3 inhibitor", "wnt activator"},
    "sb431542": {"alk5 inhibitor", "tgf-beta inhibitor", "dual smad"},
    "iwp2": {"iwp-2", "porcupine inhibitor", "wnt inhibitor"},
    "osteogenesis": {"osteoblast", "bone", "mineralization", "runx2", "alizarin red"},
    "adipogenesis": {"adipocyte", "fat", "lipid", "oil red o", "pparg"},
    "chondrogenesis": {"chondrocyte", "cartilage", "sox9", "alcian blue", "micromass"},
    "cardiogenesis": {"cardiomyocyte", "heart", "cardiac", "beating", "troponin"}
}


def expand_query_terms(query: str) -> List[str]:
    """Tokenize query and append biologically related terms and synonyms."""
    clean_q = re.sub(r"[^\w\s\-/]", " ", query.lower())
    raw_tokens = clean_q.split()
    tokens = set(raw_tokens)
    # Add singular form for simple plurals (e.g. escs -> esc, ipscs -> ipsc, cells -> cell)
    for t in raw_tokens:
        if t.endswith("s") and len(t) > 3:
            tokens.add(t[:-1])

    expanded_terms = set(tokens)

    for token in tokens:
        if token in BIOLOGICAL_SYNONYMS:
            expanded_terms.update(BIOLOGICAL_SYNONYMS[token])
        for key, syns in BIOLOGICAL_SYNONYMS.items():
            if token == key or token in syns:
                expanded_terms.add(key)
                expanded_terms.update(syns)

    return list(expanded_terms)


def search_all_entities(query: str, db_path: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """Unified multi-table search across stem cells, cell lines, differentiation,
    markers, signals, protocols, and scientific references.
    """
    if not query or not query.strip():
        return {
            "stem_cells": [],
            "cell_lines": [],
            "differentiation": [],
            "markers": [],
            "signals": [],
            "protocols": [],
            "references": [],
        }

    expanded_terms = expand_query_terms(query)
    pattern = f"%{query.strip()}%"

    results: Dict[str, List[Dict[str, Any]]] = {}

    with get_connection(db_path) as conn:
        # 1. Stem Cells
        sc_rows = conn.execute(
            """
            SELECT * FROM stem_cells
            WHERE name LIKE ? OR category LIKE ? OR potency LIKE ? OR description LIKE ?;
            """,
            (pattern, pattern, pattern, pattern)
        ).fetchall()
        results["stem_cells"] = [dict(r) for r in sc_rows]

        # 2. Cell Lines
        cl_rows = conn.execute(
            """
            SELECT cl.*, sc.name AS stem_cell_name, sc.category
            FROM cell_lines cl
            LEFT JOIN stem_cells sc ON cl.cell_id = sc.cell_id
            WHERE cl.cell_line_name LIKE ? OR cl.accession_number LIKE ?
               OR cl.synonyms LIKE ? OR cl.characteristics LIKE ? OR cl.tissue_origin LIKE ?
            LIMIT 50;
            """,
            (pattern, pattern, pattern, pattern, pattern)
        ).fetchall()
        results["cell_lines"] = [dict(r) for r in cl_rows]

        # 3. Differentiation Records
        diff_rows = conn.execute(
            """
            SELECT d.*, sc.name AS source_cell_name
            FROM differentiation d
            JOIN stem_cells sc ON d.source_cell_id = sc.cell_id
            WHERE d.target_cell LIKE ? OR d.lineage LIKE ? OR d.conditions_summary LIKE ?
               OR d.evidence_notes LIKE ?;
            """,
            (pattern, pattern, pattern, pattern)
        ).fetchall()
        results["differentiation"] = [dict(r) for r in diff_rows]

        # 4. Markers
        m_rows = conn.execute(
            """
            SELECT * FROM markers
            WHERE marker_name LIKE ? OR gene_symbol LIKE ? OR marker_type LIKE ? OR description LIKE ?;
            """,
            (pattern, pattern, pattern, pattern)
        ).fetchall()
        results["markers"] = [dict(r) for r in m_rows]

        # 5. Signals
        sig_rows = conn.execute(
            """
            SELECT * FROM signals
            WHERE signal_name LIKE ? OR pathway LIKE ? OR biological_role LIKE ? OR effect LIKE ?;
            """,
            (pattern, pattern, pattern, pattern)
        ).fetchall()
        results["signals"] = [dict(r) for r in sig_rows]

        # 6. Protocols
        proto_rows = conn.execute(
            """
            SELECT p.*, r.title AS ref_title, r.DOI AS ref_doi
            FROM protocols p
            LEFT JOIN "references" r ON p.reference_id = r.reference_id
            WHERE p.protocol_name LIKE ? OR p.source_cell LIKE ? OR p.target_cell LIKE ?
               OR p.growth_factors LIKE ? OR p.small_molecules LIKE ? OR p.validation_markers LIKE ?;
            """,
            (pattern, pattern, pattern, pattern, pattern, pattern)
        ).fetchall()
        results["protocols"] = [dict(r) for r in proto_rows]

        # 7. References
        ref_rows = conn.execute(
            """
            SELECT * FROM "references"
            WHERE title LIKE ? OR authors LIKE ? OR journal LIKE ? OR DOI LIKE ? OR reference_id LIKE ?
            LIMIT 50;
            """,
            (pattern, pattern, pattern, pattern, pattern)
        ).fetchall()
        results["references"] = [dict(r) for r in ref_rows]

    return results


def rank_text_similarity(query: str, corpus: List[str], top_n: int = 5) -> List[Tuple[int, float]]:
    """Rank documents against query using Scikit-learn TF-IDF cosine similarity."""
    if not corpus or not query.strip():
        return []

    documents = [query] + corpus
    try:
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(documents)
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        ranked_indices = cosine_sim.argsort()[::-1][:top_n]
        return [(idx, float(cosine_sim[idx])) for idx in ranked_indices if cosine_sim[idx] > 0.05]
    except Exception:
        # Fallback to keyword matching if TF-IDF encounter edge cases
        return []
