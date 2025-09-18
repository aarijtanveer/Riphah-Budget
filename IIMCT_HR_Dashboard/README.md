
# IIMCT HR Budget & Org Dashboard (Streamlit)

A clean, iPadOS‑style, multi‑page analytics web app to explore IIMCT Group's HR Position‑wise Budget. 

**Highlights**
- Global filters (Org, Region, SU, Department, Salary Category, Status, Designation, ranges)
- KPIs and hierarchy views (sunburst, treemap) across Org → Region → SU → Department
- Compensation analytics (distributions, boxplots, top earners, salary bands, vacancy budget)
- Role explorer and *Employee Comparator* (where a specific employee stands vs peers)
- Vacancy & Increment impact simulator (fill‑rate, effective months)
- Text‑based *Generative Insights* (explain key patterns, outliers and recommendations)
- CSV export of any filtered view

> ⚠️ **Data file**: Place your file `IIMCT Group HR Position wise Budget.csv` inside `./data/` **or** use the *Upload new data* control inside the app. The loader will automatically handle the meta row and messy currency fields.

## Quick start
```bash
# 1) Create & activate a virtual environment (optional)
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\\Scripts\\activate

# 2) Install deps
pip install -r requirements.txt

# 3) Run
streamlit run app.py
```

## Project structure
```
IIMCT_HR_Dashboard/
├─ app.py                        # Entry point (global filters & router)
├─ utils.py                      # Data loading, cleaning, helpers, insights text
├─ pages/
│  ├─ 01_Overview.py             # KPIs + hierarchy + budget composition
│  ├─ 02_Compensation.py         # Pay analytics (distros, boxplots, top earners)
│  ├─ 03_Roles_Explorer.py       # Role/designation analytics
│  ├─ 04_Employee_Comparator.py  # Percentile & peer benchmarking
│  ├─ 05_Vacancies_Increment.py  # Vacancies & increment impact simulator
│  └─ 06_Generative_Insights.py  # Text-based narrative report
├─ assets/
│  └─ styles.css                 # iPadOS-like theme overrides
├─ .streamlit/
│  └─ config.toml                # App theme (colors, fonts)
├─ data/
│  └─ (place your CSV here)
└─ requirements.txt
```

## Notes
- The app expects the following key columns (case-insensitive, extra spaces tolerated):
  - `Org, Region, SU's Budget Sheet, Status, Emp. ID, Name, Actual Designation, Budgeted Designation, Department, SAP SU, Personal SubArea, Salary Category, Number of Positions, Gross Pay, Total Financial Impact per month, Total Financial Impact annual, Increment, Annual Increase Salary With New Positions, Impact Months (Number of Months)`
- Numeric fields may contain commas, spaces, hyphens; the loader coerces them to numbers.
- For *Senior Manager* analytics, the app matches multiple variants: `Senior Manager`, `Sr. Manager`, `Sr Manager`, `Snr Manager`.

## Security/Privacy
Data stays local on your machine—no external API calls. All analytics are computed in‑app.

