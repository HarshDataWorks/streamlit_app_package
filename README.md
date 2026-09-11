# 🧸 Digital Analytics for E-Commerce Company

An end-to-end analytics project for a fictional e-commerce startup selling stuffed
animal toys — built to give the CEO a data-driven growth story for investors, and
regular dashboards for her marketing and website teams.

**🔗 Live App:** _add your Streamlit link here after deployment_

---

## 📊 What's Inside

This app mirrors the project's three Jupyter notebooks, one per page:

- **Descriptive EDA** — 11-step analysis of revenue, orders, margin, product
  performance, traffic, and customer behavior
- **Diagnostic Analysis** — 7 diagnostics explaining *why* the numbers moved:
  growth decomposition, A/B test results, funnel drop-off, product launch impact,
  and customer retention
- **Predictive Analytics** — an interactive, live-trained logistic regression
  model predicting session-to-order conversion, with full model evaluation
  (ROC curve, calibration, coefficients)

## 🏗️ Project Pipeline

Raw Data → SQL Server (audit + cleaning) → SQL EDA → Python EDA →
Diagnostic Analysis → Predictive Model → Power BI Dashboards → This App


## 🛠️ Tech Stack

- **SQL Server** — data auditing, cleaning, and business-question EDA
- **Python** (pandas, scikit-learn, plotly) — EDA, diagnostics, predictive modeling
- **Power BI** — three stakeholder dashboards
- **Streamlit** — this interactive app

## 🚀 Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📁 Project Structure

streamlit_app/
├── app.py # Home page
├── utils.py # Shared helpers
├── pages/ # One file per notebook
├── data_processed/ # Pre-aggregated data (no live DB needed)
└── data_prep/ # Script to regenerate data_processed/


## 📌 A Note on Data Integrity

Every number in this app was independently verified against the source data
before being included. Findings are reported honestly, including less
flattering ones — for example, 2 of 3 later product launches show a short-term
sales *dip* rather than growth, and the predictive model's AUC (0.608) is
modest and reported as such rather than overstated.

---

*Built as part of the PRP Project | Analytics Team*