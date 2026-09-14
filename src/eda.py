import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from src.database import load_analytical_dataframe

FIGURES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "figures")

def run_exploratory_data_analysis():
    os.makedirs(FIGURES_DIR, exist_ok=True)
    df = load_analytical_dataframe()

    print("==> Executing Exploratory Data Analysis (EDA)...")
    summary = {
        'total_records': len(df),
        'unique_stores': df['store_id'].nunique(),
        'unique_departments': df['dept_id'].nunique(),
        'date_range': f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}",
        'mean_weekly_sales': round(df['weekly_sales'].mean(), 2),
        'median_weekly_sales': round(df['weekly_sales'].median(), 2),
        'total_revenue_usd': round(df['weekly_sales'].sum(), 2)
    }

    # 1. Weekly Sales Trend & Seasonality Plot
    plt.figure(figsize=(12, 5))
    weekly_trend = df.groupby('date')['weekly_sales'].sum() / 1e6
    plt.plot(weekly_trend.index, weekly_trend.values, color='#1E3A8A', lw=2, label='Total Chain Sales ($M)')
    plt.title('Retail Chain Weekly Sales Trajectory (2024 - 2026)', fontsize=14, fontweight='bold', pad=12)
    plt.xlabel('Date', fontsize=11)
    plt.ylabel('Total Weekly Sales ($ Millions)', fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    trend_path = os.path.join(FIGURES_DIR, "eda_sales_trend.png")
    plt.savefig(trend_path, dpi=200)
    plt.close()

    # 2. Holiday Lift Factor Boxplot
    plt.figure(figsize=(7, 5))
    hol_data = [df[df['is_holiday'] == 0]['weekly_sales'], df[df['is_holiday'] == 1]['weekly_sales']]
    plt.boxplot(hol_data, patch_artist=True, tick_labels=['Regular Week', 'Holiday Week'],
                boxprops=dict(facecolor='#93C5FD', color='#1E40AF'),
                medianprops=dict(color='#DC2626', lw=2))
    plt.title('Sales Distribution: Regular vs Holiday Weeks', fontsize=13, fontweight='bold')
    plt.ylabel('Weekly Sales ($)', fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    hol_path = os.path.join(FIGURES_DIR, "eda_holiday_lift.png")
    plt.savefig(hol_path, dpi=200)
    plt.close()

    # 3. Store Type Performance
    plt.figure(figsize=(8, 4.5))
    type_summary = df.groupby('store_type')['weekly_sales'].mean()
    colors_list = ['#2563EB', '#10B981', '#F59E0B']
    plt.bar(type_summary.index, type_summary.values, color=colors_list, width=0.5)
    plt.title('Mean Weekly Sales by Store Type (A: Supercenter, B: Discount, C: Express)', fontsize=12, fontweight='bold')
    plt.ylabel('Mean Weekly Sales ($)', fontsize=11)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    store_path = os.path.join(FIGURES_DIR, "eda_store_type.png")
    plt.savefig(store_path, dpi=200)
    plt.close()

    # 4. Correlation Matrix
    numeric_cols = ['weekly_sales', 'size_sqft', 'temperature', 'fuel_price', 'cpi', 'unemployment', 'markdown_1', 'markdown_5', 'is_holiday']
    corr = df[numeric_cols].corr()

    plt.figure(figsize=(9, 7))
    plt.imshow(corr, cmap='coolwarm', interpolation='nearest', vmin=-1, vmax=1)
    plt.colorbar()
    plt.xticks(range(len(numeric_cols)), numeric_cols, rotation=45, ha='right', fontsize=9)
    plt.yticks(range(len(numeric_cols)), numeric_cols, fontsize=9)
    for i in range(len(numeric_cols)):
        for j in range(len(numeric_cols)):
            plt.text(j, i, f"{corr.iloc[i, j]:.2f}", ha='center', va='center', color='black' if abs(corr.iloc[i, j]) < 0.6 else 'white', fontsize=8)
    plt.title('Feature Correlation Matrix', fontsize=13, fontweight='bold', pad=12)
    plt.tight_layout()
    corr_path = os.path.join(FIGURES_DIR, "eda_correlation_matrix.png")
    plt.savefig(corr_path, dpi=200)
    plt.close()

    print(f"Saved EDA visualizations to {FIGURES_DIR}")
    return summary

if __name__ == "__main__":
    run_exploratory_data_analysis()
