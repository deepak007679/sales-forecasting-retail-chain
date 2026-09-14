import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

def train_forecasting_models(df: pd.DataFrame) -> Tuple[Dict[str, Any], Dict[str, Any], Any]:
    # Chronological out-of-time train/test split (80% train, 20% test)
    unique_dates = sorted(df['date'].unique())
    split_idx = int(len(unique_dates) * 0.80)
    split_date = unique_dates[split_idx]

    train_mask = df['date'] < split_date
    test_mask = df['date'] >= split_date

    feature_cols = [
        'store_id', 'dept_id', 'size_sqft', 'temperature', 'fuel_price',
        'cpi', 'unemployment', 'is_holiday', 'week_of_year', 'month', 'quarter',
        'total_markdown', 'holiday_markdown_interaction',
        'lag_1_week', 'lag_2_week', 'lag_4_week', 'rolling_mean_4w', 'rolling_std_4w'
    ]
    # Add one-hot encoded store type columns if present
    for col in ['store_type_B', 'store_type_C']:
        if col in df.columns:
            feature_cols.append(col)

    X_train = df.loc[train_mask, feature_cols]
    y_train = df.loc[train_mask, 'weekly_sales']
    X_test = df.loc[test_mask, feature_cols]
    y_test = df.loc[test_mask, 'weekly_sales']

    models = {
        'Linear Regression (OLS)': LinearRegression(),
        'Ridge Regression': Ridge(alpha=10.0),
        'Random Forest Regressor': RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1),
        'Gradient Boosting Regressor': GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    }

    trained_models = {}
    predictions = {}

    print(f"Training models on {len(X_train)} samples, testing on {len(X_test)} samples (Split Date: {split_date.strftime('%Y-%m-%d')})...")

    for name, model in models.items():
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        trained_models[name] = model
        predictions[name] = pred

    split_info = {
        'split_date': split_date,
        'X_train': X_train,
        'y_train': y_train,
        'X_test': X_test,
        'y_test': y_test,
        'feature_cols': feature_cols,
        'test_df': df.loc[test_mask].copy()
    }

    return trained_models, predictions, split_info
