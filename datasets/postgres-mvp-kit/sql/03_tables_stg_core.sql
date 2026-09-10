CREATE TABLE IF NOT EXISTS stg.journal_entry_header (
  document_id TEXT,
  company_code TEXT,
  fiscal_year TEXT,
  fiscal_period TEXT,
  posting_date TEXT,
  document_date TEXT,
  created_at TEXT,
  document_type TEXT,
  currency TEXT,
  exchange_rate TEXT,
  reference TEXT,
  header_text TEXT,
  created_by TEXT,
  source TEXT,
  business_process TEXT,
  raw_source_path TEXT,
  raw_record_index INTEGER
);

CREATE TABLE IF NOT EXISTS stg.journal_entry_line (
  document_id TEXT,
  line_no INTEGER,
  account_code TEXT,
  posting_key TEXT,
  debit_amount TEXT,
  credit_amount TEXT,
  amount TEXT,
  cost_center TEXT,
  profit_center TEXT,
  tax_code TEXT,
  raw_source_path TEXT,
  raw_record_index INTEGER
);

CREATE TABLE IF NOT EXISTS stg.chart_of_accounts (
  coa_id TEXT,
  industry TEXT,
  country TEXT,
  account_code TEXT,
  account_name TEXT,
  account_type TEXT,
  parent_account_code TEXT,
  raw_source_path TEXT,
  raw_record_index INTEGER
);

CREATE TABLE IF NOT EXISTS stg.vendors (
  vendor_id TEXT,
  vendor_name TEXT,
  country TEXT,
  raw_source_path TEXT,
  raw_record_index INTEGER
);

CREATE TABLE IF NOT EXISTS stg.customers (
  customer_id TEXT,
  customer_name TEXT,
  country TEXT,
  raw_source_path TEXT,
  raw_record_index INTEGER
);

CREATE TABLE IF NOT EXISTS core.gl_account (
  account_code TEXT PRIMARY KEY,
  account_name TEXT,
  account_type TEXT,
  country TEXT,
  industry TEXT,
  parent_account_code TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS core.vendor (
  vendor_id TEXT PRIMARY KEY,
  vendor_name TEXT,
  country TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS core.customer (
  customer_id TEXT PRIMARY KEY,
  customer_name TEXT,
  country TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS core.journal_entry_header (
  document_id TEXT PRIMARY KEY,
  company_code TEXT NOT NULL,
  fiscal_year INTEGER,
  fiscal_period INTEGER,
  posting_date DATE,
  document_date DATE,
  created_at_ts TIMESTAMPTZ,
  document_type TEXT,
  currency TEXT,
  exchange_rate NUMERIC(18,6),
  reference TEXT,
  header_text TEXT,
  created_by TEXT,
  source TEXT,
  business_process TEXT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS core.journal_entry_line (
  document_id TEXT NOT NULL,
  line_no INTEGER NOT NULL,
  account_code TEXT NOT NULL,
  posting_key TEXT,
  debit_amount NUMERIC(18,2),
  credit_amount NUMERIC(18,2),
  amount NUMERIC(18,2),
  cost_center TEXT,
  profit_center TEXT,
  tax_code TEXT,
  loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (document_id, line_no),
  CONSTRAINT fk_jel_header FOREIGN KEY (document_id) REFERENCES core.journal_entry_header(document_id),
  CONSTRAINT fk_jel_account FOREIGN KEY (account_code) REFERENCES core.gl_account(account_code)
);

CREATE INDEX IF NOT EXISTS idx_jeh_posting_date ON core.journal_entry_header (posting_date);
CREATE INDEX IF NOT EXISTS idx_jel_account_code ON core.journal_entry_line (account_code);
