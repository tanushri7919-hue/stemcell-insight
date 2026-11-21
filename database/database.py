"""
database.py - Central database access layer for StemCell Insight.
Provides thread-safe SQLite connection management and parameterized query functions.
"""

import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

# Locate database file relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "stemcell.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Return an SQLite connection with Row factory and foreign keys enabled."""
    target_path = db_path or DB_PATH
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize database tables using schema.sql if they do not exist.
    Does not erase or recreate existing tables.
    """
    target_path = db_path or DB_PATH
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with get_connection(target_path) as conn:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.commit()


# ============================================================================
# Statistics & Overview
# ============================================================================

def get_database_stats(db_path: Optional[str] = None) -> Dict[str, int]:
    """Retrieve dynamic record counts across all core tables."""
    stats = {}
    tables = [
        ("stem_cells", "total_stem_cells"),
        ("cell_lines", "total_cell_lines"),
        ("differentiation", "total_differentiation"),
        ("markers", "total_markers"),
        ("signals", "total_signals"),
        ("protocols", "total_protocols"),
        ("references", "total_references"),
    ]
    with get_connection(db_path) as conn:
        for table, key in tables:
            try:
                cur = conn.execute(f"SELECT COUNT(*) FROM \"{table}\";")
                stats[key] = cur.fetchone()[0]
            except sqlite3.OperationalError:
                stats[key] = 0
    return stats


# ============================================================================
# References
# ============================================================================

def insert_reference(
    reference_id: str,
    title: str,
    authors: Optional[str] = None,
    publication_year: Optional[int] = None,
    journal: Optional[str] = None,
    DOI: Optional[str] = None,
    URL: Optional[str] = None,
    source_type: str = "Peer-reviewed Journal",
    db_path: Optional[str] = None
) -> None:
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO "references" (reference_id, title, authors, publication_year, journal, DOI, URL, source_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(reference_id) DO UPDATE SET
                title = excluded.title,
                authors = COALESCE(excluded.authors, "references".authors),
                publication_year = COALESCE(excluded.publication_year, "references".publication_year),
                journal = COALESCE(excluded.journal, "references".journal),
                DOI = COALESCE(excluded.DOI, "references".DOI),
                URL = COALESCE(excluded.URL, "references".URL),
                source_type = COALESCE(excluded.source_type, "references".source_type);
            """,
            (reference_id, title, authors, publication_year, journal, DOI, URL, source_type)
        )
        conn.commit()


def get_reference(reference_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        row = conn.execute(
            'SELECT * FROM "references" WHERE reference_id = ?;', (reference_id,)
        ).fetchone()
        return dict(row) if row else None


def get_all_references(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        rows = conn.execute(
            'SELECT * FROM "references" ORDER BY publication_year DESC, title ASC;'
        ).fetchall()
        return [dict(r) for r in rows]


# ============================================================================
# Stem Cells
# ============================================================================

def insert_stem_cell(
    cell_id: str,
    name: str,
    category: str,
    potency: str,
    species: str = "Homo sapiens",
    origin: Optional[str] = None,
    self_renewal: Optional[str] = None,
    description: Optional[str] = None,
    source: Optional[str] = None,
    reference_id: Optional[str] = None,
    db_path: Optional[str] = None
) -> None:
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO stem_cells (cell_id, name, category, potency, species, origin, self_renewal, description, source, reference_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(cell_id) DO UPDATE SET
                name = excluded.name,
                category = excluded.category,
                potency = excluded.potency,
                species = excluded.species,
                origin = excluded.origin,
                self_renewal = excluded.self_renewal,
                description = excluded.description,
                source = excluded.source,
                reference_id = excluded.reference_id;
            """,
            (cell_id, name, category, potency, species, origin, self_renewal, description, source, reference_id)
        )
        conn.commit()


def get_stem_cell(cell_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        row = conn.execute(
            """
            SELECT s.*, r.title AS ref_title, r.authors AS ref_authors, r.publication_year AS ref_year,
                   r.journal AS ref_journal, r.DOI AS ref_doi, r.URL AS ref_url
            FROM stem_cells s
            LEFT JOIN "references" r ON s.reference_id = r.reference_id
            WHERE s.cell_id = ?;
            """,
            (cell_id,)
        ).fetchone()
        return dict(row) if row else None


def get_all_stem_cells(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT s.*, r.title AS ref_title, r.DOI AS ref_doi
            FROM stem_cells s
            LEFT JOIN "references" r ON s.reference_id = r.reference_id
            ORDER BY s.name ASC;
            """
        ).fetchall()
        return [dict(r) for r in rows]


# ============================================================================
# Cell Lines
# ============================================================================

def insert_cell_line(
    cell_id: Optional[str],
    cell_line_name: str,
    accession_number: Optional[str] = None,
    synonyms: Optional[str] = None,
    species: str = "Homo sapiens",
    tissue_origin: Optional[str] = None,
    disease: Optional[str] = None,
    donor_information: Optional[str] = None,
    derivation_method: Optional[str] = None,
    characteristics: Optional[str] = None,
    source_database: str = "Cellosaurus",
    reference_id: Optional[str] = None,
    db_path: Optional[str] = None
) -> int:
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO cell_lines (
                cell_id, cell_line_name, accession_number, synonyms, species,
                tissue_origin, disease, donor_information, derivation_method,
                characteristics, source_database, reference_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(accession_number) DO UPDATE SET
                cell_id = COALESCE(excluded.cell_id, cell_lines.cell_id),
                cell_line_name = excluded.cell_line_name,
                synonyms = COALESCE(excluded.synonyms, cell_lines.synonyms),
                species = excluded.species,
                tissue_origin = COALESCE(excluded.tissue_origin, cell_lines.tissue_origin),
                disease = COALESCE(excluded.disease, cell_lines.disease),
                donor_information = COALESCE(excluded.donor_information, cell_lines.donor_information),
                derivation_method = COALESCE(excluded.derivation_method, cell_lines.derivation_method),
                characteristics = COALESCE(excluded.characteristics, cell_lines.characteristics),
                reference_id = COALESCE(excluded.reference_id, cell_lines.reference_id);
            """,
            (
                cell_id, cell_line_name, accession_number, synonyms, species,
                tissue_origin, disease, donor_information, derivation_method,
                characteristics, source_database, reference_id
            )
        )
        conn.commit()
        return cur.lastrowid


def get_cell_lines(cell_id: Optional[str] = None, limit: int = 200, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        if cell_id:
            rows = conn.execute(
                """
                SELECT cl.*, sc.name AS stem_cell_name, sc.category,
                       r.title AS ref_title, r.DOI AS ref_doi
                FROM cell_lines cl
                LEFT JOIN stem_cells sc ON cl.cell_id = sc.cell_id
                LEFT JOIN "references" r ON cl.reference_id = r.reference_id
                WHERE cl.cell_id = ?
                ORDER BY cl.cell_line_name ASC LIMIT ?;
                """,
                (cell_id, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT cl.*, sc.name AS stem_cell_name, sc.category,
                       r.title AS ref_title, r.DOI AS ref_doi
                FROM cell_lines cl
                LEFT JOIN stem_cells sc ON cl.cell_id = sc.cell_id
                LEFT JOIN "references" r ON cl.reference_id = r.reference_id
                ORDER BY cl.cell_line_name ASC LIMIT ?;
                """,
                (limit,)
            ).fetchall()
        return [dict(r) for r in rows]


def get_cell_line_by_accession(accession: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        row = conn.execute(
            """
            SELECT cl.*, sc.name AS stem_cell_name, sc.category,
                   r.title AS ref_title, r.authors AS ref_authors, r.publication_year AS ref_year,
                   r.journal AS ref_journal, r.DOI AS ref_doi, r.URL AS ref_url
            FROM cell_lines cl
            LEFT JOIN stem_cells sc ON cl.cell_id = sc.cell_id
            LEFT JOIN "references" r ON cl.reference_id = r.reference_id
            WHERE cl.accession_number = ?;
            """,
            (accession,)
        ).fetchone()
        return dict(row) if row else None


def search_cell_lines(query: str, species: Optional[str] = None, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    pattern = f"%{query}%"
    with get_connection(db_path) as conn:
        if species and species != "All":
            rows = conn.execute(
                """
                SELECT cl.*, sc.name AS stem_cell_name, sc.category
                FROM cell_lines cl
                LEFT JOIN stem_cells sc ON cl.cell_id = sc.cell_id
                WHERE (cl.cell_line_name LIKE ? OR cl.accession_number LIKE ? OR cl.synonyms LIKE ? OR cl.tissue_origin LIKE ?)
                  AND cl.species LIKE ?
                ORDER BY cl.cell_line_name ASC LIMIT 100;
                """,
                (pattern, pattern, pattern, pattern, f"%{species}%")
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT cl.*, sc.name AS stem_cell_name, sc.category
                FROM cell_lines cl
                LEFT JOIN stem_cells sc ON cl.cell_id = sc.cell_id
                WHERE cl.cell_line_name LIKE ? OR cl.accession_number LIKE ? OR cl.synonyms LIKE ? OR cl.tissue_origin LIKE ?
                ORDER BY cl.cell_line_name ASC LIMIT 100;
                """,
                (pattern, pattern, pattern, pattern)
            ).fetchall()
        return [dict(r) for r in rows]


# ============================================================================
# Markers
# ============================================================================

def insert_marker(
    marker_name: str,
    gene_symbol: Optional[str] = None,
    marker_type: Optional[str] = None,
    description: Optional[str] = None,
    reference_id: Optional[str] = None,
    db_path: Optional[str] = None
) -> int:
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO markers (marker_name, gene_symbol, marker_type, description, reference_id)
            VALUES (?, ?, ?, ?, ?);
            """,
            (marker_name, gene_symbol, marker_type, description, reference_id)
        )
        conn.commit()
        return cur.lastrowid


def link_cell_marker(
    cell_id: str,
    marker_id: int,
    association: str,
    differentiation_stage: str = "Undifferentiated",
    reference_id: Optional[str] = None,
    db_path: Optional[str] = None
) -> None:
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO cell_markers (cell_id, marker_id, association, differentiation_stage, reference_id)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(cell_id, marker_id, differentiation_stage) DO UPDATE SET
                association = excluded.association,
                reference_id = excluded.reference_id;
            """,
            (cell_id, marker_id, association, differentiation_stage, reference_id)
        )
        conn.commit()


def get_markers_for_cell(cell_id: str, stage: Optional[str] = None, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        if stage:
            rows = conn.execute(
                """
                SELECT m.*, cm.association, cm.differentiation_stage,
                       r.title AS ref_title, r.DOI AS ref_doi
                FROM cell_markers cm
                JOIN markers m ON cm.marker_id = m.marker_id
                LEFT JOIN "references" r ON cm.reference_id = r.reference_id
                WHERE cm.cell_id = ? AND cm.differentiation_stage = ?
                ORDER BY cm.association DESC, m.gene_symbol ASC;
                """,
                (cell_id, stage)
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT m.*, cm.association, cm.differentiation_stage,
                       r.title AS ref_title, r.DOI AS ref_doi
                FROM cell_markers cm
                JOIN markers m ON cm.marker_id = m.marker_id
                LEFT JOIN "references" r ON cm.reference_id = r.reference_id
                WHERE cm.cell_id = ?
                ORDER BY cm.differentiation_stage ASC, cm.association DESC, m.gene_symbol ASC;
                """,
                (cell_id,)
            ).fetchall()
        return [dict(r) for r in rows]


def get_all_markers(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT m.*, r.title AS ref_title, r.DOI AS ref_doi
            FROM markers m
            LEFT JOIN "references" r ON m.reference_id = r.reference_id
            ORDER BY m.gene_symbol ASC, m.marker_name ASC;
            """
        ).fetchall()
        return [dict(r) for r in rows]


# ============================================================================
# Differentiation & Signaling
# ============================================================================

def insert_differentiation(
    source_cell_id: str,
    target_cell: str,
    lineage: str,
    conditions_summary: Optional[str] = None,
    evidence_type: str = "Experimental",
    evidence_notes: Optional[str] = None,
    reference_id: Optional[str] = None,
    db_path: Optional[str] = None
) -> int:
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO differentiation (source_cell_id, target_cell, lineage, conditions_summary, evidence_type, evidence_notes, reference_id)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (source_cell_id, target_cell, lineage, conditions_summary, evidence_type, evidence_notes, reference_id)
        )
        conn.commit()
        return cur.lastrowid


def insert_signal(
    signal_name: str,
    signal_type: str,
    pathway: Optional[str] = None,
    biological_role: Optional[str] = None,
    effect: Optional[str] = None,
    reference_id: Optional[str] = None,
    db_path: Optional[str] = None
) -> int:
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO signals (signal_name, signal_type, pathway, biological_role, effect, reference_id)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(signal_name) DO UPDATE SET
                signal_type = excluded.signal_type,
                pathway = COALESCE(excluded.pathway, signals.pathway),
                biological_role = COALESCE(excluded.biological_role, signals.biological_role),
                effect = COALESCE(excluded.effect, signals.effect),
                reference_id = COALESCE(excluded.reference_id, signals.reference_id);
            """,
            (signal_name, signal_type, pathway, biological_role, effect, reference_id)
        )
        conn.commit()
        # Retrieve id in case conflict resolved
        row = conn.execute("SELECT signal_id FROM signals WHERE signal_name = ?;", (signal_name,)).fetchone()
        return row[0] if row else cur.lastrowid


def link_differentiation_signal(
    differentiation_id: int,
    signal_id: int,
    role: str,
    concentration: Optional[str] = None,
    treatment_duration: Optional[str] = None,
    reference_id: Optional[str] = None,
    db_path: Optional[str] = None
) -> None:
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO differentiation_signals (differentiation_id, signal_id, role, concentration, treatment_duration, reference_id)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(differentiation_id, signal_id, role) DO UPDATE SET
                concentration = excluded.concentration,
                treatment_duration = excluded.treatment_duration,
                reference_id = excluded.reference_id;
            """,
            (differentiation_id, signal_id, role, concentration, treatment_duration, reference_id)
        )
        conn.commit()


def get_differentiation_records(source_cell_id: Optional[str] = None, lineage: Optional[str] = None, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        query = """
            SELECT d.*, sc.name AS source_cell_name, sc.category AS source_category,
                   r.title AS ref_title, r.authors AS ref_authors, r.publication_year AS ref_year,
                   r.journal AS ref_journal, r.DOI AS ref_doi, r.URL AS ref_url
            FROM differentiation d
            JOIN stem_cells sc ON d.source_cell_id = sc.cell_id
            LEFT JOIN "references" r ON d.reference_id = r.reference_id
            WHERE 1=1
        """
        params = []
        if source_cell_id:
            query += " AND d.source_cell_id = ?"
            params.append(source_cell_id)
        if lineage:
            query += " AND d.lineage = ?"
            params.append(lineage)
        query += " ORDER BY d.lineage ASC, d.target_cell ASC;"
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def get_differentiation_signals(differentiation_id: int, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT ds.*, s.signal_name, s.signal_type, s.pathway, s.biological_role, s.effect,
                   r.title AS ref_title, r.DOI AS ref_doi
            FROM differentiation_signals ds
            JOIN signals s ON ds.signal_id = s.signal_id
            LEFT JOIN "references" r ON ds.reference_id = r.reference_id
            WHERE ds.differentiation_id = ?
            ORDER BY ds.role ASC, s.signal_name ASC;
            """,
            (differentiation_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_all_signals(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT s.*, r.title AS ref_title, r.DOI AS ref_doi
            FROM signals s
            LEFT JOIN "references" r ON s.reference_id = r.reference_id
            ORDER BY s.pathway ASC, s.signal_name ASC;
            """
        ).fetchall()
        return [dict(r) for r in rows]


# ============================================================================
# Protocols
# ============================================================================

def insert_protocol(
    protocol_name: str,
    source_cell: str,
    target_cell: str,
    medium: Optional[str] = None,
    growth_factors: Optional[str] = None,
    small_molecules: Optional[str] = None,
    duration: Optional[str] = None,
    reported_efficiency: Optional[str] = None,
    efficiency_method: Optional[str] = None,
    validation_markers: Optional[str] = None,
    functional_validation: Optional[str] = None,
    reference_id: Optional[str] = None,
    db_path: Optional[str] = None
) -> int:
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO protocols (
                protocol_name, source_cell, target_cell, medium, growth_factors,
                small_molecules, duration, reported_efficiency, efficiency_method,
                validation_markers, functional_validation, reference_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                protocol_name, source_cell, target_cell, medium, growth_factors,
                small_molecules, duration, reported_efficiency, efficiency_method,
                validation_markers, functional_validation, reference_id
            )
        )
        conn.commit()
        return cur.lastrowid


def insert_protocol_step(
    protocol_id: int,
    step_number: int,
    procedure: str,
    reagent: Optional[str] = None,
    concentration: Optional[str] = None,
    duration: Optional[str] = None,
    notes: Optional[str] = None,
    db_path: Optional[str] = None
) -> int:
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO protocol_steps (protocol_id, step_number, procedure, reagent, concentration, duration, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (protocol_id, step_number, procedure, reagent, concentration, duration, notes)
        )
        conn.commit()
        return cur.lastrowid


def get_protocols(
    source_cell: Optional[str] = None,
    target_cell: Optional[str] = None,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        query = """
            SELECT p.*,
                   r.title AS ref_title, r.authors AS ref_authors, r.publication_year AS ref_year,
                   r.journal AS ref_journal, r.DOI AS ref_doi, r.URL AS ref_url
            FROM protocols p
            LEFT JOIN "references" r ON p.reference_id = r.reference_id
            WHERE 1=1
        """
        params = []
        if source_cell and source_cell != "All":
            query += " AND p.source_cell LIKE ?"
            params.append(f"%{source_cell}%")
        if target_cell and target_cell != "All":
            query += " AND p.target_cell LIKE ?"
            params.append(f"%{target_cell}%")
        query += " ORDER BY p.protocol_name ASC;"
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def get_protocol_by_id(protocol_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        row = conn.execute(
            """
            SELECT p.*,
                   r.title AS ref_title, r.authors AS ref_authors, r.publication_year AS ref_year,
                   r.journal AS ref_journal, r.DOI AS ref_doi, r.URL AS ref_url
            FROM protocols p
            LEFT JOIN "references" r ON p.reference_id = r.reference_id
            WHERE p.protocol_id = ?;
            """,
            (protocol_id,)
        ).fetchone()
        return dict(row) if row else None


def get_protocol_steps(protocol_id: int, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT * FROM protocol_steps
            WHERE protocol_id = ?
            ORDER BY step_number ASC;
            """,
            (protocol_id,)
        ).fetchall()
        return [dict(r) for r in rows]
