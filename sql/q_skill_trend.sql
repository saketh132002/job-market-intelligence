-- q_skill_trend: monthly demand for selected skills, Adzuna only
-- (the time-axis source; Kaggle is a snapshot). Current in-progress
-- month excluded — partial months fake negative growth (Day 14).
-- This chart THICKENS as wk5 daily ingestion accumulates history.
SELECT
  month,
  skill,
  posting_count,
  pct_of_postings,
  total_postings
FROM jobmarket.gold.gold_skill_demand_monthly
WHERE source = 'adzuna'
  AND skill IN ('python', 'sql', 'machine learning', 'llm', 'spark')
  AND month < DATE_TRUNC('month', CURRENT_DATE())
ORDER BY month, skill