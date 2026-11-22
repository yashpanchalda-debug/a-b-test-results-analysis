# A/B Test Results Analysis

A complete statistical analysis of a simulated A/B test for a web product, demonstrating hypothesis testing, data visualization, and a clear business recommendation.

## Project Overview

A product team ran an A/B test to evaluate whether a new landing page design increases user conversion rates. This project analyzes the results using Python and SQL, applies a two-proportion z-test for statistical significance, and delivers a data-driven recommendation.

## Skills Demonstrated

- **Python**: pandas, scipy, statsmodels, matplotlib, seaborn
- **SQL**: SQLite queries for data exploration and aggregation
- **Data Visualization**: bar charts, conversion rate plots, p-value interpretation
- **Statistics**: hypothesis testing, confidence intervals, effect size

## Project Structure

```
ab-test-analysis/
├── README.md
├── generate_data.py       # Generates synthetic A/B test dataset
├── analysis.py            # Full statistical analysis and visualizations
├── queries.sql            # SQL queries used in exploratory analysis
```

## Setup & Running

### 1. Install dependencies

```bash
pip install pandas scipy statsmodels matplotlib seaborn
```

### 2. Generate the dataset

```bash
python generate_data.py
```

This creates `ab_test_data.csv` in the project directory.

### 3. Run the analysis

```bash
python analysis.py
```

This prints statistical results to the console and saves `conversion_plot.png`.

## Results Summary

After running the analysis on ~10,000 simulated users:

| Group   | Users | Conversions | Conversion Rate |
|---------|-------|-------------|-----------------|
| Control | ~5000 | ~530        | ~10.6%          |
| Treatment | ~5000 | ~630      | ~12.6%          |

- **P-value**: < 0.05 → statistically significant
- **Confidence Interval**: does not cross zero → reliable effect
- **Recommendation**: Ship the new landing page — the treatment group shows a meaningful and statistically significant lift in conversions.

> Note: Exact numbers will vary slightly because the dataset is randomly generated each run.

## Key Concepts

**Null Hypothesis (H₀):** The new page has no effect on conversion rate.  
**Alternative Hypothesis (H₁):** The new page changes the conversion rate.  
**Significance level (α):** 0.05

If the p-value < 0.05, we reject H₀ and conclude the new page performs differently from the control.

## SQL Exploration

The `queries.sql` file contains standalone SQL queries. The analysis script also runs these against an in-memory SQLite database and prints results, so you can see SQL-driven aggregations alongside the Python analysis.

---

*This is a portfolio project using synthetic data for demonstration purposes.*