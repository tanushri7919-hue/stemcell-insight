-- STEMCELL INSIGHT Database Schema
-- SQLite relational database for stem-cell knowledge and cell-fate prediction

PRAGMA foreign_keys = ON;

-- Table 10: references (created first due to foreign key dependencies)
CREATE TABLE IF NOT EXISTS "references" (
    reference_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    authors TEXT,
    publication_year INTEGER,
    journal TEXT,
    DOI TEXT,
    URL TEXT,
    source_type TEXT DEFAULT 'Peer-reviewed Journal'
);

-- Table 1: stem_cells
CREATE TABLE IF NOT EXISTS stem_cells (
    cell_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    potency TEXT NOT NULL,
    species TEXT NOT NULL DEFAULT 'Homo sapiens',
    origin TEXT,
    self_renewal TEXT,
    description TEXT,
    source TEXT,
    reference_id TEXT,
    FOREIGN KEY (reference_id) REFERENCES "references"(reference_id) ON DELETE SET NULL
);

-- Table 2: cell_lines
CREATE TABLE IF NOT EXISTS cell_lines (
    line_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cell_id TEXT,
    cell_line_name TEXT NOT NULL,
    accession_number TEXT UNIQUE,
    synonyms TEXT,
    species TEXT DEFAULT 'Homo sapiens',
    tissue_origin TEXT,
    disease TEXT,
    donor_information TEXT,
    derivation_method TEXT,
    characteristics TEXT,
    source_database TEXT DEFAULT 'Cellosaurus',
    reference_id TEXT,
    FOREIGN KEY (cell_id) REFERENCES stem_cells(cell_id) ON DELETE SET NULL,
    FOREIGN KEY (reference_id) REFERENCES "references"(reference_id) ON DELETE SET NULL
);

-- Table 3: markers
CREATE TABLE IF NOT EXISTS markers (
    marker_id INTEGER PRIMARY KEY AUTOINCREMENT,
    marker_name TEXT NOT NULL,
    gene_symbol TEXT,
    marker_type TEXT,
    description TEXT,
    reference_id TEXT,
    FOREIGN KEY (reference_id) REFERENCES "references"(reference_id) ON DELETE SET NULL
);

-- Table 4: cell_markers
CREATE TABLE IF NOT EXISTS cell_markers (
    cell_id TEXT NOT NULL,
    marker_id INTEGER NOT NULL,
    association TEXT NOT NULL,
    differentiation_stage TEXT NOT NULL DEFAULT 'Undifferentiated',
    reference_id TEXT,
    PRIMARY KEY (cell_id, marker_id, differentiation_stage),
    FOREIGN KEY (cell_id) REFERENCES stem_cells(cell_id) ON DELETE CASCADE,
    FOREIGN KEY (marker_id) REFERENCES markers(marker_id) ON DELETE CASCADE,
    FOREIGN KEY (reference_id) REFERENCES "references"(reference_id) ON DELETE SET NULL
);

-- Table 5: differentiation
CREATE TABLE IF NOT EXISTS differentiation (
    differentiation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_cell_id TEXT NOT NULL,
    target_cell TEXT NOT NULL,
    lineage TEXT NOT NULL,
    conditions_summary TEXT,
    evidence_type TEXT DEFAULT 'Experimental',
    evidence_notes TEXT,
    reference_id TEXT,
    FOREIGN KEY (source_cell_id) REFERENCES stem_cells(cell_id) ON DELETE CASCADE,
    FOREIGN KEY (reference_id) REFERENCES "references"(reference_id) ON DELETE SET NULL
);

-- Table 6: signals
CREATE TABLE IF NOT EXISTS signals (
    signal_id INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_name TEXT NOT NULL UNIQUE,
    signal_type TEXT NOT NULL,
    pathway TEXT,
    biological_role TEXT,
    effect TEXT,
    reference_id TEXT,
    FOREIGN KEY (reference_id) REFERENCES "references"(reference_id) ON DELETE SET NULL
);

-- Table 7: differentiation_signals
CREATE TABLE IF NOT EXISTS differentiation_signals (
    differentiation_id INTEGER NOT NULL,
    signal_id INTEGER NOT NULL,
    role TEXT NOT NULL, -- 'Inducer (Required)', 'Enhancer (Optional)', 'Inhibitor (Negative Selector)'
    concentration TEXT,
    treatment_duration TEXT,
    reference_id TEXT,
    PRIMARY KEY (differentiation_id, signal_id, role),
    FOREIGN KEY (differentiation_id) REFERENCES differentiation(differentiation_id) ON DELETE CASCADE,
    FOREIGN KEY (signal_id) REFERENCES signals(signal_id) ON DELETE CASCADE,
    FOREIGN KEY (reference_id) REFERENCES "references"(reference_id) ON DELETE SET NULL
);

-- Table 8: protocols
CREATE TABLE IF NOT EXISTS protocols (
    protocol_id INTEGER PRIMARY KEY AUTOINCREMENT,
    protocol_name TEXT NOT NULL,
    source_cell TEXT NOT NULL,
    target_cell TEXT NOT NULL,
    medium TEXT,
    growth_factors TEXT,
    small_molecules TEXT,
    duration TEXT,
    reported_efficiency TEXT,
    efficiency_method TEXT,
    validation_markers TEXT,
    functional_validation TEXT,
    reference_id TEXT,
    FOREIGN KEY (reference_id) REFERENCES "references"(reference_id) ON DELETE SET NULL
);

-- Table 9: protocol_steps
CREATE TABLE IF NOT EXISTS protocol_steps (
    step_id INTEGER PRIMARY KEY AUTOINCREMENT,
    protocol_id INTEGER NOT NULL,
    step_number INTEGER NOT NULL,
    procedure TEXT NOT NULL,
    reagent TEXT,
    concentration TEXT,
    duration TEXT,
    notes TEXT,
    FOREIGN KEY (protocol_id) REFERENCES protocols(protocol_id) ON DELETE CASCADE
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_cell_lines_cell_id ON cell_lines(cell_id);
CREATE INDEX IF NOT EXISTS idx_cell_lines_name ON cell_lines(cell_line_name);
CREATE INDEX IF NOT EXISTS idx_cell_lines_accession ON cell_lines(accession_number);
CREATE INDEX IF NOT EXISTS idx_markers_gene ON markers(gene_symbol);
CREATE INDEX IF NOT EXISTS idx_markers_name ON markers(marker_name);
CREATE INDEX IF NOT EXISTS idx_cell_markers_cell ON cell_markers(cell_id);
CREATE INDEX IF NOT EXISTS idx_diff_source ON differentiation(source_cell_id);
CREATE INDEX IF NOT EXISTS idx_diff_target ON differentiation(target_cell);
CREATE INDEX IF NOT EXISTS idx_diff_lineage ON differentiation(lineage);
CREATE INDEX IF NOT EXISTS idx_signals_pathway ON signals(pathway);
CREATE INDEX IF NOT EXISTS idx_diff_signals_diff ON differentiation_signals(differentiation_id);
CREATE INDEX IF NOT EXISTS idx_protocols_cells ON protocols(source_cell, target_cell);
CREATE INDEX IF NOT EXISTS idx_protocol_steps_proto ON protocol_steps(protocol_id, step_number);
