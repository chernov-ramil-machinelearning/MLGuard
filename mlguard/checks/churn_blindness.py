import pandas as pd
from scipy.stats import ks_2samp


def check_churn_blindness(
    df: pd.DataFrame, 
    status_col: str = None, 
    threshold_pvalue: float = 0.05
) -> list[dict]:
    findings = []

    if status_col is None:
        possible_status_cols = [c for c in df.columns if set(df[c].dropna().unique()).issubset({0, 1})]
        if not possible_status_cols:
            return findings
        status_col = possible_status_cols[0]

    if status_col not in df.columns:
        return findings

    active_df = df[df[status_col] == 1]
    churned_df = df[df[status_col] == 0]

    if len(active_df) == 0 or len(churned_df) == 0:
        return findings

    numeric_cols = df.select_dtypes(include='number').columns

    for col in numeric_cols:
        if col == status_col:
            continue

        stat_result = ks_2samp(active_df[col], churned_df[col])

        if stat_result.pvalue < threshold_pvalue:
            findings.append({
                'check': 'churn_blindness',
                'severity': 'CRITICAL',
                'column': col,
                'metric_value': round(float(stat_result.pvalue), 4),
                'threshold': threshold_pvalue,
                'message': f"Distribution shift detected for '{col}' between active and churned clients (p-value = {stat_result.pvalue:.4f})."
            })

    return findings