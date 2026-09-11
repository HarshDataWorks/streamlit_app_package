"""
build_processed_data.py

Converts the 6 raw source tables into the small, pre-aggregated CSVs the
Streamlit app actually reads from (data_processed/). Run this once whenever
the underlying data changes.

WHY THIS EXISTS: the raw tables total ~100MB (mostly website_sessions and
website_pageviews). Shipping that to a deployed app means slow cold starts
and a bloated repo. Pre-aggregating down to ~9MB of exactly what each page
needs keeps the deployed app fast and the GitHub repo lean.

Usage:
    1. Export your 6 tables from SQL Server as CSVs into raw_data_reference_only/
       (website_sessions, website_pageviews, orders, order_items,
        order_item_refunds, products)
    2. Run: python build_processed_data.py
    3. The refreshed CSVs land in ../data_processed/ automatically.
"""
import pandas as pd
import os

RAW = "raw_data_reference_only/"
OUT = "../data_processed/"
os.makedirs(OUT, exist_ok=True)

sessions = pd.read_csv(RAW + "website_sessions.csv", parse_dates=["created_at"])
pageviews = pd.read_csv(RAW + "website_pageviews.csv", parse_dates=["created_at"])
orders = pd.read_csv(RAW + "orders.csv", parse_dates=["created_at"])
order_items = pd.read_csv(RAW + "order_items.csv", parse_dates=["created_at"])
refunds = pd.read_csv(RAW + "order_item_refunds.csv", parse_dates=["created_at"])
products = pd.read_csv(RAW + "products.csv", parse_dates=["created_at"])

sessions["ym"] = sessions["created_at"].dt.to_period("M").astype(str)
orders["ym"] = orders["created_at"].dt.to_period("M").astype(str)

# 1. Monthly KPIs (revenue, orders, margin, conversion trend)
m_sess = sessions.groupby("ym").size().rename("sessions")
m_ord = orders.groupby("ym").agg(
    orders=("order_id", "count"), revenue=("price_usd", "sum"), cogs=("cogs_usd", "sum")
).reset_index().set_index("ym")
monthly = pd.concat([m_sess, m_ord], axis=1).fillna(0).reset_index()
monthly["conversion_rate_pct"] = (monthly["orders"] / monthly["sessions"] * 100).round(2)
monthly["margin_pct"] = ((monthly["revenue"] - monthly["cogs"]) / monthly["revenue"] * 100).round(2)
monthly["aov"] = (monthly["revenue"] / monthly["orders"]).round(2)
monthly.to_csv(OUT + "monthly_kpis.csv", index=False)

# 2. Product summary (revenue, margin, refund rate per product)
oi_prod = order_items.merge(products[["product_id", "product_name"]], on="product_id")
ref_ids = set(refunds["order_item_id"])
oi_prod["refunded"] = oi_prod["order_item_id"].isin(ref_ids)
prod_summary = oi_prod.groupby("product_name").agg(
    units_sold=("order_item_id", "count"), revenue=("price_usd", "sum"),
    cogs=("cogs_usd", "sum"), items_refunded=("refunded", "sum"),
).reset_index()
prod_summary["gross_margin"] = prod_summary["revenue"] - prod_summary["cogs"]
prod_summary["margin_pct"] = (prod_summary["gross_margin"] / prod_summary["revenue"] * 100).round(2)
prod_summary["refund_rate_pct"] = (prod_summary["items_refunded"] / prod_summary["units_sold"] * 100).round(2)
prod_summary.to_csv(OUT + "product_summary.csv", index=False)

# 3. Channel & device summary
so = sessions.merge(orders[["website_session_id", "order_id"]], on="website_session_id", how="left")
so["converted"] = so["order_id"].notna().astype(int)
so["src"] = so["utm_source"].fillna("Unattributed")
channel_summary = so.groupby("src").agg(sessions=("website_session_id", "count"), orders=("converted", "sum")).reset_index()
channel_summary["cvr_pct"] = (channel_summary["orders"] / channel_summary["sessions"] * 100).round(2)
channel_summary.to_csv(OUT + "channel_summary.csv", index=False)

device_summary = so.groupby("device_type").agg(sessions=("website_session_id", "count"), orders=("converted", "sum")).reset_index()
device_summary["cvr_pct"] = (device_summary["orders"] / device_summary["sessions"] * 100).round(2)
device_summary.to_csv(OUT + "device_summary.csv", index=False)

# 4. Landing page summary
pv_sorted = pageviews.sort_values(["website_session_id", "created_at"])
first_pv = pv_sorted.groupby("website_session_id").first().reset_index()[["website_session_id", "pageview_url"]]
sl = sessions.merge(first_pv, on="website_session_id", how="left").merge(
    orders[["website_session_id", "order_id"]], on="website_session_id", how="left"
)
sl["converted"] = sl["order_id"].notna().astype(int)
landers = sl[sl["pageview_url"].isin(["/home", "/lander-1", "/lander-2", "/lander-3", "/lander-4", "/lander-5"])]
lp_summary = landers.groupby("pageview_url").agg(sessions=("website_session_id", "count"), orders=("converted", "sum")).reset_index()
lp_summary["cvr_pct"] = (lp_summary["orders"] / lp_summary["sessions"] * 100).round(2)
lp_summary.to_csv(OUT + "landing_page_summary.csv", index=False)

# 5. Funnel summary
product_pages = ["/the-original-mr-fuzzy", "/the-forever-love-bear", "/the-birthday-sugar-panda", "/the-hudson-river-mini-bear"]
def stage(url):
    if url == "/products": return "Products"
    if url in product_pages: return "Product Page"
    if url == "/cart": return "Cart"
    if url == "/shipping": return "Shipping"
    if url in ["/billing", "/billing-2"]: return "Billing"
    if url == "/thank-you-for-your-order": return "Order"
    return None
pf = pageviews.copy()
pf["stage"] = pf["pageview_url"].apply(stage)
pf = pf.dropna(subset=["stage"])
first_stage = pf.sort_values(["website_session_id", "created_at"]).drop_duplicates(["website_session_id", "stage"])
stage_order = ["Products", "Product Page", "Cart", "Shipping", "Billing", "Order"]
counts = first_stage.groupby("stage")["website_session_id"].nunique().reindex(stage_order)
pd.DataFrame({"stage": stage_order, "sessions": counts.values}).to_csv(OUT + "funnel_summary.csv", index=False)

# 6. Session-level features for the LIVE predictive model (kept at full
#    session grain, but only the 4 columns the model needs - this is why
#    it's ~9MB instead of the full sessions table's ~40MB+)
model_data = so[["website_session_id", "converted", "src", "device_type"]].copy()
model_data = model_data.merge(sessions[["website_session_id", "is_repeat_session"]], on="website_session_id")
model_data = model_data.drop(columns=["website_session_id"]).rename(columns={"src": "traffic_source"})
model_data.to_csv(OUT + "session_model_features.csv", index=False)

print("Done. Processed files written to", OUT)
for f in sorted(os.listdir(OUT)):
    print(f"  {f}: {os.path.getsize(OUT + f) / 1024:.1f} KB")
