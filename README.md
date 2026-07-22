# Job Market Intelligence Platform

**An end-to-end data platform that reads ~117,000 real job postings to answer:
what skills does the market demand, what do they pay, and what goes with what.**

Built on Databricks (PySpark · Delta Lake · Databricks SQL), with a medallion
lakehouse pipeline, dictionary + LLM skill extraction, and a live analytics
dashboard.

<!-- TODO Day 25: dashboard screenshot here -->

---

## What the data shows

Three findings from the current dataset (a 2024 snapshot of ~117k US postings,
salaries from the ~24% that disclose pay, every salary cell floored at n≥30):

### 1. The machine-learning premium is real and large
ML and AI skills command a **$40–60k median premium** over core programming in
the same states. In California: machine learning $176,800 and LLM skills
$191,000, versus Python $150,000 and SQL $134,000. The pattern repeats in
New York (ML $192,000) and Washington ($178,910). For anyone choosing what to
learn, this quantifies the payoff of specializing.

### 2. The same skill pays very differently by geography
Location moves pay as much as skill choice. Python's median runs $132,500 in
Illinois but $155,000 in New York; Excel spans $62,500 (Indiana) to $97,500
(DC and Washington). A skill's worth isn't fixed — where you work still shapes it.

### 3. Salary *spread* reveals which skills are seniority-gated
The shape of a skill's salary distribution, not just its median, tells you
whether it's an entry-door or a senior-gated skill. React shows a collapsed
25th percentile ($60,000–71,500 across CA/WA/NY) against six-figure medians —
a long junior tail. Kubernetes holds a 25th percentile of $144,560 in
California: even its lowest-paid postings are senior. Same market, opposite
distribution shapes. (Spread is suggestive of seniority, not a direct measure
of it.)

---

## How it works

A medallion lakehouse — data refined in stages, each rebuildable from the one
below it:

```
Adzuna API ─┐
Kaggle dump ─┼─► BRONZE (raw, immutable) ─► SILVER (typed, normalized,
             ┘                                       deduped) ─► skill extraction
                                                                      │
                                    ┌─────────────────────────────────┤
                                    ▼                                  ▼
                          GOLD (demand, salary, pairs,          Databricks SQL
                                role summary)                   dashboard
```

- **Bronze** — two ingestion patterns (a Kaggle historical backfill and a live
  Adzuna API feed) land untouched, with source and timestamp metadata.
- **Silver** — JSON/CSV parsed against explicit schemas; job titles normalized
  (24.7% distinct-title compression) with seniority extracted; salaries
  annualized to USD (98.5% conversion, 19 unit tests); postings deduplicated
  via windowed survivorship on deterministic hash IDs; assembled into one table
  via idempotent `MERGE INTO` (117,292 distinct postings).
- **Skill extraction** — a 134-skill dictionary matches 226,641 skill mentions
  across 69% of postings; audited for precision (see below) and cross-checked
  against an LLM.
- **Gold** — four aggregate tables (demand, salary, co-occurrence pairs, role
  summary), each carrying explicit honesty rules: within-source percentages,
  disclosed-only salaries, an n≥30 sample floor, soft-skill segregation.
- **Serving** — Databricks SQL queries feed a dashboard with filters; a
  Streamlit app is planned.

Notebooks are organized `notebooks/01_setup` through `05_gold`; serving queries
live in `sql/`.

---

## Engineering highlights

A few decisions that shaped the build:

- **Dictionary vs LLM skill extraction — measured, not assumed.** Rather than
  defaulting to an LLM, both approaches ran on 400 postings and were compared.
  The dictionary is deterministic and free at corpus scale; the LLM wins on
  context (it extracts skills like "Go" and "C" that a keyword matcher can't
  safely disambiguate) but adds cost and ~25% concept-noise. Verdict: the
  dictionary extracts, the LLM audits. (The `match_method` column supports
  running both.)

- **A precision audit that changed the dictionary.** Sampling matched postings
  by hand revealed that the skill "R" was 88% false positives (matching "R&D"
  and requisition IDs, not the language) and "Workday" 90% (ATS boilerplate).
  Both were fixed with context-bearing aliases; the false-positive rates are
  documented, not hidden.

- **Salary parsing that refuses to guess.** Pay-period labels turned out to be
  dirty (hourly-labeled rows carrying yearly figures). Every conversion is
  gated by a plausibility range; ambiguous values become null rather than
  fabricated. A verification pass caught an $85M "salary" that a planned-but-
  unbuilt sanity rule had missed.

- **Idempotency, proven.** The Bronze→Silver assembly uses `MERGE INTO` on
  deterministic hash IDs; rerunning it produces zero inserts and zero updates —
  a property demonstrated, not assumed.

---

## Honest limitations

- **The historical backfill is a single-month snapshot** (Apr 2024). It gives a
  rich cross-sectional picture but no trend — trends come from the live Adzuna
  feed, which thickens as daily ingestion accumulates.
- **Only ~24% of postings disclose salary.** All salary figures are built from
  that disclosed subset, floored at n≥30 per skill×state cell.
- **Adzuna descriptions are truncated at 500 characters**, yielding fewer skills
  per posting than the full-text Kaggle data — so demand percentages are
  computed within-source, never blended.
- **Skill extraction is dictionary-based** (134 skills). Skills phrased
  unusually, or outside the dictionary, are missed by design; the LLM comparison
  measures the gap.

---

<!-- TODO Day 25: architecture diagram image, setup/run instructions,
     screenshots, demo GIF, tech-stack badges -->
