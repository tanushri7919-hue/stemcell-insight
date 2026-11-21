"""
import_cellosaurus.py - Ingestion pipeline for Cellosaurus database files.
Parses cellosaurus.txt, cellosaurus_refs.txt, and cellosaurus_xrefs.txt,
extracts authenticated stem-cell lines and references, and stores them in SQLite.
"""

import os
import re
import sqlite3
from typing import Dict, Generator, List, Optional, Tuple
from database.database import get_connection, insert_cell_line, insert_reference

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATA_RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")


class CellosaurusIngestionPipeline:
    """Robust streaming parser for official Cellosaurus flat files."""

    def __init__(self, raw_dir: Optional[str] = None, db_path: Optional[str] = None):
        self.raw_dir = raw_dir or DATA_RAW_DIR
        self.db_path = db_path
        self.xrefs_map: Dict[str, str] = {}
        self.stats = {
            "parsed_records": 0,
            "imported_cell_lines": 0,
            "imported_references": 0,
            "skipped_records": 0,
        }

    def load_cross_references(self) -> Dict[str, str]:
        """Parse cellosaurus_xrefs.txt to build URL resolution map."""
        xrefs_file = os.path.join(self.raw_dir, "cellosaurus_xrefs.txt")
        if not os.path.exists(xrefs_file):
            print(f"[XREFS] Notice: {xrefs_file} not found. Skipping URL resolution.")
            return {}

        current_db = None
        db_url = None
        with open(xrefs_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line.startswith("Abbrev: "):
                    current_db = line[8:].strip()
                elif line.startswith("Db_URL: ") and current_db:
                    db_url = line[8:].strip()
                    self.xrefs_map[current_db] = db_url
                elif line == "//":
                    current_db = None
                    db_url = None

        print(f"[XREFS] Loaded {len(self.xrefs_map)} cross-reference URL templates.")
        return self.xrefs_map

    def parse_references_file(self, limit: int = 500) -> int:
        """Parse cellosaurus_refs.txt and ingest literature references into SQLite."""
        refs_file = os.path.join(self.raw_dir, "cellosaurus_refs.txt")
        if not os.path.exists(refs_file):
            print(f"[REFS] Notice: {refs_file} not found.")
            return 0

        print(f"[REFS] Parsing references from {refs_file} (batch limit: {limit})...")
        count = 0
        current_ref: Dict[str, str] = {}
        authors: List[str] = []

        with open(refs_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.rstrip("\r\n")
                if line.startswith("**"):
                    continue

                if line.startswith("RX   "):
                    current_ref = {}
                    authors = []
                    # Parse RX fields: PubMed=123456; DOI=10.1016/...; PMCID=PMC...;
                    rx_content = line[5:].strip()
                    for token in rx_content.split(";"):
                        token = token.strip()
                        if "=" in token:
                            k, v = token.split("=", 1)
                            current_ref[k.strip()] = v.strip()

                elif line.startswith("RA   "):
                    author = line[5:].strip()
                    if author:
                        authors.append(author)

                elif line.startswith("RT   "):
                    title_part = line[5:].strip().strip('"').rstrip(";")
                    current_ref["title"] = (current_ref.get("title", "") + " " + title_part).strip()

                elif line.startswith("RL   "):
                    citation = line[5:].strip()
                    current_ref["citation"] = citation
                    # Extract year from citation e.g. (2024).
                    year_match = re.search(r"\((\d{4})\)", citation)
                    if year_match:
                        current_ref["year"] = year_match.group(1)

                elif line == "//":
                    if current_ref and ("PubMed" in current_ref or "DOI" in current_ref):
                        ref_id = f"PMID:{current_ref['PubMed']}" if "PubMed" in current_ref else f"DOI:{current_ref['DOI']}"
                        title = current_ref.get("title") or "Cellosaurus Research Reference"
                        doi = current_ref.get("DOI")
                        year = int(current_ref["year"]) if "year" in current_ref and current_ref["year"].isdigit() else None
                        authors_str = ", ".join(authors[:5]) + (" et al." if len(authors) > 5 else "") if authors else None
                        url = f"https://doi.org/{doi}" if doi else (f"https://pubmed.ncbi.nlm.nih.gov/{current_ref['PubMed']}/" if "PubMed" in current_ref else None)

                        insert_reference(
                            reference_id=ref_id,
                            title=title,
                            authors=authors_str,
                            publication_year=year,
                            journal=current_ref.get("citation"),
                            DOI=doi,
                            URL=url,
                            source_type="Cellosaurus Reference",
                            db_path=self.db_path
                        )
                        count += 1
                        if count >= limit:
                            break

        self.stats["imported_references"] = count
        print(f"[REFS] Successfully imported {count} references into SQLite.")
        return count

    def stream_cell_lines(self) -> Generator[Dict[str, str], None, None]:
        """Stream parsed cell-line blocks from cellosaurus.txt without loading full file into memory."""
        cellosaurus_file = os.path.join(self.raw_dir, "cellosaurus.txt")
        if not os.path.exists(cellosaurus_file):
            print(f"[CELLOSAURUS] File not found: {cellosaurus_file}")
            print("[CELLOSAURUS] Please place the official cellosaurus.txt in data/raw/ to run full line parsing.")
            return

        record: Dict[str, any] = {
            "synonyms": [],
            "species": "Homo sapiens",
            "tissue": None,
            "disease": None,
            "characteristics": [],
            "category": None,
            "xrefs": {},
            "refs": [],
            "sex": None,
        }

        with open(cellosaurus_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.rstrip("\r\n")

                if line.startswith("ID   "):
                    record["name"] = line[5:].strip()
                elif line.startswith("AC   "):
                    record["accession"] = line[5:].strip()
                elif line.startswith("SY   "):
                    record["synonyms"].append(line[5:].strip())
                elif line.startswith("OX   "):
                    # OX   NCBI_TaxID=9606; ! Homo sapiens (Human)
                    ox = line[5:].strip()
                    if "Homo sapiens" in ox:
                        record["species"] = "Homo sapiens"
                    elif "Mus musculus" in ox:
                        record["species"] = "Mus musculus (Mouse)"
                    elif "!" in ox:
                        record["species"] = ox.split("!")[-1].strip()
                    else:
                        record["species"] = ox
                elif line.startswith("SX   "):
                    record["sex"] = line[5:].strip()
                elif line.startswith("CA   "):
                    # Direct category line in Cellosaurus
                    record["category"] = line[5:].strip()
                elif line.startswith("CC   "):
                    comment = line[5:].strip()
                    if comment.startswith("Category:"):
                        record["category"] = comment[9:].strip().rstrip(".")
                    elif comment.startswith("Derivation:"):
                        record["derivation"] = comment[11:].strip()
                    elif comment.startswith("Characteristics:"):
                        record["characteristics"].append(comment[16:].strip())
                    elif comment.startswith("Donor:"):
                        record["donor"] = comment[6:].strip()
                elif line.startswith("DI   "):
                    record["disease"] = line[5:].strip()
                elif line.startswith("DR   "):
                    # DR   hPSCreg; WAe009-A
                    parts = line[5:].split(";", 1)
                    if len(parts) == 2:
                        db_name = parts[0].strip()
                        db_acc = parts[1].strip()
                        record["xrefs"][db_name] = db_acc
                elif line.startswith("RX   "):
                    rx = line[5:].strip()
                    for token in rx.split(";"):
                        token = token.strip()
                        if token.startswith("PubMed="):
                            record["refs"].append(f"PMID:{token[7:]}")
                        elif token.startswith("DOI="):
                            record["refs"].append(f"DOI:{token[4:]}")

                elif line == "//":
                    if "accession" in record and "name" in record:
                        yield record
                    # Reset record
                    record = {
                        "synonyms": [],
                        "species": "Homo sapiens",
                        "tissue": None,
                        "disease": None,
                        "characteristics": [],
                        "category": None,
                        "xrefs": {},
                        "refs": [],
                        "sex": None,
                    }

    def classify_stem_cell_category(self, record: Dict[str, any]) -> Optional[str]:
        """Classify cell-line record into one of 5 stem-cell categories
        based strictly on curated annotations, avoiding naive substring matching.
        """
        category_annot = (record.get("category") or "").lower()
        characteristics = " ".join(record.get("characteristics", [])).lower()
        combined_meta = f"{category_annot} {characteristics}"

        # 1. Pluripotent categories (ESC & iPSC)
        if "embryonic stem cell" in category_annot:
            return "ESC"
        if "induced pluripotent stem cell" in category_annot or "ipsc" in category_annot:
            return "IPSC"

        # Check cross references (hPSCreg only registers hESCs and hiPSCs)
        if "hPSCreg" in record.get("xrefs", {}):
            if "embryonic" in combined_meta or "esc" in combined_meta:
                return "ESC"
            return "IPSC"

        # 2. Mesenchymal Stem/Stromal Cells
        if "mesenchymal stem cell" in category_annot or "mesenchymal stromal cell" in category_annot:
            return "MSC"
        if "multipotent stromal cell" in category_annot:
            return "MSC"

        # 3. Hematopoietic Stem Cells
        if "hematopoietic stem cell" in category_annot or "hematopoietic progenitor" in category_annot:
            return "HSC"

        # 4. Neural Stem Cells
        if "neural stem cell" in category_annot or "neural progenitor cell" in category_annot:
            return "NSC"

        return None

    def run_import(self, max_cell_lines: int = 250) -> Dict[str, int]:
        """Execute the end-to-end ingestion pipeline."""
        print("=" * 60)
        print("STARTING CELLOSAURUS DATA INGESTION PIPELINE")
        print("=" * 60)

        # 1. Load cross-reference mapping
        self.load_cross_references()

        # 2. Ingest references
        self.parse_references_file(limit=500)

        # 3. Parse cell lines
        cellosaurus_file = os.path.join(self.raw_dir, "cellosaurus.txt")
        if not os.path.exists(cellosaurus_file):
            print(f"\n[INFO] cellosaurus.txt is not currently in {self.raw_dir}.")
            print("[INFO] To import additional cell lines from Cellosaurus:")
            print("       1. Download cellosaurus.txt from ftp://ftp.expasy.org/databases/cellosaurus/cellosaurus.txt")
            print(f"       2. Place it in: {self.raw_dir}")
            print("       3. Re-run: python database/import_cellosaurus.py\n")
            return self.stats

        print(f"\n[PARSER] Streaming cell-line records from {cellosaurus_file}...")
        for record in self.stream_cell_lines():
            self.stats["parsed_records"] += 1

            cell_cat = self.classify_stem_cell_category(record)
            if not cell_cat:
                self.stats["skipped_records"] += 1
                continue

            # Resolve external URLs
            char_list = list(record.get("characteristics", []))
            for db_name, acc in record.get("xrefs", {}).items():
                if db_name in self.xrefs_map:
                    url_tpl = self.xrefs_map[db_name]
                    target_url = url_tpl.replace("%s", acc) if "%s" in url_tpl else f"{url_tpl}{acc}"
                    char_list.append(f"External Ref ({db_name}): {acc} [{target_url}]")

            donor_info = record.get("donor") or (f"Sex: {record['sex']}" if record.get("sex") else None)
            synonyms_str = "; ".join(record.get("synonyms", [])) or None
            char_str = " | ".join(char_list) or None
            ref_id = record["refs"][0] if record.get("refs") else None

            insert_cell_line(
                cell_id=cell_cat,
                cell_line_name=record["name"],
                accession_number=record["accession"],
                synonyms=synonyms_str,
                species=record.get("species", "Homo sapiens"),
                tissue_origin=record.get("tissue") or "Not reported",
                disease=record.get("disease") or "None reported",
                donor_information=donor_info,
                derivation_method=record.get("derivation"),
                characteristics=char_str,
                source_database="Cellosaurus",
                reference_id=ref_id,
                db_path=self.db_path
            )
            self.stats["imported_cell_lines"] += 1

            if self.stats["imported_cell_lines"] >= max_cell_lines:
                print(f"[LIMIT] Reached ingestion batch limit of {max_cell_lines} records.")
                break

        print("=" * 60)
        print("CELLOSAURUS INGESTION COMPLETED")
        print(f"  Total records parsed:    {self.stats['parsed_records']}")
        print(f"  Stem cell lines saved:   {self.stats['imported_cell_lines']}")
        print(f"  References saved:        {self.stats['imported_references']}")
        print("=" * 60)
        return self.stats


if __name__ == "__main__":
    pipeline = CellosaurusIngestionPipeline()
    pipeline.run_import()
