# Cellosaurus Raw Data Directory

This directory stores raw data files downloaded from the Cellosaurus knowledge resource (Swiss Institute of Bioinformatics - SIB) and complementary scientific repositories.

## Expected Files

1. `cellosaurus.txt`
   - **Description:** Complete flat file containing all cell line records with accession numbers (`AC`), names (`ID`), synonyms (`SY`), species (`OX`), disease (`DI`), category (`CA` / `CC`), and cross-references (`DR`).
   - **Download URL:** [ftp://ftp.expasy.org/databases/cellosaurus/cellosaurus.txt](https://ftp.expasy.org/databases/cellosaurus/cellosaurus.txt) or [https://ftp.expasy.org/databases/cellosaurus/cellosaurus.txt](https://ftp.expasy.org/databases/cellosaurus/cellosaurus.txt)
   - **License:** Creative Commons Attribution 4.0 International (CC BY 4.0).

2. `cellosaurus_refs.txt` (Included)
   - **Description:** References file containing literature citations, PubMed IDs, DOIs, publication titles, authors, and journal citations corresponding to Cellosaurus records.
   - **Format:** Structured records initiated by `RX` and terminated by `//`.

3. `cellosaurus_xrefs.txt` (Included)
   - **Description:** Document specifying URL templates for cross-referencing external resources (e.g., hPSCreg, ATCC, DSMZ, NCBI GEO, ChEMBL).

## Running the Ingestion Pipeline

To parse and import records from these files into the SQLite database (`database/stemcell.db`), execute:

```bash
python -m database.import_cellosaurus
```

The ingestion pipeline will:
1. Load cross-reference URL templates from `cellosaurus_xrefs.txt`.
2. Extract PubMed and DOI literature citations from `cellosaurus_refs.txt`.
3. Stream records from `cellosaurus.txt` (when present), filtering authenticated human embryonic stem cell (`ESC`), induced pluripotent stem cell (`iPSC`), mesenchymal stem cell (`MSC`), hematopoietic stem cell (`HSC`), and neural stem cell (`NSC`) records.
4. Prevent duplicate insertions using unique database constraints (`ON CONFLICT`).
