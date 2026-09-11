import streamlit as st
from utils import page_header, NAVY, GOLD

st.set_page_config(page_title="About This Project", page_icon="ℹ️", layout="wide")

page_header("About This Project", "Data sources, methodology, and the full technical pipeline behind this app.")

st.markdown("""
### Business Context
This is an end-to-end analytics project for a fictional e-commerce retail startup selling stuffed animal toys.
The CEO is raising a new venture capital round and needs a data-driven growth story for investors, plus
regular dashboards for her marketing and website teams.

### Data
Six related tables covering website sessions, pageviews, orders, order line items, refunds, and the product
catalog — roughly 1.77 million rows spanning March 2012 to March 2015.

### This App's Structure
This app is organized to match the three project notebooks exactly, one per sidebar page:
- **Descriptive EDA** → mirrors `02_Descriptive_EDA.ipynb` (11 steps)
- **Diagnostic Analysis** → mirrors `03_Diagnostic_Analysis.ipynb` (7 diagnostics)
- **Predictive Analytics** → mirrors `04_Predictive_Analytics.ipynb`

### Analytical Pipeline
""")

pipeline = [
    "Raw data audited in SQL Server (duplicates, referential integrity, chronology, financial consistency)",
    "Data cleaning — staging tables preserve raw data; analytical views standardize types and categorize traffic",
    "SQL EDA — answering the CEO's specific quarterly/channel/funnel business questions",
    "Python EDA — the same analysis reproduced in pandas (Descriptive EDA page)",
    "Diagnostic analysis — decomposing growth drivers, A/B test results, launch impact, retention (Diagnostic Analysis page)",
    "Predictive modeling — a conversion-propensity logistic regression model (Predictive Analytics page)",
    "Power BI — three live dashboards, one per stakeholder",
    "This Streamlit app — an interactive, deployable summary of the above",
]
for i, step in enumerate(pipeline, 1):
    st.markdown(f"**{i}.** {step}")

st.divider()
st.markdown("""
### Tech Stack
- **SQL Server** — data auditing, cleaning, and business-question EDA
- **Python (pandas, scikit-learn, plotly)** — EDA, diagnostics, and the predictive model
- **Power BI** — stakeholder dashboards
- **Streamlit** — this interactive app

### A Note on Honesty
This project deliberately reports real, sometimes unflattering findings rather than only the positive ones —
for example, 2 of 3 later product launches show a short-term *dip* in sales rather than growth, and the
predictive model's AUC (0.608) is modest and reported as such. The goal was an accurate story, not the most
flattering one.
""")

st.caption("Built as part of the PRP Project | Analytics Team")
