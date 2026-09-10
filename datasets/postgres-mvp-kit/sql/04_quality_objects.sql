CREATE TABLE IF NOT EXISTS audit.reject_journal_entry_header (
  id BIGSERIAL PRIMARY KEY,
  document_id TEXT,
  company_code TEXT,
  posting_date TEXT,
  reason_code TEXT NOT NULL,
  reason_detail TEXT,
  raw_source_path TEXT,
  raw_record_index INTEGER,
  rejected_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit.reject_journal_entry_line (
  id BIGSERIAL PRIMARY KEY,
  document_id TEXT,
  line_no INTEGER,
  account_code TEXT,
  debit_amount TEXT,
  credit_amount TEXT,
  amount TEXT,
  reason_code TEXT NOT NULL,
  reason_detail TEXT,
  raw_source_path TEXT,
  raw_record_index INTEGER,
  rejected_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit.pipeline_events (
  id BIGSERIAL PRIMARY KEY,
  event_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  stage TEXT NOT NULL,
  status TEXT NOT NULL,
  detail TEXT
);
