import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, roc_curve
import plotly.graph_objects as go
from utils import load_data, styled_fig, page_header, NAVY, GOLD, ICE, GREY, RED

st.set_page_config(page_title="Predictive Analytics", page_icon="🎯", layout="wide")
data = load_data()

page_header(
    "Predictive Analytics",
    "Complete predictive analysis from 04_Predictive_Analytics.ipynb.",
)


@st.cache_resource
def train_model(df: pd.DataFrame):
    """
    Trains the same model built in 04_Predictive_Analytics.ipynb, live, on
    app startup. Retraining here (instead of shipping a pickled model file)
    keeps the app self-contained and guarantees the demo always matches the
    data it's running against.
    """
    X = pd.get_dummies(df[["traffic_source", "device_type", "is_repeat_session"]],
                        columns=["traffic_source", "device_type"], drop_first=True)
    y = df["converted"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    test_probs = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, test_probs)

    return model, X.columns.tolist(), auc, X_test, y_test, test_probs


with st.spinner("Training model on session data..."):
    model, feature_cols, auc, X_test, y_test, test_probs = train_model(data["model_features"])

tab1, tab2 = st.tabs(["Try the Model", "Model Performance"])

# ============================= TAB 1: INTERACTIVE PREDICTOR =============================
with tab1:
    st.markdown("### Enter a Session Profile")
    st.caption("Adjust the inputs below to see the model's live predicted conversion probability for that type of session.")

    c1, c2, c3 = st.columns(3)
    with c1:
        traffic_source = st.selectbox("Traffic Source", sorted(data["model_features"]["traffic_source"].unique()))
    with c2:
        device_type = st.selectbox("Device Type", sorted(data["model_features"]["device_type"].unique()))
    with c3:
        is_repeat = st.selectbox("Repeat Visitor?", ["No (first-time visitor)", "Yes (returning visitor)"])
        is_repeat_val = 1 if "Yes" in is_repeat else 0

    # Build the one-hot encoding manually, matching the exact columns the
    # model was trained on. (An earlier version used pd.get_dummies() on a
    # single-row input, which only works correctly when multiple categories
    # are present in the same call — on one row it silently produces the
    # wrong columns, so every dummy variable fell back to 0 regardless of
    # the dropdown selection. This manual approach avoids that bug.)
    input_encoded = pd.DataFrame(0, index=[0], columns=feature_cols)
    if "is_repeat_session" in input_encoded.columns:
        input_encoded["is_repeat_session"] = is_repeat_val
    ts_col = f"traffic_source_{traffic_source}"
    if ts_col in input_encoded.columns:
        input_encoded[ts_col] = 1
    dt_col = f"device_type_{device_type}"
    if dt_col in input_encoded.columns:
        input_encoded[dt_col] = 1

    prob = model.predict_proba(input_encoded)[0, 1]

    st.divider()
    pc1, pc2 = st.columns([1, 2])
    with pc1:
        st.metric("Predicted Conversion Probability", f"{prob*100:.2f}%")
        baseline = data["model_features"]["converted"].mean() * 100
        delta = prob * 100 - baseline
        st.caption(f"Company average: {baseline:.2f}% ({'above' if delta > 0 else 'below'} average by {abs(delta):.2f} pts)")
    with pc2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prob * 100,
            number={"suffix": "%"},
            gauge={
                "axis": {"range": [0, max(15, baseline * 2)]},
                "bar": {"color": NAVY},
                "steps": [
                    {"range": [0, baseline], "color": "#F4F6FB"},
                    {"range": [baseline, max(15, baseline * 2)], "color": ICE},
                ],
                "threshold": {"line": {"color": GOLD, "width": 4}, "thickness": 0.8, "value": baseline},
            },
        ))
        st.plotly_chart(styled_fig(fig, height=220), use_container_width=True)

    st.info(
        "This model deliberately uses only **session-level, pre-purchase** features (traffic source, device, "
        "repeat-visit status) — no downstream behavior like reaching the cart. That avoids data leakage and keeps "
        "the model usable for real-time targeting, before a purchase decision has been made."
    )

# ============================= TAB 2: MODEL PERFORMANCE =============================
with tab2:
    st.markdown("### Honest Evaluation")
    c1, c2, c3 = st.columns(3)
    c1.metric("Test ROC-AUC", f"{auc:.3f}")
    c2.metric("Features Used", "3")
    c3.metric("Training Sessions", f"{len(data['model_features']):,}")

    st.warning(
        f"An AUC of **{auc:.3f}** is modest — meaningfully better than random (0.50) but far from a strong "
        "discriminator. With only 3 behavioral features and no demographic or intent signals, this is close to the "
        "realistic ceiling for this feature set. The value of this model is in **ranking and calibration**, not "
        "raw classification power — see the decile chart below."
    )

    st.markdown("### ROC Curve")
    st.caption("Shows the trade-off between catching real converters (true positive rate) and false alarms (false positive rate) at every possible cutoff.")
    fpr, tpr, _ = roc_curve(y_test, test_probs)
    fig_roc = go.Figure()
    fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines", name=f"Model (AUC = {auc:.3f})", line=dict(color=NAVY, width=3)))
    fig_roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Random guess (AUC = 0.50)", line=dict(color=GREY, dash="dash")))
    fig_roc.update_layout(title="ROC Curve — Test Set", xaxis_title="False Positive Rate", yaxis_title="True Positive Rate")
    st.plotly_chart(styled_fig(fig_roc, height=380), use_container_width=True)

    st.markdown("### Model Calibration — Decile Analysis")
    st.caption("Sessions ranked by predicted probability, split into deciles. A well-calibrated model shows actual conversion rate tracking predicted probability closely.")

    calib_df = pd.DataFrame({"predicted_prob": test_probs, "actual": y_test.values})
    calib_df["decile"] = pd.qcut(calib_df["predicted_prob"], 10, labels=False, duplicates="drop")
    decile_summary = calib_df.groupby("decile").agg(
        avg_predicted=("predicted_prob", "mean"),
        actual_rate=("actual", "mean"),
    ).reset_index()
    decile_summary["avg_predicted"] *= 100
    decile_summary["actual_rate"] *= 100

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=decile_summary["decile"], y=decile_summary["actual_rate"], name="Actual Conversion Rate", marker_color=NAVY))
    fig2.add_trace(go.Bar(x=decile_summary["decile"], y=decile_summary["avg_predicted"], name="Model Predicted Probability", marker_color=GOLD))
    fig2.update_layout(title="Model Calibration by Decile (Test Set)", barmode="group", xaxis_title="Decile (0 = lowest predicted, 9 = highest)")
    st.plotly_chart(styled_fig(fig2), use_container_width=True)

    top_rate = decile_summary["actual_rate"].max()
    bottom_rate = decile_summary["actual_rate"].min()
    st.success(
        f"The top-ranked segment converts at **{top_rate:.1f}%** vs. **{bottom_rate:.1f}%** in the bottom segment — "
        f"a **{top_rate/bottom_rate:.1f}x spread** the model reliably separates. Even with modest AUC, this makes the "
        "model genuinely useful for prioritizing marketing spend."
    )

    st.markdown("### Model Coefficients")
    coef_df = pd.DataFrame({"Feature": feature_cols, "Coefficient": model.coef_[0]}).sort_values("Coefficient")
    fig3 = go.Figure(go.Bar(
        x=coef_df["Coefficient"], y=coef_df["Feature"], orientation="h",
        marker_color=[RED if c < 0 else NAVY for c in coef_df["Coefficient"]]
    ))
    fig3.update_layout(title="Feature Coefficients (positive = increases conversion likelihood)")
    st.plotly_chart(styled_fig(fig3, height=320), use_container_width=True)
