import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Dict, Any
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

FIGURES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "figures")

def evaluate_models(predictions: Dict[str, Any], split_info: Dict[str, Any]) -> pd.DataFrame:
    os.makedirs(FIGURES_DIR, exist_ok=True)
    y_test = split_info['y_test']
    metrics_records = []

    for name, pred in predictions.items():
        mae = mean_absolute_error(y_test, pred)
        rmse = root_mean_squared_error(y_test, pred)
        r2 = r2_score(y_test, pred)
        mape = np.mean(np.abs((y_test - pred) / y_test)) * 100.0

        metrics_records.append({
            'Model': name,
            'R2 Score': round(r2, 4),
            'MAE ($)': round(mae, 2),
            'RMSE ($)': round(rmse, 2),
            'MAPE (%)': round(mape, 2)
        })

    metrics_df = pd.DataFrame(metrics_records).sort_values('R2 Score', ascending=False).reset_index(drop=True)

    # 1. Actual vs Predicted Plot (Best Model)
    best_model_name = metrics_df.iloc[0]['Model']
    best_preds = predictions[best_model_name]
    test_df = split_info['test_df'].copy()
    test_df['predicted_sales'] = best_preds

    # Aggregate by date for clean macro visualization
    agg_eval = test_df.groupby('date')[['weekly_sales', 'predicted_sales']].sum() / 1e6

    plt.figure(figsize=(11, 5.5))
    plt.plot(agg_eval.index, agg_eval['weekly_sales'], label='Actual Sales ($M)', color='#1E3A8A', lw=2.2)
    plt.plot(agg_eval.index, agg_eval['predicted_sales'], label=f'Forecasted Sales ({best_model_name}) ($M)',
             color='#DC2626', lw=2, linestyle='--')
    plt.title(f'Actual vs Forecasted Retail Sales — Out-of-Time Test Horizon\nBest Model: {best_model_name} (R² = {metrics_df.iloc[0]["R2 Score"]:.3f})',
              fontsize=13, fontweight='bold', pad=12)
    plt.xlabel('Date', fontsize=11)
    plt.ylabel('Chain Total Weekly Sales ($ Millions)', fontsize=11)
    plt.legend(frameon=True, facecolor='white', framealpha=0.9)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    pred_path = os.path.join(FIGURES_DIR, "actual_vs_predicted.png")
    plt.savefig(pred_path, dpi=200)
    plt.close()

    return metrics_df
