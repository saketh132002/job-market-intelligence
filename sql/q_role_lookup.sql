SELECT
  title_norm,
  state,
  posting_count,
  median_salary,
  salary_sample,
  top_skills,
  demand_trend
FROM jobmarket.gold.gold_role_summary
WHERE title_norm LIKE concat('%', :role, '%')
  AND posting_count >= 5
ORDER BY posting_count DESC
LIMIT 20