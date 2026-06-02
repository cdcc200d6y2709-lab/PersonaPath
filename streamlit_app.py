#Import Libary
import streamlit as st
import pandas as pd
import ast
import matplotlib.pyplot as plt
from matplotlib_venn import venn2

st.set_page_config(page_title="Persona Path Dashboard", layout="wide")

#Load Data
link = "https://docs.google.com/spreadsheets/d/e/2PACX-1vROJuujRIp7PPekPvkvXbgAWflOnPOSSyaOFDjhQYcIUINeOIrn_KrRLivysD3PB0G21lhVh27sHUrW/pub?output=csv"
df_processed = pd.read_csv(link)
st.title("Persona Path Dashboard")

#Prepocessing
df_processed["deskripsi"] = df_processed["deskripsi"].apply(ast.literal_eval)
df_exploded = df_processed.explode('deskripsi').reset_index(drop=True)

#Sidebar Filter
st.sidebar.header("Filter Dashboard")
selected_level = st.sidebar.selectbox(
    "Pilih Level",
    sorted(df_exploded["level"].dropna().unique()),
    index=0
)

top_n = st.sidebar.slider(
    "Jumlah Top Skill",
    min_value=3,
    max_value=15,
    value=5
)

#QA vs Tester
qa_tester = df_exploded[
    (df_exploded["posisi"].isin(["quality assurance", "tester"])) &
    (df_exploded["level"] == selected_level)
]

skill_compare = pd.crosstab(
    qa_tester["deskripsi"],
    qa_tester["posisi"],
    normalize="columns"
) * 100

#Pastikan Kolom Ada
for col in ["quality assurance", "tester"]:
    if col not in skill_compare.columns:
        skill_compare[col] = 0

skill_compare["total"] = (
    skill_compare["quality assurance"] +
    skill_compare["tester"]
)

top_skill = (
    skill_compare
    .sort_values("total", ascending=False)
    .head(top_n)
    .reset_index()
)

qa_skill = set(
    qa_tester[
        qa_tester["posisi"] == "quality assurance"
    ]["deskripsi"]
)

tester_skill = set(
    qa_tester[
        qa_tester["posisi"] == "tester"
    ]["deskripsi"]
)

if len(qa_skill | tester_skill) > 0:
    jaccard_qa = len(qa_skill & tester_skill) / len(qa_skill | tester_skill)
else:
    jaccard_qa = 0

#DA vs BA
da_ba = df_exploded[
    (df_exploded["posisi"].isin([
        "data analyst",
        "business analyst"
    ])) &
    (df_exploded["level"] == selected_level)
].copy()

skill = pd.crosstab(
    da_ba["deskripsi"],
    da_ba["posisi"],
    normalize="columns"
) * 100

for col in ["data analyst", "business analyst"]:
    if col not in skill.columns:
        skill[col] = 0

skill["gap"] = (
    skill["data analyst"]
    - skill["business analyst"]
)

plot_gap = (
    skill
    .reindex(
        skill["gap"]
        .abs()
        .sort_values(ascending=False)
        .index
    )
    .head(top_n)
    .reset_index()
)

da_skill = set(
    da_ba[
        da_ba["posisi"] == "data analyst"
    ]["deskripsi"]
)

ba_skill = set(
    da_ba[
        da_ba["posisi"] == "business analyst"
    ]["deskripsi"]
)

if len(da_skill | ba_skill) > 0:
    jaccard_da_ba = len(da_skill & ba_skill) / len(da_skill | ba_skill)
else:
    jaccard_da_ba = 0

metric1, metric2, metric3, metric4 = st.columns(4)
metric1.metric(
    "Jumlah Skill QA",
    len(qa_skill)
)
metric2.metric(
    "Jumlah Skill Tester",
    len(tester_skill)
)
metric3.metric(
    "Jumlah Skill DA",
    len(da_skill)
)
metric4.metric(
    "Jumlah Skill BA",
    len(ba_skill)
)

#Tab
tab1, tab2 = st.tabs([
    "Quality Assurance vs Tester",
    "Data Analyst vs Bussiness Analyst"
])

#Tab 1
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Perbandingan Persentase Skill Quality Assurance vs Tester")
        fig1, ax1 = plt.subplots(figsize=(5,4))
        top_skill.plot(
            x="deskripsi",
            y=["quality assurance", "tester"],
            kind="bar",
            ax=ax1
        )

        ax1.set_title("Perbandingan Persentase Skill Quality Assurance vs Tester")
        ax1.set_xlabel("Skill")
        ax1.set_ylabel("Persentase (%)")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig1, use_container_width=False)

    with col2:
        st.subheader("Overlap Skill Quality Assurance & Tester")
        fig2, ax2 = plt.subplots(figsize=(3,2))
        ax2.set_title("Overlap Skill Quality Assurance & Tester")
        venn2(
            [qa_skill, tester_skill],
            set_labels=("Quality Assurance", "Tester"),
            ax=ax2
        )
        st.pyplot(fig2, use_container_width=False)
        st.markdown(f"Jaccard Similarity: {jaccard_qa:.1%}")

#Tab 2
with tab2:
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Top Skill Pembeda: Business Analyst vs Data Analyst")
        fig3, ax3 = plt.subplots(figsize=(6,4))
        
        ax3.barh(
            plot_gap["deskripsi"],
            plot_gap["gap"]
        )
        ax3.axvline(
            x=0,
            linestyle="--"
        )
        ax3.set_title(
            "Top Skill Pembeda"
            "\nBusiness Analyst vs Data Analyst"
        )
        ax3.set_xlabel("Skill Gap (%)")
        ax3.set_ylabel("Skill")
        ax3.tick_params(axis="both")
        plt.tight_layout()
        st.pyplot(fig3, use_container_width=False)
    with col4:
        st.subheader("Overlap Skill Data Analyst & Business Analyst")
        fig4, ax4 = plt.subplots(figsize=(3,3))
        venn2(
            [da_skill, ba_skill],
            set_labels=(
                "Data Analyst",
                "Business Analyst"
            ),
            ax = ax4
        )
        ax4.set_title("Overlap Skill Data Analyst & Business Analyst")
        plt.tight_layout()
        st.pyplot(fig4, use_container_width=False)
        st.markdown(f"Jaccard Similarity: {jaccard_da_ba:.1%}")