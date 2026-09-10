TRUNCATE TABLE stg.journal_entry_header;
TRUNCATE TABLE stg.journal_entry_line;
TRUNCATE TABLE stg.chart_of_accounts;
TRUNCATE TABLE stg.vendors;
TRUNCATE TABLE stg.customers;
TRUNCATE TABLE audit.reject_journal_entry_header;
TRUNCATE TABLE audit.reject_journal_entry_line;

INSERT INTO stg.chart_of_accounts (
  coa_id, industry, country, account_code, account_name, account_type, parent_account_code, raw_source_path, raw_record_index
)
SELECT
  r.payload ->> 'coa_id',
  r.payload ->> 'industry',
  r.payload ->> 'country',
  COALESCE(a.value ->> 'account_code', a.value ->> 'account_number'),
  COALESCE(a.value ->> 'name', a.value ->> 'short_description', a.value ->> 'long_description'),
  COALESCE(a.value ->> 'type', a.value ->> 'account_type'),
  COALESCE(a.value ->> 'parent_account_code', a.value ->> 'parent_account'),
  r.source_path,
  r.record_index
FROM raw.file_records r
JOIN LATERAL jsonb_array_elements(COALESCE(r.payload -> 'accounts', '[]'::jsonb)) AS a(value) ON TRUE
WHERE r.source_path LIKE '%/chart_of_accounts.json';

INSERT INTO stg.vendors (vendor_id, vendor_name, country, raw_source_path, raw_record_index)
SELECT
  COALESCE(r.payload ->> 'vendor_id', r.payload ->> 'id'),
  COALESCE(r.payload ->> 'vendor_name', r.payload ->> 'name'),
  COALESCE(r.payload ->> 'country', r.payload ->> 'country_code'),
  r.source_path,
  r.record_index
FROM raw.file_records r
WHERE r.source_path LIKE '%/master_data/vendors.json';

INSERT INTO stg.customers (customer_id, customer_name, country, raw_source_path, raw_record_index)
SELECT
  COALESCE(r.payload ->> 'customer_id', r.payload ->> 'id'),
  COALESCE(r.payload ->> 'customer_name', r.payload ->> 'name'),
  COALESCE(r.payload ->> 'country', r.payload ->> 'country_code'),
  r.source_path,
  r.record_index
FROM raw.file_records r
WHERE r.source_path LIKE '%/master_data/customers.json';

INSERT INTO stg.journal_entry_header (
  document_id, company_code, fiscal_year, fiscal_period, posting_date, document_date, created_at,
  document_type, currency, exchange_rate, reference, header_text, created_by, source, business_process,
  raw_source_path, raw_record_index
)
SELECT
  COALESCE(hdr.value ->> 'document_id', h.value ->> 'document_id'),
  COALESCE(hdr.value ->> 'company_code', h.value ->> 'company_code'),
  COALESCE(hdr.value ->> 'fiscal_year', h.value ->> 'fiscal_year'),
  COALESCE(hdr.value ->> 'fiscal_period', h.value ->> 'fiscal_period'),
  COALESCE(hdr.value ->> 'posting_date', h.value ->> 'posting_date'),
  COALESCE(hdr.value ->> 'document_date', h.value ->> 'document_date'),
  COALESCE(hdr.value ->> 'created_at', h.value ->> 'created_at'),
  COALESCE(hdr.value ->> 'document_type', h.value ->> 'document_type'),
  COALESCE(hdr.value ->> 'currency', h.value ->> 'currency'),
  COALESCE(hdr.value ->> 'exchange_rate', h.value ->> 'exchange_rate'),
  COALESCE(hdr.value ->> 'reference', h.value ->> 'reference'),
  COALESCE(hdr.value ->> 'header_text', h.value ->> 'header_text'),
  COALESCE(hdr.value ->> 'created_by', h.value ->> 'created_by'),
  COALESCE(hdr.value ->> 'source', h.value ->> 'source'),
  COALESCE(hdr.value ->> 'business_process', h.value ->> 'business_process'),
  r.source_path,
  r.record_index
FROM raw.file_records r
JOIN LATERAL jsonb_array_elements(
  CASE
    WHEN jsonb_typeof(r.payload) = 'array' THEN r.payload
    ELSE jsonb_build_array(r.payload)
  END
) h(value) ON TRUE
JOIN LATERAL (
  SELECT CASE
    WHEN jsonb_typeof(h.value -> 'header') = 'object' THEN h.value -> 'header'
    ELSE h.value
  END AS value
) hdr ON TRUE
WHERE r.source_path LIKE '%/journal_entries.json';

INSERT INTO stg.journal_entry_line (
  document_id, line_no, account_code, posting_key, debit_amount, credit_amount, amount,
  cost_center, profit_center, tax_code, raw_source_path, raw_record_index
)
SELECT
  COALESCE(
    h.value -> 'header' ->> 'document_id',
    l.value ->> 'document_id',
    h.value ->> 'document_id'
  ),
  COALESCE(
    NULLIF(l.value ->> 'line_number', '')::INTEGER,
    NULLIF(l.value ->> 'line_no', '')::INTEGER,
    ROW_NUMBER() OVER (
      PARTITION BY COALESCE(
        h.value -> 'header' ->> 'document_id',
        l.value ->> 'document_id',
        h.value ->> 'document_id'
      )
      ORDER BY l.ordinality
    )::INTEGER
  ) AS line_no,
  COALESCE(l.value ->> 'account_code', l.value ->> 'gl_account'),
  l.value ->> 'posting_key',
  COALESCE(l.value ->> 'debit_amount', l.value ->> 'debit'),
  COALESCE(l.value ->> 'credit_amount', l.value ->> 'credit'),
  l.value ->> 'amount',
  l.value ->> 'cost_center',
  l.value ->> 'profit_center',
  l.value ->> 'tax_code',
  r.source_path,
  r.record_index
FROM raw.file_records r
JOIN LATERAL jsonb_array_elements(
  CASE
    WHEN jsonb_typeof(r.payload) = 'array' THEN r.payload
    ELSE jsonb_build_array(r.payload)
  END
) h(value) ON TRUE
JOIN LATERAL jsonb_array_elements(COALESCE(h.value -> 'lines', '[]'::jsonb)) WITH ORDINALITY l(value, ordinality) ON TRUE
WHERE r.source_path LIKE '%/journal_entries.json';

INSERT INTO core.gl_account (account_code, account_name, account_type, country, industry, parent_account_code)
SELECT DISTINCT
  s.account_code,
  s.account_name,
  s.account_type,
  s.country,
  s.industry,
  s.parent_account_code
FROM stg.chart_of_accounts s
WHERE COALESCE(s.account_code, '') <> ''
ON CONFLICT (account_code) DO UPDATE SET
  account_name = EXCLUDED.account_name,
  account_type = EXCLUDED.account_type,
  country = EXCLUDED.country,
  industry = EXCLUDED.industry,
  parent_account_code = EXCLUDED.parent_account_code;

INSERT INTO core.vendor (vendor_id, vendor_name, country)
SELECT DISTINCT s.vendor_id, s.vendor_name, s.country
FROM stg.vendors s
WHERE COALESCE(s.vendor_id, '') <> ''
ON CONFLICT (vendor_id) DO UPDATE SET
  vendor_name = EXCLUDED.vendor_name,
  country = EXCLUDED.country;

INSERT INTO core.customer (customer_id, customer_name, country)
SELECT DISTINCT s.customer_id, s.customer_name, s.country
FROM stg.customers s
WHERE COALESCE(s.customer_id, '') <> ''
ON CONFLICT (customer_id) DO UPDATE SET
  customer_name = EXCLUDED.customer_name,
  country = EXCLUDED.country;

WITH invalid_headers AS (
  SELECT
    s.*,
    CASE
      WHEN COALESCE(s.document_id, '') = '' THEN 'missing_document_id'
      WHEN COALESCE(s.company_code, '') = '' THEN 'missing_company_code'
      WHEN COALESCE(s.posting_date, '') !~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' THEN 'invalid_posting_date_format'
      ELSE NULL
    END AS reason_code
  FROM stg.journal_entry_header s
)
INSERT INTO audit.reject_journal_entry_header (
  document_id, company_code, posting_date, reason_code, reason_detail, raw_source_path, raw_record_index
)
SELECT
  i.document_id,
  i.company_code,
  i.posting_date,
  i.reason_code,
  'Header rejected during validation',
  i.raw_source_path,
  i.raw_record_index
FROM invalid_headers i
WHERE i.reason_code IS NOT NULL;

WITH valid_headers AS (
  SELECT s.*
  FROM stg.journal_entry_header s
  LEFT JOIN audit.reject_journal_entry_header r
    ON r.document_id IS NOT DISTINCT FROM s.document_id
   AND r.raw_source_path IS NOT DISTINCT FROM s.raw_source_path
   AND r.raw_record_index IS NOT DISTINCT FROM s.raw_record_index
  WHERE r.id IS NULL
)
INSERT INTO core.journal_entry_header (
  document_id, company_code, fiscal_year, fiscal_period, posting_date, document_date, created_at_ts,
  document_type, currency, exchange_rate, reference, header_text, created_by, source, business_process
)
SELECT DISTINCT
  v.document_id,
  v.company_code,
  NULLIF(v.fiscal_year, '')::INTEGER,
  NULLIF(v.fiscal_period, '')::INTEGER,
  NULLIF(v.posting_date, '')::DATE,
  NULLIF(v.document_date, '')::DATE,
  NULLIF(v.created_at, '')::TIMESTAMPTZ,
  v.document_type,
  v.currency,
  NULLIF(v.exchange_rate, '')::NUMERIC(18,6),
  v.reference,
  v.header_text,
  v.created_by,
  v.source,
  v.business_process
FROM valid_headers v
ON CONFLICT (document_id) DO UPDATE SET
  company_code = EXCLUDED.company_code,
  fiscal_year = EXCLUDED.fiscal_year,
  fiscal_period = EXCLUDED.fiscal_period,
  posting_date = EXCLUDED.posting_date,
  document_date = EXCLUDED.document_date,
  created_at_ts = EXCLUDED.created_at_ts,
  document_type = EXCLUDED.document_type,
  currency = EXCLUDED.currency,
  exchange_rate = EXCLUDED.exchange_rate,
  reference = EXCLUDED.reference,
  header_text = EXCLUDED.header_text,
  created_by = EXCLUDED.created_by,
  source = EXCLUDED.source,
  business_process = EXCLUDED.business_process;

WITH line_eval AS (
  SELECT
    s.*,
    h.document_id AS hdr_document_id,
    a.account_code AS acc_account_code,
    CASE
      WHEN COALESCE(s.document_id, '') = '' THEN 'missing_document_id'
      WHEN s.line_no IS NULL THEN 'missing_line_no'
      WHEN COALESCE(s.account_code, '') = '' THEN 'missing_account_code'
      WHEN COALESCE(s.debit_amount, '') <> '' AND s.debit_amount !~ '^-?[0-9]+(\.[0-9]+)?$' THEN 'invalid_debit_amount'
      WHEN COALESCE(s.credit_amount, '') <> '' AND s.credit_amount !~ '^-?[0-9]+(\.[0-9]+)?$' THEN 'invalid_credit_amount'
      WHEN COALESCE(s.amount, '') <> '' AND s.amount !~ '^-?[0-9]+(\.[0-9]+)?$' THEN 'invalid_amount'
      WHEN h.document_id IS NULL THEN 'missing_header_reference'
      WHEN a.account_code IS NULL THEN 'missing_account_reference'
      ELSE NULL
    END AS reason_code
  FROM stg.journal_entry_line s
  LEFT JOIN core.journal_entry_header h ON h.document_id = s.document_id
  LEFT JOIN core.gl_account a ON a.account_code = s.account_code
)
INSERT INTO audit.reject_journal_entry_line (
  document_id, line_no, account_code, debit_amount, credit_amount, amount,
  reason_code, reason_detail, raw_source_path, raw_record_index
)
SELECT
  l.document_id,
  l.line_no,
  l.account_code,
  l.debit_amount,
  l.credit_amount,
  l.amount,
  l.reason_code,
  'Line rejected during validation',
  l.raw_source_path,
  l.raw_record_index
FROM line_eval l
WHERE l.reason_code IS NOT NULL;

WITH valid_lines AS (
  SELECT s.*
  FROM stg.journal_entry_line s
  LEFT JOIN audit.reject_journal_entry_line r
    ON r.document_id IS NOT DISTINCT FROM s.document_id
   AND r.line_no IS NOT DISTINCT FROM s.line_no
   AND r.raw_source_path IS NOT DISTINCT FROM s.raw_source_path
   AND r.raw_record_index IS NOT DISTINCT FROM s.raw_record_index
  WHERE r.id IS NULL
)
INSERT INTO core.journal_entry_line (
  document_id, line_no, account_code, posting_key, debit_amount, credit_amount,
  amount, cost_center, profit_center, tax_code
)
SELECT
  v.document_id,
  v.line_no,
  v.account_code,
  v.posting_key,
  NULLIF(v.debit_amount, '')::NUMERIC(18,2),
  NULLIF(v.credit_amount, '')::NUMERIC(18,2),
  NULLIF(v.amount, '')::NUMERIC(18,2),
  v.cost_center,
  v.profit_center,
  v.tax_code
FROM valid_lines v
ON CONFLICT (document_id, line_no) DO UPDATE SET
  account_code = EXCLUDED.account_code,
  posting_key = EXCLUDED.posting_key,
  debit_amount = EXCLUDED.debit_amount,
  credit_amount = EXCLUDED.credit_amount,
  amount = EXCLUDED.amount,
  cost_center = EXCLUDED.cost_center,
  profit_center = EXCLUDED.profit_center,
  tax_code = EXCLUDED.tax_code;

INSERT INTO audit.pipeline_events (stage, status, detail)
VALUES ('transform', 'ok', 'Transform completed with reject logging');
