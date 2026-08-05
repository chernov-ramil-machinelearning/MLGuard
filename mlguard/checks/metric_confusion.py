import pandas as pd
from scipy.stats import kendalltau


def check_metric_confusion(
    df: pd.DataFrame, 
    time_col: str, 
    vanity_col: str = None, 
    health_col: str = None, 
    alpha: float = 0.05
) -> list[dict]:
    findings = []

    if time_col not in df.columns:
        return findings

    df_sorted = df.sort_values(by=time_col).reset_index(drop=True)
    time_idx = list(range(len(df_sorted)))

    if vanity_col is None or health_col is None:
        numeric_cols = [c for c in df_sorted.select_dtypes(include='number').columns if c != time_col]
        
        increasing_cols = []
        decreasing_cols = []

        for col in numeric_cols:
            tau, pval = kendalltau(time_idx, df_sorted[col])
            if pval < alpha:
                if tau > 0:
                    increasing_cols.append((col, tau, pval))
                elif tau < 0:
                    decreasing_cols.append((col, tau, pval))

        for v_name, v_tau, v_p in increasing_cols:
            for h_name, h_tau, h_p in decreasing_cols:
                findings.append({
                    'check': 'metric_confusion',
                    'severity': 'CRITICAL',
                    'column': f"{v_name} vs {h_name}",
                    'metric_value': round(float(v_p), 4),
                    'threshold': alpha,
                    'message': f"Metric divergence: '{v_name}' is increasing (tau={v_tau:.2f}, p={v_p:.4f}), while '{h_name}' is decreasing (tau={h_tau:.2f}, p={h_p:.4f})."
                })
        return findings

    if vanity_col not in df.columns or health_col not in df.columns:
        return findings

    tau_v, pval_v = kendalltau(time_idx, df_sorted[vanity_col])
    tau_h, pval_h = kendalltau(time_idx, df_sorted[health_col])

    if (tau_v > 0 and pval_v < alpha) and (tau_h < 0 and pval_h < alpha):
        findings.append({
            'check': 'metric_confusion',
            'severity': 'CRITICAL',
            'column': f"{vanity_col} vs {health_col}",
            'metric_value': round(float(pval_v), 4),
            'threshold': alpha,
            'message': f"Metric divergence: '{vanity_col}' is increasing (tau={tau_v:.2f}, p={pval_v:.4f}), while '{health_col}' is decreasing (tau={tau_h:.2f}, p={pval_h:.4f})."
        })

    return findings