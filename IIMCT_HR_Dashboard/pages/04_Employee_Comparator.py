
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils import salary_percentile, currency

st.set_page_config(page_title="Employee Comparator", page_icon="🆚", layout="wide")
with open('assets/styles.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from app import _load, uploaded
df = _load(uploaded)

st.header("🆚 Employee Comparator")

emp = st.text_input("Enter Emp. ID or Name", placeholder="e.g., 2466 or 'Muhammad' ")
person, peers = df.hr.peers(emp)

if person is None:
    st.info("Type an Emp. ID (exact) or part of a Name to compare within their Budgeted Designation cohort.")
    st.stop()

role = person['BudDesignation']
st.subheader(f"{person.get('Name','—')} — {role}")

pay = person.get('GrossPay', np.nan)
perc = salary_percentile(peers['GrossPay'], pay)

c1,c2,c3 = st.columns(3)
with c1:
    st.metric("Gross Pay", currency(pay))
with c2:
    st.metric("Percentile in role", f"{perc:.1f}%" if perc is not None else '—')
with c3:
    st.metric("Peers in cohort", f"{len(peers):,}")

fig = px.histogram(peers, x='GrossPay', nbins=30, title=f"Gross Pay distribution — {role}")
fig.add_vline(x=pay, line_dash='dash', line_color='red')
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)

st.markdown("#### Peers table")
cols = ['EmpID','Name','BudDesignation','Department','GrossPay']
st.dataframe(peers[cols].sort_values('GrossPay'))
