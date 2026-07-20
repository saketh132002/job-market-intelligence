-- q_salary_by_skill: skill x state pay, disclosed-only, n>=30 floor
-- (floor stored at build, applied at serve — Day 14, Decision 3)
SELECT
  skill,
  skill_group,
  state,
  p25_salary,
  median_salary,
  p75_salary,
  sample_size
FROM jobmarket.gold.gold_skill_salary
WHERE sample_size >= 30
ORDER BY median_salary DESC