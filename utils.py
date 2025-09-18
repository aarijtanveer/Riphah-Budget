import re
from pathlib import Path
from typing import Optional
import pandas as pd
import numpy as np
import streamlit as st

DISPLAY_COLS = [
    'Org','Region','SU's Budget Sheet','Status','Emp. ID','Name','Actual Designation',
    'Budgeted Designation','Department','SAP SU','Personal SubArea','Salary Category',
    'Number of Positions','Gross Pay','Total Financial Impact per month','Total Financial Impact annual',
    'Increment','Annual Increase Salary With New Positions','Impact Months (Number of Months)'
]

NUMERIC_COLS = [
    'Number of Positions','Gross Pay','Total Financial Impact per month','Total Financial Impact annual',
    'Increment','Annual Increase Salary With New Positions','Impact Months (Number of Months)'
]

RENAMES = {
    'SU's Budget Sheet': 'SU',
    'Emp. ID': 'EmpID',
    'Actual Designation': 'ActDesignation',
    'Budgeted Designation': 'BudDesignation',
    'Personal SubArea': 'SubArea',
    'Salary Category': 'SalaryCategory',
    'Number of Positions': 'Positions',
    'Gross Pay': 'GrossPay',
    'Total Financial Impact per month': 'ImpactMonthly',
    'Total Financial Impact annual': 'ImpactAnnual',
    'Annual Increase Salary With New Positions': 'AnnualIncreaseWithNew',
    'Impact Months (Number of Months)': 'ImpactMonths'
}

ROLE_ALIASES = ["senior manager","sr. manager","sr manager","snr manager"]


def inject_css():
    root = Path(__file__).resolve().parent
    css_path = root / 'assets' / 'styles.css'
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def _clean_number(x):
    if pd.isna(x):
        return np.nan
    if isinstance(x, (int, float)):
        return x
    s = str(x)
    if s.strip() in ['-','', 'NaN', 'nan', 'None']:
        return np.nan
    s = s.replace('"','').replace("'","")
    s = re.sub(r"[^0-9.\-]", "", s)
    try:
        return float(s)
    except:
        return np.nan


def load_data(path_or_buffer) -> pd.DataFrame:
    # Read CSV, handle messy header/meta row like "Data, ..., Increment Rate ,6%"
    try:
        df = pd.read_csv(path_or_buffer, header=0, dtype=str, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(path_or_buffer, header=0, dtype=str, encoding='latin-1')

    # If the first column looks like 'Data' or the first rows are meta, find actual header
    if df.columns[0].lower().startswith('data') or (df.iloc[0,0] and str(df.iloc[0,0]).lower() in ['iimct','org']):
        header_idx = None
        for i in range(min(6, len(df))):
            if str(df.iloc[i,0]).strip().lower() in ['org']:
                header_idx = i
                break
        if header_idx is not None and header_idx != 0:
            new_header = df.iloc[header_idx]
            df = df.iloc[header_idx+1:].copy()
            df.columns = new_header

    # Keep only known columns if present
    keep = [c for c in DISPLAY_COLS if c in df.columns]
    df = df[keep].copy()

    # Clean numerics
    for c in NUMERIC_COLS:
        if c in df.columns:
            df[c] = df[c].apply(_clean_number)

    # Rename to short forms used in pages
    df = df.rename(columns=RENAMES)

    # Normalize
    for c in ['Status','Org','Region','Department','SAP SU','SubArea','SalaryCategory','ActDesignation','BudDesignation']:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()

    # Helpers
    if 'Positions' in df.columns:
        df['Positions'] = df['Positions'].fillna(1)
    df['IsVacant'] = df.get('Status','').str.lower().eq('vacant')
    df['IsExisting'] = df.get('Status','').str.lower().eq('existing')
    # Senior Manager flag
    desig = df.get('BudDesignation','').fillna('').str.lower()
    sm = False
    for a in ROLE_ALIASES:
        sm = sm | desig.str.contains(a)
    df['IsSeniorManager'] = sm

    return df


def currency(x: float) -> str:
    if pd.isna(x):
        return '—'
    return f"₨ {x:,.0f}"

@pd.api.extensions.register_dataframe_accessor("hr")
class HRAccessor:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj
    def kpis(self):
        df = self._obj
        existing = df[df['IsExisting']]
        return {
            'total_positions': int(df.get('Positions', 0).fillna(0).sum()) if 'Positions' in df.columns else len(df),
            'headcount': int(existing.get('Positions', 0).fillna(0).sum()) if 'Positions' in df.columns else len(existing),
            'annual_budget': float(df.get('ImpactAnnual', 0).fillna(0).sum()),
            'monthly_budget': float(df.get('ImpactMonthly', 0).fillna(0).sum()),
            'vacancy_budget': float(df[df['IsVacant']].get('ImpactAnnual', 0).fillna(0).sum()),
            'increment_total': float(df.get('Increment', 0).fillna(0).sum()),
        }
    def peers(self, emp_identifier: str, by: str = 'BudDesignation'):
        df = self._obj.copy()
        if not emp_identifier:
            return None, df
        person = None
        if str(emp_identifier).strip().isdigit() and 'EmpID' in df.columns:
            m = df[df['EmpID'].astype(str) == str(emp_identifier).strip()]
            if len(m): person = m.iloc[0]
        if person is None and 'Name' in df.columns:
            m = df[df['Name'].str.contains(str(emp_identifier), case=False, na=False)]
            if len(m): person = m.iloc[0]
        if person is None:
            return None, df
        role = person.get(by, None)
        peers = df[df[by] == role].copy() if by in df.columns else df
        return person, peers