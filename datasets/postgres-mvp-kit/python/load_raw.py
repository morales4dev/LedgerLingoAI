#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path
from typing import Iterable

import psycopg


def iter_json_records(file_path: Path):
    text = file_path.read_text(encoding="utf-8")

    # Detect unresolved Git LFS pointer files.
    if text.startswith("version https://git-lfs.github.com/spec/v1"):
        raise ValueError("git-lfs pointer detected (file content not pulled)")

    data = json.loads(text)
    if isinstance(data, list):
        for idx, row in enumerate(data):
            yield idx, row
    elif isinstance(data, dict):
        yield 0, data
    else:
        yield 0, {"value": data}


def iter_csv_records(file_path: Path):
    with file_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            yield idx, row


def discover_files(dataset_root: Path) -> Iterable[Path]:
    for path in sorted(dataset_root.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".json", ".csv"}:
            yield path


def load_records(conn, source_path: str, records):
    sql = """
    INSERT INTO raw.file_records (source_path, record_index, payload)
    VALUES (%s, %s, %s::jsonb)
    ON CONFLICT (source_path, record_index)
    DO UPDATE SET payload = EXCLUDED.payload, loaded_at = NOW()
    """
    with conn.cursor() as cur:
        batch = []
        for record_index, payload in records:
            batch.append((source_path, record_index, json.dumps(payload)))
            if len(batch) >= 1000:
                cur.executemany(sql, batch)
                batch.clear()
        if batch:
            cur.executemany(sql, batch)


def main():
    parser = argparse.ArgumentParser(description="Load dataset files into raw.file_records")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--dataset-dir", required=True)
    parser.add_argument("--db-host", required=True)
    parser.add_argument("--db-port", required=True)
    parser.add_argument("--db-name", required=True)
    parser.add_argument("--db-user", required=True)
    parser.add_argument("--db-password", required=True)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    dataset_root = (repo_root / args.dataset_dir).resolve()
    if not dataset_root.exists():
        raise SystemExit(f"Dataset directory not found: {dataset_root}")

    conn = psycopg.connect(
        host=args.db_host,
        port=args.db_port,
        dbname=args.db_name,
        user=args.db_user,
        password=args.db_password,
        autocommit=False,
    )

    total_files = 0
    loaded_files = 0
    skipped_files = 0

    try:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE raw.file_records")
        conn.commit()

        for file_path in discover_files(dataset_root):
            total_files += 1
            rel_path = str(file_path.relative_to(repo_root)).replace("\\\\", "/")
            try:
                if file_path.suffix.lower() == ".json":
                    records = iter_json_records(file_path)
                else:
                    records = iter_csv_records(file_path)

                load_records(conn, rel_path, records)
                conn.commit()
                loaded_files += 1
            except Exception as exc:
                conn.rollback()
                skipped_files += 1
                print(f"[WARN] Skipping {rel_path}: {exc}")

        print(f"[INFO] Files discovered: {total_files}")
        print(f"[INFO] Files loaded: {loaded_files}")
        print(f"[INFO] Files skipped: {skipped_files}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
