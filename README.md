# StemCell Insight

### *An Intelligent Stem Cell Knowledge and Cell-Fate Prediction System*

**Tagline:** *Explore Stem Cell Biology. Understand Cell Fate. Discover Differentiation Pathways.*

---

## 1. Project Overview

**StemCell Insight** is an integrated, evidence-based stem cell knowledge and cell-fate reasoning platform developed in Python and Streamlit. Designed for stem cell biologists, biomedical engineers, regenerative medicine researchers, and computational biologists, it addresses the fragmentation of stem-cell knowledge by establishing transparent, traceable biological links across experimental dimensions:

$$\text{Starting Cell} \longrightarrow \text{Potency / Origin} \longrightarrow \text{Signaling Molecules} \longrightarrow \text{Pathways} \longrightarrow \text{Candidate Fate} \longrightarrow \text{Markers} \longrightarrow \text{Protocols} \longrightarrow \text{Literature Evidence}$$

---

## 2. Problem Statement & Objectives

### Problem Statement
Stem cell differentiation literature is vast, dispersed across thousands of journals, and burdened by heterogeneous experimental reporting. Conventional search engines only match keywords without understanding developmental hierarchies (e.g., distinguishing pluripotent capabilities from multipotent lineages) or signaling logic (e.g., temporal Wnt activation vs. inhibition). Furthermore, artificial intelligence language models frequently hallucinate reagent concentrations, protocol steps, or nonexistent DOI citations.

### Core Objectives
1. **Curate an Evidence-Based Knowledge Base:** Organize verified characteristics across five primary stem-cell categories (ESCs, iPSCs, MSCs, HSCs, NSCs).
2. **Standardize Cell-Line Records:** Ingest and parse Cellosaurus flat files with accession numbers (`CVCL_...`), synonyms, species, and external cross-references (e.g., hPSCreg, ATCC).
3. **Provide Explainable Biological Reasoning:** Develop a rule-based cell-fate reasoning engine that deduces candidate fates from experimental inputs and flags unsupported developmental transitions.
4. **Facilitate Protocol Comparison:** Search and benchmark published differentiation protocols side-by-side across basal media, growth factors, small molecules, and reported efficiencies.
5. **Audit Experimental Evidence:** Quantify documentation thoroughness using a transparent *Evidence Completeness Score*.
6. **Ground Chatbot Queries:** Answer natural-language biological questions strictly from verified SQLite records with direct literature citations.

---

## 3. System Architecture

The application adopts a modular **Three-Layer Architecture** supported by an independent offline data ingestion pipeline:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      LAYER 1: PRESENTATION (STREAMLIT)                  │
│   Home Dashboard │ Cell Explorer │ Biology Chatbot │ Cell-Fate Engine   │
│              Protocol Advisor │ Evidence Analyser │ Plotly Diagrams    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Python API Calls
┌───────────────────────────────────▼────────────────────────────────────┐
│                    LAYER 2: BUSINESS LOGIC (PYTHON MODULES)             │
│   modules/prediction_engine.py   │   modules/chatbot.py                │
│   utils/search.py (TF-IDF/Syns)  │   utils/visualizations.py (NetworkX)│
│   utils/data_validation.py       │   modules/protocol_advisor.py       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Parameterized SQL
┌───────────────────────────────────▼────────────────────────────────────┐
│                        LAYER 3: DATA LAYER (SQLITE)                     │
│                           database/stemcell.db                         │
│   stem_cells  cell_lines  markers  cell_markers  differentiation       │
│   signals     differentiation_signals  protocols  protocol_steps  refs  │
└───────────────────────────────────▲────────────────────────────────────┘
                                    │ Ingestion
┌───────────────────────────────────┴────────────────────────────────────┐
│               INDEPENDENT DATA INGESTION PIPELINE (PYTHON)              │
│       data/raw/cellosaurus.txt  cellosaurus_refs.txt  cellosaurus_xrefs │
│                database/import_cellosaurus.py ➔ SQLite                  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Technology Stack

| Component | Technology | Rationale / Contribution |
| :--- | :--- | :--- |
| **Language** | Python 3.11 | Modern, typed scientific computing environment |
| **Frontend Framework** | Streamlit | Responsive, interactive scientific web dashboard |
| **Database** | SQLite 3 (`stemcell.db`) | ACID-compliant, persistent relational data storage |
| **Data Processing** | Pandas | Tabular data manipulation and CSV export/import |
| **Network Graphs** | NetworkX | Biological graph modeling and topology layouts |
| **Interactive Visuals** | Plotly Graph Objects & Express | Interactive lineage networks, timelines, and radar charts |
| **Information Retrieval**| Python Regex + Scikit-learn TF-IDF | Keyword matching, biological synonym expansion, and cosine ranking |
| **Automated Testing** | Pytest | Comprehensive test suite for database, search, and logic |

---

## 5. Application Modules

### Module 1: Home Dashboard (`modules/home.py`)
- Live dynamic metrics queried from SQLite (stem cells, cell lines, differentiation relationships, markers, protocols, references).
- Visual workflow diagram mapping developmental transitions.
- Interactive Plotly overview network of stem cell lineages.

### Module 2: Cell Explorer (`modules/cell_explorer.py`)
- **Stem-Cell Profiles:** Dedicated profiles for ESCs, iPSCs, MSCs, HSCs, and NSCs detailing potency, biological origin, self-renewal mechanisms, surface markers, and differentiation potential.
- **Cell-Line Database:** Search authenticated cell lines by name, accession (`CVCL_...`), species, or tissue. Displays donor information, derivation method, and direct links to Cellosaurus and hPSCreg.

### Module 3: Ask StemCell Insight – Biology Chatbot (`modules/chatbot.py`)
- Retrieval-based question answering engine with synonym expansion (e.g. `OCT4` $\leftrightarrow$ `POU5F1`, `TUJ1` $\leftrightarrow$ `TUBB3`).
- Answers queries on mechanisms, signaling cascades, marker expressions, and protocols.
- Traceable literature references with DOIs and PubMed IDs.
- Guardrail: Explicitly returns an out-of-domain message rather than inventing false biology.

### Module 4: Cell-Fate Prediction Engine (`modules/prediction_engine.py`)
- Explainable biological rule engine. Users select starting stem cell, target cell fate, supplied induction signals, and culture format.
- Evaluates required vs. optional signals and verifies developmental potency.
- Rejects biologically impossible transitions (e.g., MSC $\rightarrow$ Cardiomyocyte, HSC $\rightarrow$ Cortical Neuron) with mechanistic explanations.
- Generates interactive Plotly pathway graphs and identifies missing induction factors.

### Module 5: Protocol Advisor (`modules/protocol_advisor.py`)
- Search published differentiation protocols by starting cell and target fate.
- Displays basal media, growth factors, small molecules, reported efficiencies, and validation assays.
- Step-by-step procedural viewer with reagent concentrations, durations, and protocol timelines.
- Side-by-side comparison matrix with radar completeness profiles.

### Module 6: Evidence Analyser (`modules/evidence_analyzer.py`)
- Audits experimental thoroughness across 10 empirical parameters (cell line details, concentrations, durations, controls, functional assays, replicates, DOIs).
- Generates an *Evidence Completeness Score* (0–100%) and categorizes reporting quality.

---

## 6. Database Schema (`database/schema.sql`)

The database is fully normalized with primary keys, foreign keys, cascade rules, and performance indexes:

1. `stem_cells`: Core stem cell classes (potency, origin, self-renewal, description).
2. `cell_lines`: Authenticated cell lines with unique accession numbers (`CVCL_...`), synonyms, species, tissue, disease, derivation.
3. `markers`: Molecular markers (gene symbol, marker name, class, description).
4. `cell_markers`: Many-to-many associations between cells and markers (positive/negative, stage).
5. `differentiation`: Lineage transitions, conditions summary, evidence notes.
6. `signals`: Biochemical factors, small molecules, signaling pathways, and biological effects.
7. `differentiation_signals`: Many-to-many mapping of signals to differentiation paths (required vs. optional, concentration, duration).
8. `protocols`: Published protocols (medium, growth factors, small molecules, duration, efficiency, validation assays).
9. `protocol_steps`: Sequential protocol steps (step number, procedure, reagent, concentration, duration, notes).
10. `references`: Traceable scientific citations (title, authors, year, journal, DOI, URL).

---

## 7. Installation & Local Execution

### Prerequisites
- Python 3.9+ (Python 3.11 recommended)
- Git (optional)

### Setup Instructions

1. **Clone or navigate to the project directory:**
   ```bash
   cd StemCell_Insight
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize and Seed Database:**
   ```bash
   python -m database.seed_data
   ```

5. **Run Cellosaurus Ingestion Pipeline (Optional/Included):**
   ```bash
   python -m database.import_cellosaurus
   ```

6. **Launch the Streamlit Web Application:**
   ```bash
   streamlit run app.py
   ```
   The application will open automatically in your browser at `http://localhost:8501`.

---

## 8. Cellosaurus Ingestion Instructions

The application includes an offline ingestion pipeline for Cellosaurus flat files located in `data/raw/`:

- `cellosaurus_refs.txt` (Included): Contains thousands of scientific citations.
- `cellosaurus_xrefs.txt` (Included): Contains external database URL mapping rules.
- `cellosaurus.txt`: The primary flat file containing >150,000 cell lines.

### Adding New Records from Cellosaurus
1. Download `cellosaurus.txt` from the official Swiss Institute of Bioinformatics FTP server:
   [ftp://ftp.expasy.org/databases/cellosaurus/cellosaurus.txt](ftp://ftp.expasy.org/databases/cellosaurus/cellosaurus.txt)
2. Place `cellosaurus.txt` into `data/raw/`.
3. Execute the parser:
   ```bash
   python -m database.import_cellosaurus
   ```
4. The parser streams records line-by-line, filters authenticated stem-cell lines (`ESC`, `IPSC`, `MSC`, `HSC`, `NSC`), resolves external URLs, and prevents duplicate entries using `ON CONFLICT(accession_number) DO UPDATE`.

---

## 9. Running Automated Tests

A comprehensive Pytest suite validates database integrity, biological reasoning, search algorithms, and chatbot guardrails:

```bash
pytest -v
```

### Test Coverage Highlights:
- `tests/test_database.py`: Table creation, foreign key referential integrity, duplicate prevention, dynamic statistics.
- `tests/test_prediction.py`: MSC osteogenesis/adipogenesis rule matching, missing signal detection, incompatible lineage rejection (e.g. HSC $\rightarrow$ Cardiomyocyte).
- `tests/test_search.py`: Biological synonym expansion (`OCT4` $\rightarrow$ `POU5F1`), multi-table search, chatbot QA retrieval, unsupported question guardrails.

---

## 10. Scientific Scope & Methodological Limitations

- **Rule-Based Deductive System:** The cell-fate prediction engine is a deterministic, explainable biological rule engine. It is **not** a trained statistical machine learning model.
- **Reporting vs. Execution:** The *Evidence Completeness Score* reflects documentation thoroughness within the curated publication. A missing parameter indicates that the detail was **'Not reported'**; it does not constitute proof that the assay was not performed.
- **Biological Heterogeneity:** Stem cell differentiation kinetics vary across genetic backgrounds, clonal passage numbers, feeder vs. feeder-free matrices, and batch-to-batch growth factor bioactivity. Always validate experimental parameters in pilot titrations.

---

## 11. Future Scope

1. **scRNA-seq Transcriptomic Integration:** Ingest single-cell RNA sequencing datasets (e.g., Human Cell Atlas) to project differentiating cells onto reference trajectory manifolds (UMAP/pseudotime).
2. **Automated PubMed / BioRxiv Harvester:** Continuous ingestion of new differentiation protocols via NCBI Entrez API.
3. **LLM Hybrid Agent:** Embed localized, quantized LLM inference (e.g., Llama-3/Gemini) with strict RAG verification over SQLite records.
4. **Lab Automation Integration:** Export protocol steps directly to liquid handling robot scripts (e.g., Opentrons OT-2 Python protocol format).

---

## 12. License & Attribution

- **Application Software:** MIT License.
- **Cellosaurus Data:** Creative Commons Attribution 4.0 International (CC BY 4.0) License. Swiss Institute of Bioinformatics (SIB).
- **Literature Records:** Citations, abstracts, and DOIs remain copyright of their respective peer-reviewed journals.
