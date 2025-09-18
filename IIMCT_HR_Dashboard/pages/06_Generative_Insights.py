
import streamlit as st
from utils import generative_summary

st.set_page_config(page_title="Generative Insights", page_icon="🧠", layout="wide")
with open('assets/styles.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from app import _load, uploaded
df = _load(uploaded)

st.header("🧠 Generative insights (textual analysis)")

scope = st.text_input("Scope label (optional)", value="Current filters")
if st.button("Generate narrative"):
    st.markdown(generative_summary(df, scope_label=scope))
else:
    st.caption("Click the button to generate a clean, human‑readable summary of the current dataset.")
