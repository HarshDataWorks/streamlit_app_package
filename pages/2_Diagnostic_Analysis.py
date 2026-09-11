import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import load_data, kpi_card, styled_fig, page_header, NAVY, GOLD, ICE, GREY, RED, GREEN

st.set_page_config(page_title="Diagnostic Analysis", page_icon="🔍", layout="wide")
data = load_data()

page_header(
    "Diagnostic Analysis",
    "Complete diagnostic analysis from 03_Diagnostic_Analysis.ipynb.",
)

tabs = st.tabs([
    "Business Performance Drivers", "Conversion / Funnel Diagnosis", "Landing Page Diagnosis",
    "Website Funnel", "Billing Page Test", "Product Launch Analysis", "Customer Retention",
])

# ============================= TAB 1: BUSINESS PERFORMANCE DRIVERS =============================
with tabs[0]:
    st.caption("Comparing the same calendar month three years apart removes seasonality and isolates real, structural improvement.")
    growth_rows = [
        ("Sessions", "1,879", "15,083", "8.0x"),
        ("Orders", "60", "1,254", "20.9x"),
        ("Conversion Rate", "3.19%", "8.31%", "2.6x"),
        ("Average Order Value", "$49.99", "$62.96", "1.3x"),
        ("Revenue", "$2,999", "$78,951", "26.3x"),
    ]
    gcols = st.columns(5)
    for i, (metric, before, after, mult) in enumerate(growth_rows):
        with gcols[i]:
            st.markdown(f"**{metric}**")
            st.write(f"{before} → {after}")
            st.markdown(f":orange[**{mult}**]")
    st.success("Revenue = Sessions × Conversion Rate × AOV. The 26x growth (March 2012 vs. March 2015) isn't a traffic story alone — all three levers moved together.")

# ============================= TAB 2: CONVERSION / FUNNEL DIAGNOSIS =============================
with tabs[1]:
    st.markdown("#### Conversion By Device Over Time")
    device_monthly = data["device_monthly"]
    fig = go.Figure()
    for dv in device_monthly["device_type"].unique():
        d = device_monthly[device_monthly["device_type"] == dv]
        color = NAVY if dv == "desktop" else GOLD
        fig.add_trace(go.Scatter(x=d["ym"], y=d["conversion_rate_pct"], mode="lines+markers", name=dv, line=dict(color=color, width=2.5)))
    fig.update_layout(title="Conversion Rate by Device Type Over Time", xaxis_title="Month", yaxis_title="Conversion Rate (%)")
    st.plotly_chart(styled_fig(fig, height=420), use_container_width=True)

    st.markdown("**March & December Year-over-Year Gap**")
    gap_rows = [
        (2012, "March", 4.37, 1.36, 3.00), (2012, "December", 6.10, 1.65, 4.45),
        (2013, "March", 7.42, 2.35, 5.08), (2013, "December", 8.18, 3.65, 4.53),
        (2014, "March", 9.15, 2.86, 6.29), (2014, "December", 9.58, 3.50, 6.08),
        (2015, "March", 10.55, 3.23, 7.32),
    ]
    gap_df = pd.DataFrame(gap_rows, columns=["Year", "Month", "Desktop %", "Mobile %", "Gap (pts)"])
    st.dataframe(gap_df, use_container_width=True, hide_index=True)
    st.error(
        "**The desktop-mobile gap is widening, not closing** — 3.00 points in March 2012 to 7.32 points in March 2015. "
        "Mobile isn't catching up as the business matures; it's falling further behind."
    )

# ============================= TAB 3: LANDING PAGE DIAGNOSIS =============================
with tabs[2]:
    st.caption("Could landing-page performance explain differences in conversion?")
    landing = data["landing"]
    c1, c2 = st.columns([1.3, 1])
    with c1:
        land_sorted = landing.sort_values("cvr_pct")
        colors = [RED if v == land_sorted["cvr_pct"].min() else (GOLD if v == land_sorted["cvr_pct"].max() else NAVY) for v in land_sorted["cvr_pct"]]
        fig2 = go.Figure(go.Bar(x=land_sorted["cvr_pct"], y=land_sorted["pageview_url"], orientation="h", marker_color=colors))
        fig2.update_layout(title="Conversion Rate by Landing Page")
        st.plotly_chart(styled_fig(fig2, height=360), use_container_width=True)
    with c2:
        home_cvr = landing.loc[landing["pageview_url"] == "/home", "cvr_pct"].values[0]
        l1_cvr = landing.loc[landing["pageview_url"] == "/lander-1", "cvr_pct"].values[0]
        lift = (home_cvr - l1_cvr) / l1_cvr * 100
        st.metric("/home CVR", f"{home_cvr:.2f}%")
        st.metric("/lander-1 CVR", f"{l1_cvr:.2f}%")
        st.metric("Relative Advantage for /home", f"+{lift:.1f}%")
    st.info(
        "The 'obvious' choice — a dedicated landing page — was wrong here: /home outperforms the purpose-built "
        "/lander-1 by over 55% (relative). **Caveat:** the full ranking is partly confounded by device mix — "
        "some landers received almost entirely mobile traffic."
    )

# ============================= TAB 4: WEBSITE FUNNEL =============================
with tabs[3]:
    st.caption("Finding where users drop in the conversion funnel.")
    funnel = data["funnel"]
    colors = [RED if s == "Cart" else NAVY for s in funnel["stage"]]
    fig3 = go.Figure(go.Bar(x=funnel["stage"], y=funnel["sessions"], marker_color=colors,
                             text=funnel["sessions"].map(lambda x: f"{x:,}"), textposition="outside"))
    fig3.update_layout(title="Website Conversion Funnel")
    st.plotly_chart(styled_fig(fig3, height=420), use_container_width=True)
    st.error("The **Cart** step loses 54.8% of sessions — more than any other step. This is the single highest-leverage point to fix in the entire funnel.")

# ============================= TAB 5: BILLING PAGE TEST =============================
with tabs[4]:
    bc1, bc2, bc3, bc4 = st.columns(4)
    kpi_card(bc1, "/billing CVR", "44.8%")
    kpi_card(bc2, "/billing-2 CVR", "63.4%")
    kpi_card(bc3, "Revenue/Session (old)", "$22.39")
    kpi_card(bc4, "Revenue/Session (new)", "$38.35")

    fig4 = go.Figure()
    fig4.add_trace(go.Bar(x=["/billing", "/billing-2"], y=[44.8, 63.4], marker_color=[GREY, GOLD],
                           text=["44.8%", "63.4%"], textposition="outside", name="Billing-to-Order CVR"))
    fig4.update_layout(title="Billing-to-Order Conversion Rate")
    st.plotly_chart(styled_fig(fig4, height=380), use_container_width=True)
    st.success("A completed, already-realized win: **+41.5% conversion lift** and **+71.3% revenue-per-session lift** from the /billing-2 redesign.")

# ============================= TAB 6: PRODUCT LAUNCH ANALYSIS =============================
with tabs[5]:
    st.caption("Did launching new products actually contribute to business growth?")
    launch_rows = [
        ("Forever Love Bear", -17, -14),
        ("Birthday Sugar Panda", -13, -8),
        ("Hudson River Mini Bear", 13, 25),
    ]
    launch_df = pd.DataFrame(launch_rows, columns=["Product", "Orders Δ%", "Revenue Δ%"])
    fig5 = go.Figure()
    fig5.add_trace(go.Bar(x=launch_df["Product"], y=launch_df["Orders Δ%"], name="Orders Δ%", marker_color=NAVY))
    fig5.add_trace(go.Bar(x=launch_df["Product"], y=launch_df["Revenue Δ%"], name="Revenue Δ%", marker_color=GOLD))
    fig5.update_layout(title="Business Impact 30 Days Before vs. After Each Product Launch", barmode="group")
    fig5.add_hline(y=0, line_color="gray")
    st.plotly_chart(styled_fig(fig5, height=420), use_container_width=True)
    st.warning(
        "**Honest finding:** 2 of the 3 later launches (Forever Love Bear, Birthday Sugar Panda) show a short-term "
        "*dip* in total orders/revenue in the 30 days around launch — likely cannibalizing existing sales rather "
        "than adding new demand. Only the Hudson River Mini Bear shows clear incremental growth."
    )

# ============================= TAB 7: CUSTOMER RETENTION =============================
with tabs[6]:
    nr = data["new_vs_repeat"]
    total_customers = nr["customers"].sum()
    repeat_pct = nr.loc[nr["customer_type"] == "Repeat", "customers"].values[0] / total_customers * 100
    ltv_multiple = nr.loc[nr["customer_type"] == "Repeat", "revenue_per_customer"].values[0] / nr.loc[nr["customer_type"] == "New", "revenue_per_customer"].values[0]

    c1, c2, c3 = st.columns(3)
    kpi_card(c1, "Repeat Customer Rate", f"{repeat_pct:.2f}%")
    kpi_card(c2, "Repeat Customers", f"{nr.loc[nr['customer_type']=='Repeat','customers'].values[0]:,.0f}")
    kpi_card(c3, "Repeat Customer LTV Multiple", f"{ltv_multiple:.1f}x")

    st.info(
        "Repeat purchase rate is low in absolute terms, but the customers who do return are worth "
        f"**{ltv_multiple:.1f}x** more per customer. This is a stuffed-animal gift retailer — a low repeat rate may "
        "be structurally expected (birthdays, one-off gifts) rather than a retention failure, but the value gap "
        "still makes even a small increase in repeat rate a high-leverage lever."
    )
