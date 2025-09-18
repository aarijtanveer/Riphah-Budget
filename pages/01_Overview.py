import streamlit as st
import plotly.express as px
from pathlib import Path
from utils import inject_css
from app import _load, uploaded

st.set_page_config(page_title="Overview", page_icon="🧭", layout="wide")
inject_css()

df = _load(uploaded)

st.header("🧭 Overview")

k = df.hr.kpis()
c1,c2,c3,c4,c5 = st.columns(5)
for c, label, val in [
    (c1,'Annual Budget', f"₨ {k['annual_budget']:,.0f}"),
    (c2,'Monthly Budget', f"₨ {k['monthly_budget']:,.0f}"),
    (c3,'Total Positions', f"{k['total_positions']:,}"),
    (c4,'Active Headcount', f"{k['headcount']:,}"),
    (c5,'Increment Pool', f"₨ {k['increment_total']:,.0f}")
]:
    with c:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-label">{label}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-value">{val}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

if 'ImpactAnnual' in df.columns:
    st.markdown("#### Org → Region → SU → Department (Sunburst)")
    g = df.groupby(['Org','Region','SU','Department'], dropna=False)['ImpactAnnual'].sum().reset_index()
    fig = px.sunburst(g, path=['Org','Region','SU','Department'], values='ImpactAnnual', color='ImpactAnnual', color_continuous_scale='Blues')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Budget by Salary Category")
    cat = df.groupby('SalaryCategory', dropna=False)['ImpactAnnual'].sum().reset_index().sort_values('ImpactAnnual', ascending=False)
    fig2 = px.bar(cat, x='SalaryCategory', y='ImpactAnnual', text='ImpactAnnual', color='SalaryCategory', color_discrete_sequence=px.colors.qualitative.Set2)
    fig2.update_yaxes(title='Annual Budget')
    fig2.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Top 15 Departments by Annual Spend")
    by_dept = df.groupby('Department', dropna=False)['ImpactAnnual'].sum().sort_values(ascending=False).head(15).reset_index()
    fig3 = px.bar(by_dept, x='ImpactAnnual', y='Department', orientation='h', text='ImpactAnnual', color='ImpactAnnual', color_continuous_scale='Teal')
    fig3.update_traces(texttemplate='%{text:,.0f}')
    st.plotly_chart(fig3, use_container_width=True)