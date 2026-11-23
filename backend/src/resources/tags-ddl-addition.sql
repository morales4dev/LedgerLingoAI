-- ==============================================================================
-- DDL Addition for Layer 1: Semantic Tag Master & Many-to-Many Bridge
-- ==============================================================================

CREATE TABLE core.tag (
    tag_code     TEXT PRIMARY KEY,
    tag_name     TEXT NOT NULL,
    tag_category TEXT NOT NULL, -- e.g., 'pnl_line', 'bs_line', 'ebitda_adjustment'
    description  TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE core.gl_account_tag (
    account_code TEXT NOT NULL,
    tag_code     TEXT NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_gl_account_tag PRIMARY KEY (account_code, tag_code),
    CONSTRAINT fk_gat_account FOREIGN KEY (account_code)
        REFERENCES core.gl_account (account_code) ON DELETE CASCADE,
    CONSTRAINT fk_gat_tag FOREIGN KEY (tag_code)
        REFERENCES core.tag (tag_code) ON DELETE RESTRICT
);

-- Index to optimize EXISTS subqueries from journal_entry_line -> gl_account_tag
CREATE INDEX idx_gl_account_tag_tag_code_account
    ON core.gl_account_tag (tag_code, account_code);
