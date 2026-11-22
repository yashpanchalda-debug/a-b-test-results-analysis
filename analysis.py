"""
analysis.py
Performs statistical A/B test analysis on ab_test_data.csv.
Includes SQL exploration via SQLite, hypothesis testing, and visualization.
"""

import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest, proportion_confint

# ── 1. Load Data ──────────────────────────────────────────────────────────────
df = pd.read_csv("ab_test_data.csv")
print("=== Dataset Preview ===")
print(df.head())
print(f"\nShape: {df.shape}\n")

# ── 2. SQL Exploration via SQLite ─────────────────────────────────────────────
conn = sqlite3.connect(":memory:")
df.to_sql("ab_test", conn, index=False, if_exists="replace")

sql_summary = """
SELECT
    group_name,
    COUNT(*)                          AS total_users,
    SUM(converted)                    AS total_conversions,
    ROUND(AVG(converted) * 100, 2)    AS conversion_rate_pct,
    ROUND(AVG(session_duration_sec), 1) AS avg_session_sec
FROM (
    SELECT
        "group" AS group_name,
        converted,
        session_duration_sec
    FROM ab_test
)
GROUP BY group_name
ORDER BY group_name;
"""

print("=== SQL Summary (via SQLite) ===")
sql_result = pd.read_sql_query(sql_summary, conn)
print(sql_result.to_string(index=False))
print()

conn.close()

# ── 3. Compute Key Metrics ────────────────────────────────────────────────────
summary = df.groupby("group").agg(
    total_users=("user_id", "count"),
    total_conversions=("converted", "sum"),
).reset_index()

summary["conversion_rate"] = summary["total_conversions"] / summary["total_users"]

control   = summary[summary["group"] == "control"].iloc[0]
treatment = summary[summary["group"] == "treatment"].iloc[0]

print("=== Conversion Summary ===")
print(summary.to_string(index=False))
print()

# ── 4. Two-Proportion Z-Test ──────────────────────────────────────────────────
count = np.array([treatment["total_conversions"], control["total_conversions"]])
nobs  = np.array([treatment["total_users"],       control["total_users"]])

z_stat, p_value = proportions_ztest(count, nobs)

alpha = 0.05
print("=== Hypothesis Test ===")
print(f"H0: Conversion rate(treatment) == Conversion rate(control)")
print(f"H1: Conversion rate(treatment) != Conversion rate(control)")
print(f"Significance level (alpha): {alpha}")
print(f"Z-statistic : {z_stat:.4f}")
print(f"P-value     : {p_value:.4f}")

if p_value < alpha:
    print("Result      : REJECT H0 — statistically significant difference detected.")
else:
    print("Result      : FAIL TO REJECT H0 — no statistically significant difference.")

# ── 5. Confidence Intervals ───────────────────────────────────────────────────
ci_control   = proportion_confint(control["total_conversions"],   control["total_users"],   alpha=0.05)
ci_treatment = proportion_confint(treatment["total_conversions"], treatment["total_users"], alpha=0.05)

lift = treatment["conversion_rate"] - control["conversion_rate"]

print(f"\n=== Confidence Intervals (95%) ===")
print(f"Control   : {ci_control[0]:.4f} – {ci_control[1]:.4f}  (rate: {control['conversion_rate']:.4f})")
print(f"Treatment : {ci_treatment[0]:.4f} – {ci_treatment[1]:.4f}  (rate: {treatment['conversion_rate']:.4f})")
print(f"Absolute lift: {lift:+.4f} ({lift*100:+.2f} percentage points)")

# ── 6. Recommendation ────────────────────────────────────────────────────────
print("\n=== Business Recommendation ===")
if p_value < alpha and lift > 0:
    print(
        f"The treatment page shows a statistically significant improvement.\n"
        f"Conversion rate increased from {control['conversion_rate']:.2%} to "
        f"{treatment['conversion_rate']:.2%} (+{lift*100:.2f} pp, p={p_value:.4f}).\n"
        f"Recommendation: SHIP the new landing page."
    )
elif p_value < alpha and lift < 0:
    print(
        f"The treatment page performs significantly WORSE than control.\n"
        f"Recommendation: DO NOT ship. Revert to control page."
    )
else:
    print(
        f"No statistically significant difference detected (p={p_value:.4f}).\n"
        f"Recommendation: Continue testing or investigate other metrics."
    )

# ── 7. Visualization ──────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# -- Plot 1: Conversion Rates with CI bars
groups_labels = ["Control", "Treatment"]
rates = [control["conversion_rate"], treatment["conversion_rate"]]
errors = [
    [control["conversion_rate"]   - ci_control[0],   ci_control[1]   - control["conversion_rate"]],
    [treatment["conversion_rate"] - ci_treatment[0], ci_treatment[1] - treatment["conversion_rate"]],
]
errors_low  = [e[0] for e in errors]
errors_high = [e[1] for e in errors]

colors = ["#5B9BD5", "#ED7D31"]
bars = axes[0].bar(groups_labels, rates, color=colors, width=0.4, edgecolor="black")
axes[0].errorbar(
    groups_labels, rates,
    yerr=[errors_low, errors_high],
    fmt="none", color="black", capsize=8, linewidth=2,
)
axes[0].set_title("Conversion Rate by Group\n(with 95% CI)", fontsize=13)
axes[0].set_ylabel("Conversion Rate")
axes[0].set_ylim(0, max(rates) * 1.4)

for bar, rate in zip(bars, rates):
    axes[0].text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.004,
        f"{rate:.2%}",
        ha="center", va="bottom", fontweight="bold"
    )

# -- Plot 2: Total Conversions
conversions = [control["total_conversions"], treatment["total_conversions"]]
bars2 = axes[1].bar(groups_labels, conversions, color=colors, width=0.4, edgecolor="black")
axes[1].set_title("Total Conversions by Group", fontsize=13)
axes[1].set_ylabel("Number of Conversions")
axes[1].set_ylim(0, max(conversions) * 1.3)

for bar, val in zip(bars2, conversions):
    axes[1].text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 5,
        str(int(val)),
        ha="center", va="bottom", fontweight="bold"
    )

# Annotate p-value
sig_label = f"p = {p_value:.4f} ({'significant' if p_value < alpha else 'not significant'})"
fig.text(0.5, 0.01, sig_label, ha="center", fontsize=11, style="italic", color="darkred")

plt.tight_layout(rect=[0, 0.04, 1, 1])
plt.savefig("conversion_plot.png", dpi=150)
print("\nPlot saved: conversion_plot.png")
plt.show()