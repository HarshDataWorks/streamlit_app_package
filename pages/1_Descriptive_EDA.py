import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from utils import load_data, kpi_card, styled_fig, page_header, NAVY, GOLD, ICE, GREY, RED, GREEN

st.set_page_config(page_title="Descriptive EDA", page_icon="📊", layout="wide")
data = load_data()

page_header(
    "Descriptive EDA",
    "Complete descriptive analysis from 02_Descriptive_EDA.ipynb.",
)

monthly = data["monthly"]
product = data["product"]
channel = data["channel"]
device = data["device"]
nr = data["new_vs_repeat"]

tabs = st.tabs([
    "Revenue / Orders / AOV", "Gross Margin", "Product Performance", "Refund Analysis",
    "Traffic", "Device", "Product Profitability", "Refund Behavior",
    "Traffic → Conversion", "Device → Conversion", "New vs Repeat",
])

# ============================= TAB 1: REVENUE / ORDERS / AOV =============================
with tabs[0]:
    st.markdown("#### 1.1 Revenue Trend")
    fig = px.bar(monthly, x="ym", y="revenue", title="Monthly Revenue")
    fig.update_traces(marker_color=NAVY)
    st.plotly_chart(styled_fig(fig, height=380), use_container_width=True)

    st.markdown("#### 1.2 Order Trend")
    fig2 = px.line(monthly, x="ym", y="orders", title="Monthly Orders", markers=True)
    fig2.update_traces(line_color=GOLD)
    st.plotly_chart(styled_fig(fig2, height=380), use_container_width=True)

    st.markdown("#### 1.3 Average Order Value Trend")
    fig3 = px.line(monthly, x="ym", y="aov", title="Monthly Average Order Value", markers=True)
    fig3.update_traces(line_color=NAVY)
    st.plotly_chart(styled_fig(fig3, height=380), use_container_width=True)

# ============================= TAB 2: GROSS MARGIN =============================
with tabs[1]:
    st.markdown("#### 2.1 Gross Margin % Trend")
    fig4 = px.line(monthly, x="ym", y="margin_pct", title="Monthly Gross Margin %", markers=True)
    fig4.update_traces(line_color=GREEN)
    fig4.add_hline(y=monthly["margin_pct"].mean(), line_dash="dash", line_color=GOLD,
                    annotation_text=f"Avg: {monthly['margin_pct'].mean():.1f}%")
    st.plotly_chart(styled_fig(fig4, height=400), use_container_width=True)

    st.markdown("#### 2.2 Order-Value Distribution")
    stats = data["order_value_stats"]
    stat_dict = dict(zip(stats.iloc[:, 0], stats.iloc[:, 1]))
    c1, c2 = st.columns([2, 1])
    with c1:
        fig_hist = px.histogram(data["order_value_raw"], x="price_usd", nbins=50, title="Distribution of Order Values")
        fig_hist.update_traces(marker_color=NAVY)
        st.plotly_chart(styled_fig(fig_hist, height=380), use_container_width=True)
    with c2:
        st.markdown("**Summary Statistics**")
        for label in ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]:
            if label in stat_dict:
                val = stat_dict[label]
                display = f"{val:,.0f}" if label == "count" else f"${val:,.2f}"
                st.write(f"**{label}:** {display}")

# ============================= TAB 3: PRODUCT PERFORMANCE =============================
with tabs[2]:
    st.markdown("#### 3.1 Top Product by Revenue")
    prod_sorted = product.sort_values("revenue")
    colors = [GOLD if v == prod_sorted["revenue"].max() else NAVY for v in prod_sorted["revenue"]]
    fig5 = go.Figure(go.Bar(x=prod_sorted["revenue"], y=prod_sorted["product_name"], orientation="h", marker_color=colors))
    fig5.update_layout(title="Revenue by Product")
    st.plotly_chart(styled_fig(fig5, height=380), use_container_width=True)

    st.markdown("#### 3.2 Top Products by Units")
    units_sorted = product.sort_values("units_sold")
    fig6 = go.Figure(go.Bar(x=units_sorted["units_sold"], y=units_sorted["product_name"], orientation="h", marker_color=NAVY))
    fig6.update_layout(title="Units Sold by Product")
    st.plotly_chart(styled_fig(fig6, height=380), use_container_width=True)

# ============================= TAB 4: REFUND ANALYSIS =============================
with tabs[3]:
    overall_refund_rate = product["items_refunded"].sum() / product["units_sold"].sum() * 100
    st.metric("Overall Refund Rate", f"{overall_refund_rate:.2f}%")

    st.markdown("#### 4.1 Refunds by Product")
    ref_count_sorted = product.sort_values("items_refunded")
    fig7 = go.Figure(go.Bar(x=ref_count_sorted["items_refunded"], y=ref_count_sorted["product_name"], orientation="h", marker_color=RED))
    fig7.update_layout(title="Refunded Units by Product")
    st.plotly_chart(styled_fig(fig7, height=380), use_container_width=True)

# ============================= TAB 5: TRAFFIC (SESSIONS EXPLORATION) =============================
with tabs[4]:
    fig8 = go.Figure(go.Bar(x=channel["src"], y=channel["sessions"], marker_color=NAVY,
                             text=channel["sessions"].map(lambda x: f"{x:,}"), textposition="outside"))
    fig8.update_layout(title="Sessions by Traffic Source")
    st.plotly_chart(styled_fig(fig8, height=420), use_container_width=True)

# ============================= TAB 6: DEVICE (EXPLORATION) =============================
with tabs[5]:
    fig9 = go.Figure(go.Bar(x=device["device_type"], y=device["sessions"], marker_color=[NAVY, GOLD],
                             text=device["sessions"].map(lambda x: f"{x:,}"), textposition="outside"))
    fig9.update_layout(title="Sessions by Device Type")
    st.plotly_chart(styled_fig(fig9, height=420), use_container_width=True)

# ============================= TAB 7: PRODUCT PROFITABILITY =============================
with tabs[6]:
    display_df = product[["product_name", "units_sold", "revenue", "cogs", "gross_margin", "margin_pct"]].copy()
    display_df.columns = ["Product", "Units Sold", "Revenue", "COGS", "Gross Margin", "Margin %"]
    for c in ["Revenue", "COGS", "Gross Margin"]:
        display_df[c] = display_df[c].map(lambda x: f"${x:,.0f}")
    display_df["Margin %"] = display_df["Margin %"].map(lambda x: f"{x:.2f}%")
    st.dataframe(display_df.sort_values("Margin %", ascending=False), use_container_width=True, hide_index=True)

    fig10 = go.Figure(go.Bar(
        x=product.sort_values("margin_pct")["margin_pct"],
        y=product.sort_values("margin_pct")["product_name"],
        orientation="h", marker_color=GREEN,
    ))
    fig10.update_layout(title="Gross Margin % by Product")
    st.plotly_chart(styled_fig(fig10, height=360), use_container_width=True)
    st.caption("Note: the hero product often has the *lowest* margin % — margin-weighted mix matters as much as revenue mix.")

# ============================= TAB 8: REFUND BEHAVIOR =============================
with tabs[7]:
    ref_rate_sorted = product.sort_values("refund_rate_pct")
    colors = [RED if v == ref_rate_sorted["refund_rate_pct"].max() else NAVY for v in ref_rate_sorted["refund_rate_pct"]]
    fig11 = go.Figure(go.Bar(x=ref_rate_sorted["refund_rate_pct"], y=ref_rate_sorted["product_name"], orientation="h", marker_color=colors))
    fig11.update_layout(title="Refund Rate % by Product")
    st.plotly_chart(styled_fig(fig11, height=420), use_container_width=True)

# ============================= TAB 9: TRAFFIC SOURCE → CONVERSION =============================
with tabs[8]:
    st.caption("Which sources bring quality traffic rather than merely large amounts of traffic?")
    ch_sorted = channel.sort_values("cvr_pct")
    colors = [RED if v == ch_sorted["cvr_pct"].min() else (GOLD if v == ch_sorted["cvr_pct"].max() else NAVY) for v in ch_sorted["cvr_pct"]]
    fig12 = go.Figure(go.Bar(x=ch_sorted["cvr_pct"], y=ch_sorted["src"], orientation="h", marker_color=colors))
    fig12.update_layout(title="Conversion Rate by Traffic Source")
    st.plotly_chart(styled_fig(fig12, height=380), use_container_width=True)
    st.warning("Gsearch drives the most volume (316K sessions) but converts lowest of the paid sources (6.75%) — 'Unattributed' (direct/repeat) traffic actually converts best (7.34%).")

# ============================= TAB 10: DEVICE → CONVERSION =============================
with tabs[9]:
    fig13 = go.Figure(go.Bar(x=device["device_type"], y=device["cvr_pct"], marker_color=[NAVY, GOLD],
                              text=device["cvr_pct"].map(lambda x: f"{x:.2f}%"), textposition="outside"))
    fig13.update_layout(title="Conversion Rate: Desktop vs Mobile")
    st.plotly_chart(styled_fig(fig13, height=380), use_container_width=True)
    st.warning("Desktop converts nearly 3x better than mobile (8.50% vs 3.09%) despite mobile being roughly a third of all traffic.")

# ============================= TAB 11: NEW VS REPEAT =============================
with tabs[10]:
    c1, c2 = st.columns(2)
    with c1:
        fig14 = go.Figure(go.Bar(x=nr["customer_type"], y=nr["revenue"], marker_color=[NAVY, GOLD],
                                  text=nr["revenue"].map(lambda x: f"${x:,.0f}"), textposition="outside"))
        fig14.update_layout(title="Total Revenue by Customer Type")
        st.plotly_chart(styled_fig(fig14, height=360), use_container_width=True)
    with c2:
        fig15 = go.Figure(go.Bar(x=nr["customer_type"], y=nr["revenue_per_customer"], marker_color=[NAVY, GOLD],
                                  text=nr["revenue_per_customer"].map(lambda x: f"${x:,.2f}"), textposition="outside"))
        fig15.update_layout(title="Revenue per Customer")
        st.plotly_chart(styled_fig(fig15, height=360), use_container_width=True)

    total_customers = nr["customers"].sum()
    repeat_pct = nr.loc[nr["customer_type"] == "Repeat", "customers"].values[0] / total_customers * 100
    ltv_multiple = nr.loc[nr["customer_type"] == "Repeat", "revenue_per_customer"].values[0] / nr.loc[nr["customer_type"] == "New", "revenue_per_customer"].values[0]

    c1, c2, c3 = st.columns(3)
    kpi_card(c1, "Repeat Customer Rate", f"{repeat_pct:.2f}%")
    kpi_card(c2, "Repeat Customers", f"{nr.loc[nr['customer_type']=='Repeat','customers'].values[0]:,.0f}")
    kpi_card(c3, "Repeat Customer LTV Multiple", f"{ltv_multiple:.1f}x")
