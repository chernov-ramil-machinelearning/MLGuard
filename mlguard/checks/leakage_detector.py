import pandas as pd


def check_correlation_leakage(
    df: pd.DataFrame, 
    target_col: str = None, 
    threshold: float = 0.95
) -> list[dict]:
    findings = []
    numeric_df = df.select_dtypes(include='number')
    numeric_cols = list(numeric_df.columns)

    if len(numeric_cols) < 2:
        return findings

    if target_col is not None:
        if target_col not in numeric_df.columns:
            return findings

        for col in numeric_cols:
            if col == target_col:
                continue
                
            corr_value = abs(numeric_df[col].corr(numeric_df[target_col]))
            if corr_value > threshold:
                findings.append({
                    "check": "leakage_detector",
                    "severity": "CRITICAL",
                    "column": col,
                    "metric_value": round(float(corr_value), 4),
                    "threshold": threshold,
                    "message": f"Feature '{col}' has a correlation of {corr_value:.4f} with target '{target_col}'."
                })
        return findings

    for i in range(len(numeric_cols)):
        for j in range(i + 1, len(numeric_cols)):
            col1 = numeric_cols[i]
            col2 = numeric_cols[j]
            
            corr_value = abs(numeric_df[col1].corr(numeric_df[col2]))
            if corr_value > threshold:
                findings.append({
                    "check": "leakage_detector",
                    "severity": "WARNING",
                    "column": f"{col1} vs {col2}",
                    "metric_value": round(float(corr_value), 4),
                    "threshold": threshold,
                    "message": f"High correlation ({corr_value:.4f}) detected between '{col1}' and '{col2}'."
                })

    return findings