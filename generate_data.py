"""
generate_data.py
Generates a synthetic A/B test dataset and saves it as ab_test_data.csv.
"""

import pandas as pd
import numpy as np

np.random.seed(42)

N = 10_000  # total users

user_ids = range(1, N + 1)

# Randomly assign users to control or treatment
groups = np.random.choice(["control", "treatment"], size=N, p=[0.5, 0.5])

# Conversion rates: control ~10.5%, treatment ~12.5%
conversion_probs = np.where(groups == "control", 0.105, 0.125)
conversions = np.random.binomial(1, conversion_probs)

# Random session duration in seconds (not used in core test, but realistic)
session_duration = np.round(
    np.random.exponential(scale=120, size=N) + 30, 1
)

df = pd.DataFrame({
    "user_id": user_ids,
    "group": groups,
    "converted": conversions,
    "session_duration_sec": session_duration,
})

df.to_csv("ab_test_data.csv", index=False)
print(f"Dataset saved: {len(df)} rows")
print(df["group"].value_counts())
print(df.groupby("group")["converted"].mean().rename("conversion_rate"))