\pset format aligned
\pset tuples_only off

SELECT 'core.gl_account count' AS metric, COUNT(*)::TEXT AS value FROM core.gl_account
UNION ALL
SELECT 'core.customer count', COUNT(*)::TEXT FROM core.customer
UNION ALL
SELECT 'core.vendor count', COUNT(*)::TEXT FROM core.vendor
UNION ALL
SELECT 'core.journal_entry_header count', COUNT(*)::TEXT FROM core.journal_entry_header
UNION ALL
SELECT 'core.journal_entry_line count', COUNT(*)::TEXT FROM core.journal_entry_line
UNION ALL
SELECT 'reject header count', COUNT(*)::TEXT FROM audit.reject_journal_entry_header
UNION ALL
SELECT 'reject line count', COUNT(*)::TEXT FROM audit.reject_journal_entry_line
ORDER BY metric;

SELECT reason_code, COUNT(*) AS reject_count
FROM audit.reject_journal_entry_line
GROUP BY reason_code
ORDER BY reject_count DESC, reason_code;

SELECT h.document_id,
       COALESCE(SUM(COALESCE(l.debit_amount, 0)), 0) AS total_debit,
       COALESCE(SUM(COALESCE(l.credit_amount, 0)), 0) AS total_credit,
       COALESCE(SUM(COALESCE(l.debit_amount, 0)), 0) - COALESCE(SUM(COALESCE(l.credit_amount, 0)), 0) AS delta
FROM core.journal_entry_header h
LEFT JOIN core.journal_entry_line l ON l.document_id = h.document_id
GROUP BY h.document_id
HAVING COALESCE(SUM(COALESCE(l.debit_amount, 0)), 0) <> COALESCE(SUM(COALESCE(l.credit_amount, 0)), 0)
ORDER BY ABS(COALESCE(SUM(COALESCE(l.debit_amount, 0)), 0) - COALESCE(SUM(COALESCE(l.credit_amount, 0)), 0)) DESC
LIMIT 50;
