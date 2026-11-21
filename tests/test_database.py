"""
test_database.py - Automated tests for SQLite database schema, operations, and integrity.
"""

import os
import sqlite3
import pytest
from database.database import (
    get_connection, init_db, get_database_stats,
    get_all_stem_cells, get_stem_cell, get_cell_lines,
    search_cell_lines, get_markers_for_cell, get_differentiation_records,
    get_protocols, get_protocol_by_id, get_protocol_steps, get_all_references,
    insert_cell_line
)

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_stemcell.db")


@pytest.fixture(scope="module")
def setup_test_db():
    """Create a temporary test database seeded with schema."""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    init_db(TEST_DB_PATH)

    # Seed minimal test data
    conn = get_connection(TEST_DB_PATH)
    conn.execute(
        """
        INSERT INTO stem_cells (cell_id, name, category, potency, species)
        VALUES ('ESC', 'Embryonic Stem Cell', 'Embryonic', 'Pluripotent', 'Homo sapiens');
        """
    )
    conn.execute(
        """
        INSERT INTO cell_lines (cell_id, cell_line_name, accession_number, species)
        VALUES ('ESC', 'H9', 'CVCL_9773', 'Homo sapiens');
        """
    )
    conn.commit()
    conn.close()

    yield TEST_DB_PATH

    # Teardown: handle Windows file locking gracefully
    import gc
    gc.collect()
    try:
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
    except Exception:
        pass


def test_database_init(setup_test_db):
    """Test that schema initializes all 10 core tables."""
    conn = get_connection(setup_test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    expected_tables = [
        "references", "stem_cells", "cell_lines", "markers",
        "cell_markers", "differentiation", "signals",
        "differentiation_signals", "protocols", "protocol_steps"
    ]
    for table in expected_tables:
        assert table in tables, f"Expected table '{table}' not found in database."


def test_stem_cell_retrieval(setup_test_db):
    """Test retrieving stem cell record by ID."""
    sc = get_stem_cell("ESC", db_path=setup_test_db)
    assert sc is not None
    assert sc["cell_id"] == "ESC"
    assert sc["potency"] == "Pluripotent"


def test_cell_line_search(setup_test_db):
    """Test searching cell lines by accession and name."""
    results = search_cell_lines("H9", db_path=setup_test_db)
    assert len(results) >= 1
    assert results[0]["accession_number"] == "CVCL_9773"

    results_acc = search_cell_lines("CVCL_9773", db_path=setup_test_db)
    assert len(results_acc) >= 1


def test_duplicate_prevention(setup_test_db):
    """Test that inserting a duplicate cell line accession number updates rather than duplicates."""
    insert_cell_line(
        cell_id="ESC",
        cell_line_name="H9 Updated",
        accession_number="CVCL_9773",
        db_path=setup_test_db
    )
    lines = get_cell_lines("ESC", db_path=setup_test_db)
    matching = [l for l in lines if l["accession_number"] == "CVCL_9773"]
    assert len(matching) == 1
    assert matching[0]["cell_line_name"] == "H9 Updated"


def test_dynamic_statistics(setup_test_db):
    """Test dynamic database statistics query."""
    stats = get_database_stats(setup_test_db)
    assert stats["total_stem_cells"] >= 1
    assert stats["total_cell_lines"] >= 1
