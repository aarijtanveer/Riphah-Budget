
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils import currency

st.set_page_config(page_title="Vacancies & Increments", page_icon="📈", layout="wide")
with open('assets/styles.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from app import _load, uploaded
df = _load(uploaded)

st.header("📈 Vacancies & Increment impact")

vac = df[df['IsVacant']]
inc = df[df['Increment'].notna() & (df['Increment']!=0)]

c1,c2,c3 = st.columns(3)
with c1: st.metric("Vacant positions", f"{int(vac['Positions'].fillna(0).sum()):,}")
with c2: st.metric("Vacancy annual budget", currency(vac['ImpactAnnual'].sum()))
with c3: st.metric("Increment pool", currency(inc['Increment'].sum()))

st.subheader("Scenario: Fill vacancy rate")
fill = st.slider("Assumed fill rate of vacant positions", 0, 100, 75, step=5)
months = st.slider("Effective months in year for new hires", 1, 12, 9)

projected = vac['GrossPay'].fillna(0).sum() * (fill/100) * months
st.info(f"Projected additional gross pay outflow: {currency(projected)}")

st.markdown("#### Vacancies by Department")
vv = vac.groupby('Department', dropna=False)[['Positions','ImpactAnnual']].sum().reset_index().sort_values('ImpactAnnual', ascending=False)
fig = px.bar(vv, x='ImpactAnnual', y='Department', orientation='h')
st.plotly_chart(fig, use_container_width=True)

st.markdown("#### Increments by Department")
ii = inc.groupby('Department', dropna=False)['Increment'].sum().reset_index().sort_values('Increment', ascending=False)
fig2 = px.bar(ii, x='Increment', y='Department', orientation='h', color='Increment')
st.plotly_chart(fig2, use_container_width=True)
