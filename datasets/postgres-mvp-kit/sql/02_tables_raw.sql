CREATE TABLE IF NOT EXISTS raw.file_records (
  id BIGSERIAL PRIMARY KEY,
  source_path TEXT NOT NULL,
  record_index INTEGER NOT NULL,
  payload JSONB NOT NULL,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (source_path, record_index)
);

CREATE TABLE IF NOT EXISTS raw.load_runs (
  run_id BIGSERIAL PRIMARY KEY,
  dataset_dir TEXT NOT NULL,
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  finished_at TIMESTAMPTZ,
  status TEXT NOT NULL DEFAULT 'running',
  message TEXT
);
