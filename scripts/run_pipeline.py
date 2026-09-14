import os
import sys

# Ensure root directory is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_generator import generate_retail_dataset
from src.database import load_analytical_dataframe
from src.eda import run_exploratory_data_analysis
from src.feature_engineering import build_feature_matrix
from src.models import train_forecasting_models
from src.evaluator import evaluate_models

def run_complete_pipeline():
    print("====================================================================")
    print("  RETAIL CHAIN SALES FORECASTING — END-TO-END PIPELINE")
    print("====================================================================")

    # 1. Data Ingestion & SQL Database Seeding
    generate_retail_dataset(num_stores=10, num_depts=12, start_year=2024, weeks_count=130)

    # 2. Exploratory Data Analysis
    eda_summary = run_exploratory_data_analysis()

    # 3. Load & Feature Engineering
    df = load_analytical_dataframe()
    feat_df = build_feature_matrix(df)

    # 4. Model Training & Out-of-Time Forecasting
    models, predictions, split_info = train_forecasting_models(feat_df)

    # 5. Model Evaluation & Benchmark Metrics
    metrics_df = evaluate_models(predictions, split_info)

    print("\n==> FINAL MODEL BENCHMARK RESULTS:")
    print(metrics_df.to_string(index=False))
    print("\n==> Pipeline execution finished successfully!")

if __name__ == "__main__":
    run_complete_pipeline()
