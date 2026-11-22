-- queries.sql
-- SQL queries for exploring the A/B test dataset.
-- These are run against an in-memory SQLite DB in analysis.py,
-- but can also be used in any SQL tool that supports the CSV as a table.

-- ── 1. Overall Summary by Group ─────────────────────────────────────────────
SELECT
    "group"                              AS group_name,
    COUNT(*)                             AS total_users,
    SUM(converted)                       AS total_conversions,
    ROUND(AVG(converted) * 100, 2)       AS conversion_rate_pct,
    ROUND(AVG(session_duration_sec), 1)  AS avg_session_sec
FROM ab_test
GROUP BY "group"
ORDER BY "group";


-- ── 2. Sanity Check: Any duplicate user_ids? ─────────────────────────────────
SELECT user_id, COUNT(*) AS occurrences
FROM ab_test
GROUP BY user_id
HAVING COUNT(*) > 1;


-- ── 3. Distribution of session duration by group (bucketed) ──────────────────
SELECT
    "group"                                   AS group_name,
    CASE
        WHEN session_duration_sec <  60  THEN '< 1 min'
        WHEN session_duration_sec < 120  THEN '1–2 min'
        WHEN session_duration_sec < 300  THEN '2–5 min'
        ELSE '5+ min'
    END                                       AS duration_bucket,
    COUNT(*)                                  AS users
FROM ab_test
GROUP BY "group", duration_bucket
ORDER BY "group", duration_bucket;


-- ── 4. Conversion rate among users who stayed > 2 minutes ────────────────────
SELECT
    "group"                             AS group_name,
    COUNT(*)                            AS users,
    SUM(converted)                      AS conversions,
    ROUND(AVG(converted) * 100, 2)      AS conversion_rate_pct
FROM ab_test
WHERE session_duration_sec >= 120
GROUP BY "group"
ORDER BY "group";


-- ── 5. Quick check: group sizes are roughly balanced ─────────────────────────
SELECT
    "group",
    COUNT(*) AS n,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM ab_test), 1) AS pct_of_total
FROM ab_test
GROUP BY "group";