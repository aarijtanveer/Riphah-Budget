
import re
import pandas as pd
import numpy as np
from typing import List, Tuple, Optional

DISPLAY_COLS = [
    'Org','Region','SU\'s Budget Sheet','Status','Emp. ID','Name','Actual Designation',
    'Budgeted Designation','Department','SAP SU','Personal SubArea','Salary Category',
    'Number of Positions','Gross Pay','Total Financial Impact per month','Total Financial Impact annual',
    'Increment','Annual Increase Salary With New Positions','Impact Months (Number of Months)'
]

ROLE_ALIASES = ["senior manager","sr. manager","sr manager","snr manager"]

NUMERIC_COLS = [
    'Number of Positions','Gross Pay','Total Financial Impact per month','Total Financial Impact annual',
    'Increment','Annual Increase Salary With New Positions','Impact Months (Number of Months)'
]

RENAMES = {
    'SU\'s Budget Sheet': 'SU',
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

@pd.api.extensions.register_dataframe_accessor("hr")
class HRAccessor:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def is_senior_manager(self) -> pd.Series:
        desig = self._obj['BudDesignation'].fillna('').str.lower()
        mask = False
        for a in ROLE_ALIASES + ['senior manager']:
            mask = mask | desig.str.contains(a)
        return mask

    def kpis(self):
        df = self._obj
        existing = df[df['Status'].str.lower().eq('existing')]
        total_positions = df['Positions'].fillna(0).sum()
        headcount = existing['Positions'].fillna(0).sum()
        annual_budget = df['ImpactAnnual'].fillna(0).sum()
        monthly_budget = df['ImpactMonthly'].fillna(0).sum()
        vacancy_budget = df[df['Status'].str.lower().eq('vacant')]['ImpactAnnual'].fillna(0).sum()
        increment_total = df['Increment'].fillna(0).sum()
        return {
            'total_positions': int(total_positions),
            'headcount': int(headcount),
            'annual_budget': float(annual_budget),
            'monthly_budget': float(monthly_budget),
            'vacancy_budget': float(vacancy_budget),
            'increment_total': float(increment_total)
        }

    def peers(self, emp_identifier: str, by: str = 'BudDesignation') -> Tuple[Optional[pd.Series], pd.DataFrame]:
        df = self._obj.copy()
        if emp_identifier is None or str(emp_identifier).strip()=='' :
            return None, df
        # match by EmpID (exact) or Name (case-insensitive contains)
        person = None
        if str(emp_identifier).strip().isdigit():
            m = df[df['EmpID'].astype(str) == str(emp_identifier).strip()]
            if len(m):
                person = m.iloc[0]
        if person is None:
            m = df[df['Name'].str.contains(str(emp_identifier), case=False, na=False)]
            if len(m):
                person = m.iloc[0]
        if person is None:
            return None, df
        role = person.get(by, None)
        peers = df[df[by] == role].copy()
        return person, peers


def _clean_number(x):
    if pd.isna(x):
        return np.nan
    if isinstance(x, (int,float)):
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


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # strip spaces and unify column names
    df.columns = [c.strip() for c in df.columns]
    # ensure all expected columns exist
    return df


def load_data(path_or_buffer) -> pd.DataFrame:
    # Try reading; handle meta first row like "Data, ... Increment Rate ,6%"
    try:
        df = pd.read_csv(path_or_buffer, header=0, dtype=str, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(path_or_buffer, header=0, dtype=str, encoding='latin-1')

    # If first column looks like 'Data', drop that row
    if df.columns[0].lower().startswith('data') or (df.iloc[0,0] and str(df.iloc[0,0]).lower().startswith('iimct')):
        # Heuristic: find header row by locating the first row where col0 == 'Org'
        idx_header = None
        for i in range(min(5, len(df))):
            if str(df.iloc[i,0]).strip().lower() == 'iimct' or str(df.iloc[i,0]).strip().lower() == 'org':
                idx_header = i
                break
        if idx_header is not None and idx_header != 0:
            new_header = df.iloc[idx_header]
            df = df.iloc[idx_header+1:].copy()
            df.columns = new_header

    df = _standardize_columns(df)

    # keep only relevant columns if present
    keep = [c for c in DISPLAY_COLS if c in df.columns]
    df = df[keep].copy()

    # clean numeric cols
    for c in NUMERIC_COLS:
        if c in df.columns:
            df[c] = df[c].apply(_clean_number)

    # rename
    df = df.rename(columns=RENAMES)

    # normalize
    for c in ['Status','Org','Region','Department','SAP SU','SubArea','SalaryCategory','ActDesignation','BudDesignation']:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()

    # compute helpers
    if 'Positions' in df.columns:
        df['Positions'] = df['Positions'].fillna(1)

    # coerce EmpID to string
    if 'EmpID' in df.columns:
        df['EmpID'] = df['EmpID'].astype(str).str.replace('.0','', regex=False)

    # add flags
    df['IsVacant'] = df['Status'].str.lower().eq('vacant')
    df['IsExisting'] = df['Status'].str.lower().eq('existing')

    # Senior manager role flag
    df['IsSeniorManager'] = df.hr.is_senior_manager()

    return df


def salary_percentile(series: pd.Series, value: float) -> Optional[float]:
    if value is None or np.isnan(value):
        return None
    s = series.dropna().astype(float)
    if len(s)==0:
        return None
    return float((s < value).sum() / len(s) * 100)


def currency(x: float) -> str:
    if pd.isna(x):
        return '—'
    return f"₨ {x:,.0f}"


def generative_summary(df: pd.DataFrame, scope_label: str = "All Filters") -> str:
    k = df.hr.kpis()
    # Top by spend
    by_dept = df.groupby('Department', dropna=False)['ImpactAnnual'].sum().sort_values(ascending=False).head(5)
    by_su = df.groupby('SU', dropna=False)['ImpactAnnual'].sum().sort_values(ascending=False).head(5)
    # Outliers (top/bottom earners among existing)
    existing = df[df['IsExisting'] & df['GrossPay'].notna()]
    top5 = existing[['Name','BudDesignation','Department','GrossPay']].sort_values('GrossPay', ascending=False).head(5)
    bottom5 = existing[['Name','BudDesignation','Department','GrossPay']].sort_values('GrossPay', ascending=True).head(5)
    vac_rate = (df['IsVacant'].mean() * 100) if len(df) else 0

    # Compose narrative
    lines = []
    lines.append(f"**{scope_label} — Narrative Insights**")
    lines.append(
        f"• Annual budget: {currency(k['annual_budget'])} (monthly: {currency(k['monthly_budget'])}). "
        f"Vacancy budget parked: {currency(k['vacancy_budget'])}. Total positions: {k['total_positions']} (active headcount: {k['headcount']})."
    )
    if len(by_dept):
        tops = ", ".join([f"{d} ({currency(v)})" for d,v in by_dept.items()])
        lines.append(f"• Top departments by annual spend: {tops}.")
    if len(by_su):
        topsu = ", ".join([f"{d} ({currency(v)})" for d,v in by_su.items()])
        lines.append(f"• Top SUs by annual spend: {topsu}.")
    lines.append(f"• Vacancy ratio: {vac_rate:.1f}% of rows flagged as Vacant. Total increment pool: {currency(k['increment_total'])}.")
    if len(top5):
        t = ", ".join([f"{r.Name} — {r.BudDesignation} ({r.Department}): {currency(r.GrossPay)}" for _,r in top5.iterrows()])
        lines.append(f"• Highest gross pays (existing): {t}.")
    if len(bottom5):
        b = ", ".join([f"{r.Name} — {r.BudDesignation} ({r.Department}): {currency(r.GrossPay)}" for _,r in bottom5.iterrows()])
        lines.append(f"• Lowest gross pays (existing): {b}.")
    lines.append("• Recommendation: review bands where dispersion is high (see boxplots), and redirect a portion of vacancy budget to critical roles before Q2.")

    return "\n".join(lines)
