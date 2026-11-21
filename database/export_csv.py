"""
export_csv.py - Exports SQLite tables to structured CSV files in data/processed/.
"""

import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DB_PATH = os.path.join(BASE_DIR, "stemcell.db")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")


def export_all_tables_to_csv() -> None:
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    tables = [
        "stem_cells",
        "cell_lines",
        "markers",
        "cell_markers",
        "differentiation",
        "signals",
        "differentiation_signals",
        "protocols",
        "protocol_steps",
        "references"
    ]
    for table in tables:
        df = pd.read_sql_query(f'SELECT * FROM "{table}";', conn)
        csv_file = os.path.join(PROCESSED_DIR, f"{table}.csv")
        df.to_csv(csv_file, index=False)
        print(f"Exported {table}: {len(df)} rows -> {csv_file}")
    conn.close()


if __name__ == "__main__":
    export_all_tables_to_csv()
