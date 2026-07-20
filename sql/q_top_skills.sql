-- q_top_skills: top technical skills, cross-sectional view (Kaggle only)
-- Rules encoded: within-source pct (Day 14), soft group excluded (Day 12/13)
SELECT
  skill,
  skill_group,
  posting_count,
  pct_of_postings
FROM jobmarket.gold.gold_skill_demand_monthly
WHERE source = 'kaggle_backfill'
  AND skill_group != 'soft'
ORDER BY posting_count DESC
LIMIT 15