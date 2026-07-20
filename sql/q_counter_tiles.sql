-- q_counter_tiles: headline numbers for the dashboard's top row
SELECT
  COUNT(DISTINCT p.posting_id)                          AS postings_tracked,

  ROUND(MEDIAN(CASE WHEN p.salary_is_estimated = false
                    THEN (p.salary_min + COALESCE(p.salary_max, p.salary_min)) / 2
               END))                                    AS median_disclosed_salary,

  ROUND(AVG(CASE WHEN p.is_remote THEN 1 ELSE 0 END) * 100, 1)
                                                        AS remote_share_pct,

  (SELECT COUNT(DISTINCT skill)
   FROM jobmarket.silver.silver_posting_skills)         AS skills_tracked
FROM jobmarket.silver.silver_job_postings p