
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import currency

st.set_page_config(page_title="Roles Explorer", page_icon="🧩", layout="wide")
with open('assets/styles.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from app import _load, uploaded
df = _load(uploaded)

st.header("🧩 Roles / Designation explorer")

role = st.selectbox("Choose a role (Budgeted Designation)", sorted(df['BudDesignation'].dropna().unique()))
role_df = df[df['BudDesignation'] == role]

c1,c2,c3 = st.columns(3)
with c1:
    st.metric("Positions", f"{int(role_df['Positions'].fillna(0).sum()):,}")
with c2:
    st.metric("Annual Budget", currency(role_df['ImpactAnnual'].sum()))
with c3:
    st.metric("Median Gross Pay", currency(role_df['GrossPay'].median()))

fig = px.histogram(role_df, x='GrossPay', nbins=30, color='Status', barmode='overlay')
fig.update_layout(yaxis_title='Count', xaxis_title='Gross Pay')
st.plotly_chart(fig, use_container_width=True)

st.markdown("#### Breakdown by Org / Region / Department")
agg = role_df.groupby(['Org','Region','Department'], dropna=False)[['Positions','ImpactAnnual']].sum().reset_index()
st.dataframe(agg)
