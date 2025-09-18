import streamlit as st
import pandas as pd
from pathlib import Path
from utils import load_data, currency, inject_css

st.set_page_config(page_title="IIMCT HR Budget Dashboard", page_icon="📊", layout="wide")
inject_css()

st.title("📊 IIMCT HR Budget & Org Dashboard")
st.caption("Clean. Simple. Robust — iPadOS‑style HR analytics for IIMCT Group")

# Data loader (sidebar)
st.sidebar.header("Data & Filters")
DEFAULT_PATH = Path(__file__).resolve().parent / 'data' / 'IIMCT Group HR Position wise Budget.csv'

uploaded = st.sidebar.file_uploader("Upload CSV (IIMCT Position-wise Budget)", type=['csv'])

@st.cache_data(show_spinner=True)
def _load(_uploaded_bytes):
    if _uploaded_bytes is not None:
        return load_data(_uploaded_bytes)
    else:
        if DEFAULT_PATH.exists():
            return load_data(DEFAULT_PATH)
        else:
            raise FileNotFoundError("CSV not found. Upload it from the sidebar or place it in ./data/")

try:
    df = _load(uploaded)
except Exception as e:
    st.warning("Place your CSV in ./data or upload it using the control in the left sidebar.")
    st.stop()

# Global filters
org = st.sidebar.multiselect('Org', sorted(df['Org'].dropna().unique().tolist()) if 'Org' in df.columns else [])
region = st.sidebar.multiselect('Region', sorted(df['Region'].dropna().unique().tolist()) if 'Region' in df.columns else [])
su = st.sidebar.multiselect("SU (Business Unit)", sorted(df['SU'].dropna().unique().tolist()) if 'SU' in df.columns else [])
dept = st.sidebar.multiselect('Department', sorted(df['Department'].dropna().unique().tolist()) if 'Department' in df.columns else [])
cat = st.sidebar.multiselect('Salary Category', sorted(df['SalaryCategory'].dropna().unique().tolist()) if 'SalaryCategory' in df.columns else [])
status = st.sidebar.multiselect('Status', sorted(df['Status'].dropna().unique().tolist()) if 'Status' in df.columns else [])
role_query = st.sidebar.text_input('Designation contains…', '')

min_pay, max_pay = st.sidebar.slider('Gross Pay range (₨)', 0, int(df.get('GrossPay', pd.Series([0])).fillna(0).max() or 1_000_000), (0, int(df.get('GrossPay', pd.Series([0])).fillna(0).max() or 1_000_000)), step=1000)

if st.sidebar.button('Reset filters'):
    st.experimental_rerun()

# Apply filters
f = df.copy()
if 'Org' in f.columns and org: f = f[f['Org'].isin(org)]
if 'Region' in f.columns and region: f = f[f['Region'].isin(region)]
if 'SU' in f.columns and su: f = f[f['SU'].isin(su)]
if 'Department' in f.columns and dept: f = f[f['Department'].isin(dept)]
if 'SalaryCategory' in f.columns and cat: f = f[f['SalaryCategory'].isin(cat)]
if 'Status' in f.columns and status: f = f[f['Status'].isin(status)]
if role_query.strip():
    left = f.get('BudDesignation', pd.Series([], dtype=str)).fillna('').str.contains(role_query, case=False)
    right = f.get('ActDesignation', pd.Series([], dtype=str)).fillna('').str.contains(role_query, case=False)
    mask = left | right
    f = f[mask]

if 'GrossPay' in f.columns:
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

st.markdown("### Preview (filtered data)")
st.dataframe(f.head(50))

st.download_button(
    label="⬇️ Download filtered CSV",
    data=f.to_csv(index=False).encode('utf-8'),
    file_name='iimct_hr_filtered.csv',
    mime='text/csv'
)