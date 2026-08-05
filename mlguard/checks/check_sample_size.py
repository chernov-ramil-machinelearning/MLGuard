import pandas as pd
import numpy as np


def check_sample_size(
    df: pd.DataFrame, 
    target_col: str = None, 
    min_samples: int = 200
) -> list[dict]:
    findings = []
    bootstrap_means = []

    if len(df) < min_samples:
        findings.append({
            "check": "small_sample_guard",
            "severity": "WARNING",
            "column": "all",
            "metric_value": len(df),
            "threshold": min_samples,
            "message": f"Sample size ({len(df)}) is below the minimum threshold ({min_samples})."
        })

    target_cols_to_check = []
    if target_col is not None and target_col in df.columns:
        target_cols_to_check.append(target_col)
    else:
        target_cols_to_check = [c for c in df.columns if df[c].nunique() <= 10]

    for col in target_cols_to_check:
        proportions = df[col].value_counts(normalize=True)
        if len(proportions) > 1 and proportions.min() < 0.15:
            findings.append({
                "check": "small_sample_guard",
                "severity": "WARNING",
                "column": col,
                "metric_value": round(float(proportions.min()), 4),
                "threshold": 0.15,
                "message": f"Class imbalance detected in '{col}': minority class represents {proportions.min():.1%}."
            })

    num_cols = df.select_dtypes(include='number').columns
    eval_col = target_col if (target_col in num_cols) else (num_cols[0] if len(num_cols) > 0 else None)

    if eval_col is not None:
        for _ in range(1000):
            sample = np.random.choice(df[eval_col], size=len(df), replace=True)
            bootstrap_means.append(sample.mean())

        p_97 = np.percentile(bootstrap_means, 97.5)
        p_2 = np.percentile(bootstrap_means, 2.5)
        difference = p_97 - p_2

        if difference > 0.20:
            findings.append({
                "check": "small_sample_guard",
                "severity": "CRITICAL",
                "column": eval_col,
                "metric_value": round(float(difference), 4),
                "threshold": 0.20,
                "message": f"High uncertainty for '{eval_col}': 95% CI [{p_2:.3f}, {p_97:.3f}], width {difference:.3f}."
            })

    return findings