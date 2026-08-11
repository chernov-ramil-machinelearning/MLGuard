import numpy as np
import pandas as pd
from pathlib import Path


def generate_bank_churn_dataset(n: int = 500) -> pd.DataFrame:
    np.random.seed(42)
    customer_id = np.arange(1000, 1000 + n)
    age = np.random.randint(21, 65, size=n)
    credit_score = np.random.randint(500, 850, size=n)
    
    is_churn = np.random.choice([0, 1], size=n, p=[0.8, 0.2])
    
    salary = np.where(is_churn == 1, np.random.normal(45000, 10000, n), np.random.normal(120000, 25000, n))
    salary = np.clip(salary, 20000, 300000)

    closure_event_flag = is_churn.copy()
    flip_mask = np.random.rand(n) < 0.01
    closure_event_flag[flip_mask] = 1 - closure_event_flag[flip_mask]

    df = pd.DataFrame({
        "customer_id": customer_id,
        "age": age,
        "credit_score": credit_score,
        "salary": np.round(salary, 2),
        "closure_event_flag": closure_event_flag,
        "is_churn": is_churn,
    })
    return df


def generate_retail_sales_dataset(periods: int = 30) -> pd.DataFrame:
    np.random.seed(42)
    dates = pd.date_range(start="2026-01-01", periods=periods, freq="D")
    
    order_volume = np.linspace(100, 500, periods) + np.random.normal(0, 10, periods)
    net_profit_margin = np.linspace(0.35, 0.05, periods) + np.random.normal(0, 0.01, periods)
    
    seasonal_cycle = np.sin(np.linspace(0, 8 * np.pi, periods)) * 30000
    weekly_revenue = np.linspace(100000, 250000, periods) + seasonal_cycle + np.random.normal(0, 5000, periods)

    df = pd.DataFrame({
        "date": dates,
        "order_volume": np.round(order_volume, 0),
        "net_profit_margin": np.round(net_profit_margin, 4),
        "weekly_revenue": np.round(weekly_revenue, 2),
    })
    return df


def main():
    out_dir = Path(__file__).parent
    
    bank_df = generate_bank_churn_dataset()
    bank_df.to_csv(out_dir / "bank_churn_pitfalls.csv", index=False)

    retail_df = generate_retail_sales_dataset()
    retail_df.to_csv(out_dir / "retail_sales_pitfalls.csv", index=False)


if __name__ == "__main__":
    main()
