"""Dataset import utility and CLI command for loading, validating, and persisting music datasets.

Usage:
    python -m backend.data.import_songs [--csv PATH] [--db PATH]
"""

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import sqlite3
import sys
import time
from typing import List, Optional
import pandas as pd

# Add repository root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.data.preprocessing import preprocess_dataset
from backend.database.connection import DEFAULT_DB_PATH, get_db_connection, init_db, is_postgres


def import_dataset(
    csv_path: Optional[Path] = None,
    db_path: Path = DEFAULT_DB_PATH,
    chunk_size: int = 5000,
) -> dict:
    """Executes the dataset import pipeline for a given CSV or all raw datasets."""
    start_time = time.time()
    
    files_to_import: List[Path] = []
    if csv_path is not None:
        files_to_import = [Path(csv_path)]
    else:
        # Import all available raw datasets
        raw_dir = PROJECT_ROOT / "data" / "raw"
        candidate_files = [
            raw_dir / "spotify_millsongdata.csv",
            raw_dir / "tamil_songs_corpus.csv",
            raw_dir / "songs.csv",
        ]
        for f in candidate_files:
            if f.exists() and f.stat().st_size > 0:
                files_to_import.append(f)

    if not files_to_import:
        raise FileNotFoundError(f"No source datasets found in data/raw/.")

    print(f"[*] Found {len(files_to_import)} dataset file(s) to import:")
    for f in files_to_import:
        print(f"    - {f.name} ({f.stat().st_size / (1024*1024):.2f} MB)")

    all_clean_dfs: List[pd.DataFrame] = []
    total_source_rows = 0
    total_valid_rows = 0
    total_invalid_rows = 0
    total_duplicate_rows = 0

    for file_p in files_to_import:
        print(f"\n[*] Processing: {file_p.name}...")
        raw_df = pd.read_csv(file_p)
        print(f"[*] Raw shape: {raw_df.shape[0]:,} rows, {raw_df.shape[1]} columns.")
        clean_df, rep = preprocess_dataset(raw_df)
        if clean_df is not None and not clean_df.empty:
            all_clean_dfs.append(clean_df)
            total_source_rows += rep.source_rows
            total_valid_rows += rep.valid_rows
            total_invalid_rows += rep.invalid_rows
            total_duplicate_rows += rep.duplicate_rows
            print(f"[*] Processed {len(clean_df):,} valid records from {file_p.name}.")

    if not all_clean_dfs:
        raise ValueError("No valid songs were extracted from any input datasets.")

    combined_df = pd.concat(all_clean_dfs, ignore_index=True)
    before_dedup = len(combined_df)
    combined_df = combined_df.drop_duplicates(subset=["song_id"]).reset_index(drop=True)
    cross_dataset_dups = before_dedup - len(combined_df)

    report_dir = PROJECT_ROOT / "data" / "processed"
    report_dir.mkdir(parents=True, exist_ok=True)
    processed_csv_path = report_dir / "songs_processed.csv"
    combined_df.to_csv(processed_csv_path, index=False)
    print(f"\n[*] Unified dataset saved to {processed_csv_path} ({len(combined_df):,} total songs).")

    # Initialize database schema
    print("[*] Initializing database schema...")
    init_db(db_path)

    # Bulk insert into database
    conn = get_db_connection(db_path)
    is_pg = hasattr(conn, "autocommit") and not isinstance(conn, sqlite3.Connection)
    cursor = conn.cursor()

    upsert_sql = """
    INSERT INTO songs (
        song_id, song_name, artist, lyrics, source_link, source_dataset,
        album, genre, language, year
    ) VALUES (
        ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?
    )
    ON CONFLICT(song_id) DO UPDATE SET
        song_name=excluded.song_name,
        artist=excluded.artist,
        lyrics=excluded.lyrics,
        source_link=excluded.source_link,
        album=excluded.album,
        genre=excluded.genre,
        language=excluded.language,
        year=excluded.year,
        updated_at=CURRENT_TIMESTAMP
    """
    if is_pg:
        upsert_sql = upsert_sql.replace("?", "%s")

    print(f"[*] Bulk inserting {len(combined_df):,} songs into database in batches of {chunk_size:,}...")
    records = []
    for _, row in combined_df.iterrows():
        records.append((
            str(row["song_id"]),
            str(row["song_name"]),
            str(row["artist"]),
            str(row["lyrics"]) if pd.notna(row.get("lyrics")) and row.get("lyrics") is not None else None,
            str(row["source_link"]) if pd.notna(row.get("source_link")) and row.get("source_link") is not None else None,
            str(row.get("source_dataset", "spotify_millsongdata")),
            str(row["album"]) if pd.notna(row.get("album")) and row.get("album") is not None else None,
            str(row["genre"]) if pd.notna(row.get("genre")) and row.get("genre") is not None else None,
            str(row["language"]) if pd.notna(row.get("language")) and row.get("language") is not None else None,
            int(row["year"]) if pd.notna(row.get("year")) and row.get("year") is not None else None,
        ))

    total_inserted = 0
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i + chunk_size]
        cursor.executemany(upsert_sql, chunk)
        conn.commit()
        total_inserted += len(chunk)
        print(f"    -> Inserted {total_inserted:,} / {len(records):,} records...")

    conn.close()

    # Tamil songs breakdown
    tamil_count = int((combined_df["language"].str.lower() == "tamil").sum())
    languages_counts = combined_df["language"].value_counts().to_dict()

    elapsed = time.time() - start_time
    print(f"\n[+] Import complete in {elapsed:.2f} seconds.")
    print("=" * 60)
    print(f"  Total Source Rows:      {total_source_rows:,}")
    print(f"  Final Imported Rows:    {len(combined_df):,}")
    print(f"  Tamil Songs Imported:   {tamil_count:,}")
    print(f"  Unique Artists:         {combined_df['artist'].nunique():,}")
    print(f"  Unique Songs:           {combined_df['song_name'].nunique():,}")
    print(f"  Languages Distribution: {languages_counts}")
    print("=" * 60)

    # Save detailed data quality report
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "total_source_rows": total_source_rows,
        "final_imported_rows": len(combined_df),
        "tamil_songs_imported": tamil_count,
        "languages_distribution": languages_counts,
        "unique_artists": int(combined_df["artist"].nunique()),
        "unique_songs": int(combined_df["song_name"].nunique()),
        "elapsed_seconds": round(elapsed, 2),
    }
    with open(report_dir / "data_quality_report.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    return report_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import music datasets into TuneSphere database.")
    parser.add_argument("--csv", type=Path, default=None, help="Path to specific raw CSV dataset")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="Path to SQLite database")
    args = parser.parse_args()

    import_dataset(csv_path=args.csv, db_path=args.db)

