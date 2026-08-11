import numpy as np
import pandas as pd

def make_leakage_dataset(n: int = 1000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    
    target_event_time = pd.date_range(start='2026-01-01', periods=n, freq='30min')
    target = rng.integers(low=0, high=2, size=n)
    
    leaky_corr_feature = target + rng.normal(loc=0.0, scale=0.05, size=n)
    
    # 1. СНАЧАЛА создаем переменную future_hours
    future_hours = rng.integers(low=1, high=6, size=n)
    
    # 2. ЗАТЕМ используем её!
    leaky_time_feature = target_event_time + pd.to_timedelta(future_hours, unit='h')
    
    age = rng.integers(low=18, high=65, size=n)
    salary = rng.normal(loc=60000, scale=15000, size=n).round(2)
    score = rng.uniform(low=0.0, high=1.0, size=n).round(2)
    
    df = pd.DataFrame({
        'user_id': np.arange(1001, 1001 + n),
        'target_event_time': target_event_time,
        'age': age,
        'salary': salary,
        'credit_score': score,
        'leaky_corr_feature': leaky_corr_feature.round(4),
        'feature_calc_time': leaky_time_feature,
        'target': target
    })
    
    return df
# Проверка работы генератора
if __name__ == '__main__':
    df = make_leakage_dataset(n=5)
    print(df.to_string())
