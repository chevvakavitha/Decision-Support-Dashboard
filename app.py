import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Decision Support Dashboard",
    layout="wide"
)

# =====================================================
# STYLING (PROFESSIONAL)
# =====================================================
st.markdown("""
<style>
.stApp {
    background-color: #f4f7fb;
}

.header {
    background: linear-gradient(90deg, #111827, #1f2937);
    color: white;
    padding: 26px;
    border-radius: 16px;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 14px;
}

.decision-high { border-left: 6px solid #dc2626; }
.decision-medium { border-left: 6px solid #f59e0b; }
.decision-low { border-left: 6px solid #16a34a; }

.metric {
    text-align: center;
}
.metric h1 {
    margin: 0;
    font-size: 36px;
}
.metric p {
    margin: 0;
    font-size: 13px;
    color: #6b7280;
}

.section {
    margin-top: 28px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# FILE UPLOAD
# =====================================================
file = st.file_uploader("Upload CSV or Excel dataset", type=["csv", "xlsx"])

if not file:
    st.info("Upload a dataset to generate a decision.")
    st.stop()

df = pd.read_csv(file) if file.name.endswith("csv") else pd.read_excel(file)

dataset_title = os.path.splitext(file.name)[0].replace("_", " ").replace("-", " ").title()

# =====================================================
# HEADER
# =====================================================
st.markdown(f"""
<div class="header">
<h1>Final Decision Summary</h1>
<p style="opacity:0.8;">Dataset: {dataset_title}</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# METRIC SELECTION
# =====================================================
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

if not numeric_cols:
    st.error("No numeric columns available for decision evaluation.")
    st.stop()

metric = st.selectbox("Select numeric metric for decision evaluation", numeric_cols)
series = df[metric].dropna()

# =====================================================
# DECISION CONTEXT
# =====================================================
total_records = len(series)
recent_ratio = 0.2
recent_n = max(3, int(total_records * recent_ratio))
baseline_n = total_records - recent_n

recent = series.tail(recent_n)
baseline = series.head(baseline_n)

st.markdown("## Decision Context")
ctx1, ctx2, ctx3, ctx4 = st.columns(4)

ctx1.markdown(f"<div class='card metric'><h1>{total_records}</h1><p>Records Analyzed</p></div>", unsafe_allow_html=True)
ctx2.markdown(f"<div class='card metric'><h1>{recent_n}</h1><p>Recent Window</p></div>", unsafe_allow_html=True)
ctx3.markdown(f"<div class='card metric'><h1>{baseline_n}</h1><p>Baseline Window</p></div>", unsafe_allow_html=True)
ctx4.markdown(f"<div class='card metric'><h1>{metric}</h1><p>Metric Evaluated</p></div>", unsafe_allow_html=True)

# =====================================================
# SIGNAL COMPUTATION
# =====================================================
baseline_mean = baseline.mean()
recent_mean = recent.mean()

baseline_std = baseline.std()
recent_std = recent.std()

change_ratio = (recent_mean - baseline_mean) / abs(baseline_mean) if baseline_mean != 0 else 0
variability_ratio = recent_std / baseline_std if baseline_std != 0 else 0

trend_signs = np.sign(series.diff()).dropna()
trend_consistency = abs(trend_signs.mean())

# =====================================================
# DECISION READINESS SCORE
# =====================================================
score = 100
score -= 35 if change_ratio < 0 else 0
score -= 30 if variability_ratio > 1.2 else 0
score -= 20 if trend_consistency < 0.6 else 0
score -= 15 if total_records < 20 else 0
score = int(max(0, min(100, score)))

# =====================================================
# PRIORITY CLASSIFICATION
# =====================================================
if change_ratio < 0 and variability_ratio > 1.2:
    priority = "High"
    decision_class = "decision-high"
elif variability_ratio > 1.2 or trend_consistency < 0.6:
    priority = "Medium"
    decision_class = "decision-medium"
else:
    priority = "Low"
    decision_class = "decision-low"

# =====================================================
# DECISION CONFIDENCE
# =====================================================
if total_records >= 40 and trend_consistency >= 0.7:
    confidence = "High"
elif total_records >= 20:
    confidence = "Medium"
else:
    confidence = "Low"

# =====================================================
# FINAL DECISION
# =====================================================
st.markdown("## Final Decision")
st.markdown(f"""
<div class="card {decision_class}">
<h2>Priority Level: {priority}</h2>
<p><strong>Decision Readiness Score:</strong> {score} / 100</p>
<p><strong>Decision Confidence:</strong> {confidence}</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# WHY THIS DECISION
# =====================================================
st.markdown("## Why this decision was generated")

reasons = []

reasons.append(
    "Recent values decreased compared to baseline"
    if change_ratio < 0 else
    "Recent values did not decrease compared to baseline"
)

reasons.append(
    "Recent variability increased relative to baseline"
    if variability_ratio > 1.2 else
    "Recent variability remains within baseline range"
)

reasons.append(
    "Trend direction is inconsistent"
    if trend_consistency < 0.6 else
    "Trend direction remains consistent"
)

for r in reasons:
    st.markdown(f"- {r}")

# =====================================================
# DECISION STABILITY
# =====================================================
st.markdown("## Decision Stability")

if trend_consistency >= 0.75 and variability_ratio < 1.1:
    stability = "High"
elif trend_consistency >= 0.6:
    stability = "Medium"
else:
    stability = "Low"

st.info(f"Decision Stability: **{stability}**")

# =====================================================
# WHAT-IF SIMULATION
# =====================================================
st.markdown("## What-If Scenario Simulation")

colA, colB = st.columns(2)

with colA:
    simulated_drop = st.slider(
        "Simulated decrease (%)",
        0, 50, 10
    )

with colB:
    simulated_variability = st.slider(
        "Simulated variability increase (%)",
        0, 50, 10
    )

sim_change = change_ratio - simulated_drop / 100
sim_variability = variability_ratio * (1 + simulated_variability / 100)

if sim_change < 0 and sim_variability > 1.2:
    sim_priority = "High"
elif sim_variability > 1.2:
    sim_priority = "Medium"
else:
    sim_priority = "Low"

st.markdown("### Scenario Outcome")
st.warning(f"Under this simulation → Priority becomes **{sim_priority}**")

# =====================================================
# DECISION COMPARISON
# =====================================================
st.markdown("## Decision Comparison")

d1, d2 = st.columns(2)

d1.markdown(
    f"<div class='card'><h3>Current</h3><p>Priority: {priority}</p><p>Score: {score}</p><p>Confidence: {confidence}</p></div>",
    unsafe_allow_html=True
)

d2.markdown(
    f"<div class='card'><h3>Simulated</h3><p>Priority: {sim_priority}</p><p>Score: recalculated</p><p>Confidence: adjusted</p></div>",
    unsafe_allow_html=True
)

# =====================================================
# RECOMMENDED ACTIONS
# =====================================================
st.markdown("## Recommended Actions")

if priority == "High":
    actions = [
        "Avoid decisions dependent on this metric",
        "Increase monitoring frequency",
        "Reduce exposure until stability improves"
    ]
elif priority == "Medium":
    actions = [
        "Monitor metric more frequently",
        "Delay irreversible decisions",
        "Wait for trend stabilization"
    ]
else:
    actions = [
        "Current state acceptable for continuation",
        "Maintain regular monitoring",
        "No immediate adjustment required"
    ]

for a in actions:
    st.markdown(f"- {a}")

# =====================================================
# OPTIONAL SUPPORTING VISUAL (MINIMAL)
# =====================================================
st.markdown("## Supporting Trend View")

fig, ax = plt.subplots(figsize=(7, 2))
ax.plot(series.values, linewidth=1.5)
ax.set_title(metric)
ax.set_xticks([])
st.pyplot(fig)
plt.close(fig)
