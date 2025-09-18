
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import currency

st.set_page_config(page_title="Compensation", page_icon="💸", layout="wide")
with open('assets/styles.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from app import _load, uploaded
df = _load(uploaded)

st.header("💸 Compensation analytics")

existing = df[df['IsExisting'] & df['GrossPay'].notna()] 

c1,c2 = st.columns(2)
with c1:
    st.subheader("Distribution — Gross Pay by Designation")
    top_roles = existing['BudDesignation'].value_counts().head(20).index.tolist()
    d1 = existing[existing['BudDesignation'].isin(top_roles)]
    fig = px.violin(d1, y='GrossPay', x='BudDesignation', color='BudDesignation', box=True, points='all',
                    color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_layout(showlegend=False, xaxis_title='Designation', yaxis_title='Gross Pay')
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Boxplot — Gross Pay by Salary Category")
    fig2 = px.box(existing, x='SalaryCategory', y='GrossPay', color='SalaryCategory', points='all')
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Top 25 highest gross pay (Existing)")
cols = ['EmpID','Name','BudDesignation','Department','GrossPay','ImpactAnnual']
st.dataframe(existing[cols].sort_values('GrossPay', ascending=False).head(25))
