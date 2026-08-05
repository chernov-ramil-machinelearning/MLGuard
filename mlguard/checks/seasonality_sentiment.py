import pandas as pd
from statsmodels.tsa.seasonal import STL


def check_seasonality(
    df: pd.DataFrame, 
    time_col: str = None, 
    target_col: str = None, 
    threshold_ratio: float = 0.30
) -> list[dict]:
    findings = []

    if time_col is None:
        date_cols = df.select_dtypes(include=['datetime', 'datetime64']).columns
        if len(date_cols) > 0:
            time_col = date_cols[0]
        else:
            for col in df.columns:
                if 'date' in col.lower() or 'time' in col.lower():
                    time_col = col
                    break

    if time_col is None or time_col not in df.columns:
        return findings

    df_copy = df.copy()
    df_copy[time_col] = pd.to_datetime(df_copy[time_col])
    df_sorted = df_copy.sort_values(by=time_col).set_index(time_col)
    df_resampled = df_sorted.resample('D').mean(numeric_only=True).ffill()

    if target_col and target_col in df_resampled.columns:
        numeric_cols = [target_col]
    else:
        numeric_cols = df_resampled.select_dtypes(include='number').columns

    for col in numeric_cols:
        series = df_resampled[col].dropna()
        
        if len(series) < 14:
            continue

        try:
            stl = STL(series, period=7)
            res = stl.fit()

            var_total = series.var()
            if var_total == 0:
                continue

            seasonal_ratio = res.seasonal.var() / var_total

            if seasonal_ratio > threshold_ratio:
                findings.append({
                    'check': 'seasonality_sentiment',
                    'severity': 'WARNING',
                    'column': col,
                    'metric_value': round(float(seasonal_ratio), 4),
                    'threshold': threshold_ratio,
                    'message': f"High seasonality in '{col}': seasonal component explains {seasonal_ratio:.1%} of total variance."
                })
        except Exception:
            continue

    return findings