import streamlit as st
import pandas as pd
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

st.title("Job Market Intelligence")
st.caption("Skills, salaries, and demand from ~117k real job postings · "
           "data snapshot: August 2026")

@st.cache_data
def load(name):
    return pd.read_parquet(DATA_DIR / f"{name}.parquet")

roles   = load("gold_role_summary")
pairs   = load("gold_skill_pairs")
demand  = load("gold_skill_demand_monthly")


tab_roles, tab_pairs, tab_trends = st.tabs(["🔍 Roles", "🔗 Skill pairs", "📊 Top skills"])

with tab_roles:
    st.subheader("Search a role")
    role = st.text_input("Job title", placeholder="e.g. data engineer, analyst, scientist")

    if not role:
        st.info("Type a role above to see its salary, demand, and top skills. "
                "Try: data engineer · data analyst · machine learning engineer")
    else:
        q = role.lower().strip()
        df = roles[roles["title_norm"].str.contains(q, na=False)] \
                 .sort_values("posting_count", ascending=False).head(20)

        if df.empty:
            st.warning(f"No roles found matching '{role}'. "
                       f"Try a broader term like 'engineer' or 'analyst'.")
        else:
            total_postings = int(df["posting_count"].sum())
            salaried = df[df["median_salary"].notna()]
            med = int(salaried["median_salary"].median()) if not salaried.empty else None

            c1, c2, c3 = st.columns(3)
            c1.metric("Matching postings", f"{total_postings:,}")
            c2.metric("Median salary", f"${med:,}" if med else "—")
            c3.metric("Locations", f"{df['state'].nunique()}")

            st.divider()
            st.caption("By location")

            for _, row in df.iterrows():
                state = row["state"] if row["state"] else "Unknown"
                raw = row["top_skills"]
                # top_skills is now a JSON string (we stringified on export)
                try:
                    skills = json.loads(raw) if raw else []
                except (TypeError, json.JSONDecodeError):
                    skills = []

                with st.container(border=True):
                    a, b, c = st.columns([1, 1, 3])
                    a.markdown(f"**{state}**")
                    a.caption(f"{row['posting_count']} postings")

                    if pd.notna(row["median_salary"]):
                        sample = row["salary_sample"]
                        if sample and sample < 3:
                            b.markdown(f"~${int(row['median_salary']):,}")
                            b.caption(f"⚠ from {sample} posting(s)")
                        else:
                            b.markdown(f"**${int(row['median_salary']):,}**")
                            b.caption("median")
                    else:
                        b.markdown("—")
                        b.caption("no salary data")

                    with c:
                        st.markdown("**Top skills**")
                        if skills:
                            tag_html = " ".join(
                                f"<span style='background:#E8EDF0; color:#1C1917; "
                                f"padding:2px 8px; border-radius:10px; margin:2px; "
                                f"display:inline-block; font-size:0.8em;'>{s}</span>"
                                for s in skills
                            )
                            st.markdown(tag_html, unsafe_allow_html=True)
                        else:
                            st.caption("no skills recorded")

with tab_pairs:
    st.subheader("What pairs with a skill?")
    st.caption("Skills that appear together far more than chance would predict")

    skill = st.text_input("Skill", placeholder="e.g. python, pandas, kubernetes",
                          key="pair_skill")

    if not skill:
        st.info("Type a skill to see what it's most often paired with. "
                "Try: pandas · kubernetes · spark")
    else:
        s = skill.lower().strip()
        mask = (pairs["skill_a"] == s) | (pairs["skill_b"] == s)
        matched = pairs[mask].copy()
        # the partner is whichever column ISN'T the searched skill
        matched["partner"] = matched.apply(
            lambda r: r["skill_b"] if r["skill_a"] == s else r["skill_a"], axis=1)
        matched = matched.sort_values("lift", ascending=False).head(15)

        if matched.empty:
            st.warning(f"No strong pairings found for '{skill}'. "
                       f"Try an exact skill name like 'pandas' or 'aws'.")
        else:
            st.markdown(f"**{s}** most often appears alongside:")
            for _, row in matched.iterrows():
                with st.container(border=True):
                    x, y = st.columns([2, 3])
                    x.markdown(f"**{row['partner']}**")
                    y.caption(f"{row['lift']:.0f}× more likely than chance  ·  "
                              f"co-occurs in {int(row['co_occurrence'])} postings")

with tab_trends:
    st.subheader("Most-demanded skills")
    st.caption("Share of postings mentioning each skill (2024 cross-section, "
               "technical skills only)")

    top = demand.sort_values("pct_of_postings", ascending=False).head(15)
    chart_df = top.set_index("skill")["pct_of_postings"]
    st.bar_chart(chart_df, horizontal=True)
    st.caption("Note: 'excel' includes ~10% verb matches (audited "
               "false-positive rate); soft skills excluded.")
