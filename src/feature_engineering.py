import pandas as pd
import numpy as np

def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(['store_id', 'dept_id', 'date']).reset_index(drop=True)

    # 1. Calendar & Temporal Features
    df['week_of_year'] = df['date'].dt.isocalendar().week.astype(int)
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['is_month_end'] = df['date'].dt.is_month_end.astype(int)

    # 2. Total Promotional Markdown Activity
    df['total_markdown'] = (
        df['markdown_1'] + df['markdown_2'] + df['markdown_3'] + 
        df['markdown_4'] + df['markdown_5']
    )
    df['holiday_markdown_interaction'] = df['is_holiday'] * df['total_markdown']

    # 3. Autoregressive Lags (t-1, t-2, t-4 weeks)
    grouped = df.groupby(['store_id', 'dept_id'])['weekly_sales']
    df['lag_1_week'] = grouped.shift(1)
    df['lag_2_week'] = grouped.shift(2)
    df['lag_4_week'] = grouped.shift(4)

    # 4. Rolling Statistics (4-week moving average & volatility)
    df['rolling_mean_4w'] = grouped.shift(1).rolling(window=4, min_periods=1).mean()
    df['rolling_std_4w'] = grouped.shift(1).rolling(window=4, min_periods=1).std().fillna(0)

    # 5. One-Hot Encoding for Store Type
    df = pd.get_dummies(df, columns=['store_type'], drop_first=True)

    # Drop early rows containing NaN due to lag-4 shift
    df = df.dropna().reset_index(drop=True)
    return df
