
import streamlit as st
import pandas as pd
from utils import load_data, currency

st.set_page_config(page_title="IIMCT HR Budget Dashboard", page_icon="📊", layout="wide")
with open('assets/styles.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("📊 IIMCT HR Budget & Org Dashboard")
st.caption("Clean. Simple. Robust — iPadOS‑style HR analytics for IIMCT Group")

# Data loader (sidebar)
st.sidebar.header("Data & Filters")

# Load default if present
DEFAULT_PATH = 'data/IIMCT Group HR Position wise Budget.csv'

uploaded = st.sidebar.file_uploader("Upload CSV (IIMCT Position-wise Budget)", type=['csv'])

@st.cache_data(show_spinner=True)
def _load(_uploaded_bytes):
    if _uploaded_bytes is not None:
        return load_data(_uploaded_bytes)
    else:
        return load_data(DEFAULT_PATH)

try:
    df = _load(uploaded)
except Exception as e:
    st.warning("Place your CSV in ./data or upload it using the control in the left sidebar.")
    st.exception(e)
    st.stop()

# Global filters
cols = st.sidebar.columns(2)
org = st.sidebar.multiselect('Org', sorted(df['Org'].dropna().unique().tolist()))
region = st.sidebar.multiselect('Region', sorted(df['Region'].dropna().unique().tolist()))
su = st.sidebar.multiselect("SU (Business Unit)", sorted(df['SU'].dropna().unique().tolist()))
dept = st.sidebar.multiselect('Department', sorted(df['Department'].dropna().unique().tolist()))
cat = st.sidebar.multiselect('Salary Category', sorted(df['SalaryCategory'].dropna().unique().tolist()))
status = st.sidebar.multiselect('Status', sorted(df['Status'].dropna().unique().tolist()))
role_query = st.sidebar.text_input('Designation contains…', '')

min_pay, max_pay = st.sidebar.slider('Gross Pay range (₨)', 0, int(df['GrossPay'].fillna(0).max() or 1000000), (0, int(df['GrossPay'].fillna(0).max() or 1000000)), step=1000)

if st.sidebar.button('Reset filters'):
    st.experimental_rerun()

# Apply filters
f = df.copy()
if org: f = f[f['Org'].isin(org)]
if region: f = f[f['Region'].isin(region)]
if su: f = f[f['SU'].isin(su)]
if dept: f = f[f['Department'].isin(dept)]
if cat: f = f[f['SalaryCategory'].isin(cat)]
if status: f = f[f['Status'].isin(status)]
if role_query.strip():
    mask = f['BudDesignation'].fillna('').str.contains(role_query, case=False) | f['ActDesignation'].fillna('').str.contains(role_query, case=False)
    f = f[mask]

f = f[(f['GrossPay'].fillna(0) >= min_pay) & (f['GrossPay'].fillna(0) <= max_pay)]

# KPIs
k = f.hr.kpis()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    st.markdown('<div class="kpi-label">Annual Budget</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-value">{currency(k["annual_budget"])}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
with kpi2:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    st.markdown('<div class="kpi-label">Monthly Budget</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-value">{currency(k["monthly_budget"])}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
with kpi3:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    st.markdown('<div class="kpi-label">Headcount (Existing)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-value">{k["headcount"]:,}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
with kpi4:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    st.markdown('<div class="kpi-label">Vacancy Budget</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-value">{currency(k["vacancy_budget"])}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.info("Use the **Pages** menu (left) to open specialized views: Overview, Compensation, Roles, Comparator, Vacancies & Increments, and Generative Insights.")

st.markdown("### Preview (filtered data)")
st.dataframe(f.head(50))

st.download_button(
    label="⬇️ Download filtered CSV",
    data=f.to_csv(index=False).encode('utf-8'),
    file_name='iimct_hr_filtered.csv',
    mime='text/csv'
)
