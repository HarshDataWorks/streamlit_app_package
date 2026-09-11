import streamlit as st
from utils import load_data, kpi_card, NAVY, GOLD, GREY

st.set_page_config(
    page_title="E-Commerce Analytics | Digital Analytics for E-Commerce Company",
    page_icon="🧸",
    layout="wide",
)

data = load_data()
monthly = data["monthly"]
product = data["product"]

st.markdown(f"<h1 style='color:{NAVY};'>🧸 Digital Analytics for E-Commerce Company</h1>", unsafe_allow_html=True)
st.markdown(
    f"<p style='color:{GREY}; font-size:1.1rem;'>An end-to-end analytics project — SQL, Python, diagnostic analysis, "
    f"a predictive model, and Power BI — for a stuffed-animal-toy e-commerce startup raising its next funding round.</p>",
    unsafe_allow_html=True,
)
st.divider()

total_revenue = monthly["revenue"].sum()
total_orders = monthly["orders"].sum()
total_sessions = monthly["sessions"].sum()
total_margin_dollars = (monthly["margin_pct"] / 100 * monthly["revenue"]).sum()
gross_margin_pct = total_margin_dollars / total_revenue * 100
overall_cvr = total_orders / total_sessions * 100

c1, c2, c3, c4 = st.columns(4)
kpi_card(c1, "Total Revenue", f"${total_revenue/1e6:.2f}M")
kpi_card(c2, "Total Orders", f"{total_orders:,.0f}")
kpi_card(c3, "Gross Margin", f"{gross_margin_pct:.1f}%")
kpi_card(c4, "Conversion Rate", f"{overall_cvr:.2f}%")

st.divider()

st.markdown("### The Bottom Line")
st.info(
    "Over three years, revenue grew roughly **26x** (comparing March 2012 to March 2015), built on more traffic "
    "**and** meaningfully better conversion efficiency — not growth alone. The underlying economics are healthy: "
    "a **62.74% gross margin** and a **4.32% refund rate** are both strong signals for this business.\n\n"
    "The opportunity ahead is **efficiency, not acquisition** — mobile converts at roughly a third of desktop's rate, "
    "the single largest funnel drop-off happens at the Cart step, and one product carries 62% of all revenue."
)

st.divider()
st.markdown("### Navigate This App")
nc1, nc2, nc3 = st.columns(3)
with nc1:
    st.markdown("#### 📊 Descriptive & Diagnostic EDA")
    st.write("Revenue trends, product performance, traffic & device breakdowns, the website funnel, and the *why* behind the growth story.")
with nc2:
    st.markdown("#### 🎯 Predictive Model")
    st.write("An interactive conversion-propensity predictor — enter a session profile and see the model's live prediction.")
with nc3:
    st.markdown("#### ℹ️ About This Project")
    st.write("Data sources, methodology, tech stack, and links to the full SQL, Python, and Power BI deliverables.")

st.caption("Use the sidebar to navigate between pages →")
