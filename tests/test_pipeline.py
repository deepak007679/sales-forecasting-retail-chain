import os
import pytest
import pandas as pd
from src.database import get_connection, load_analytical_dataframe, execute_query
from src.data_generator import generate_retail_dataset
from src.feature_engineering import build_feature_matrix
from src.models import train_forecasting_models

@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    # Generate smaller dataset for quick unit testing
    generate_retail_dataset(num_stores=3, num_depts=3, start_year=2024, weeks_count=40)
    yield

def test_database_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM stores;")
    stores_count = cursor.fetchone()[0]
    assert stores_count == 3

    cursor.execute("SELECT COUNT(*) FROM weekly_sales;")
    sales_count = cursor.fetchone()[0]
    assert sales_count > 0
    conn.close()

def test_sql_analytics_query():
    sql = """
    SELECT store_type, ROUND(AVG(weekly_sales), 2) AS mean_sales
    FROM weekly_sales w
    JOIN stores s ON w.store_id = s.store_id
    GROUP BY store_type;
    """
    rows = execute_query(sql)
    assert len(rows) > 0
    assert all(r['mean_sales'] > 0 for r in rows)

def test_feature_engineering():
    df = load_analytical_dataframe()
    feat_df = build_feature_matrix(df)
    
    assert 'week_of_year' in feat_df.columns
    assert 'lag_1_week' in feat_df.columns
    assert 'rolling_mean_4w' in feat_df.columns
    assert feat_df['lag_1_week'].isna().sum() == 0

def test_model_training_and_accuracy():
    df = load_analytical_dataframe()
    feat_df = build_feature_matrix(df)
    models, preds, split_info = train_forecasting_models(feat_df)

    assert 'Linear Regression (OLS)' in models
    assert 'Random Forest Regressor' in models
    assert len(preds['Random Forest Regressor']) == len(split_info['y_test'])
    assert len(preds['Random Forest Regressor']) > 0
