import os
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from src.database import get_connection, init_schema

DATA_RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")

def generate_retail_dataset(num_stores: int = 10, num_depts: int = 12, start_year: int = 2024, weeks_count: int = 130):
    np.random.seed(42)
    os.makedirs(DATA_RAW_DIR, exist_ok=True)

    print(f"==> Generating synthetic retail dataset ({num_stores} stores, {num_depts} depts, {weeks_count} weeks)...")

    # 1. Stores Metadata
    store_types = ['A', 'B', 'C']
    regions = ['North', 'South', 'East', 'West', 'Central']
    stores_data = []
    for s_id in range(1, num_stores + 1):
        stype = store_types[(s_id - 1) % 3]
        size = 180000 if stype == 'A' else (120000 if stype == 'B' else 60000)
        size += int(np.random.normal(0, 5000))
        region = regions[(s_id - 1) % len(regions)]
        stores_data.append({
            'store_id': s_id,
            'store_type': stype,
            'size_sqft': size,
            'region': region
        })
    df_stores = pd.DataFrame(stores_data)
    df_stores.to_csv(os.path.join(DATA_RAW_DIR, "stores.csv"), index=False)

    # 2. Economic Features by Date
    start_date = datetime(start_year, 1, 5) # First Friday of 2024
    dates = [start_date + timedelta(weeks=w) for w in range(weeks_count)]
    
    features_data = []
    cpi_base = 210.0
    unemployment_base = 7.2

    # Standard holiday weeks: Super Bowl (~Wk 6), Labor Day (~Wk 36), Thanksgiving (~Wk 47), Christmas (~Wk 51)
    holiday_weeks = {6, 36, 47, 51}

    for idx, d in enumerate(dates):
        week_num = d.isocalendar()[1]
        is_holiday = 1 if week_num in holiday_weeks else 0
        
        # Seasonality for temperature
        temp = 60 + 25 * np.sin(2 * np.pi * (week_num - 15) / 52) + np.random.normal(0, 5)
        fuel = 3.20 + 0.5 * np.sin(2 * np.pi * week_num / 52) + (idx * 0.005) + np.random.normal(0, 0.05)
        
        # Markdowns are higher near holidays
        md_factor = 2.5 if is_holiday else 0.8
        md1 = max(0.0, np.random.exponential(1500 * md_factor))
        md2 = max(0.0, np.random.exponential(800 * md_factor))
        md3 = max(0.0, np.random.exponential(600 * md_factor))
        md4 = max(0.0, np.random.exponential(1200 * md_factor))
        md5 = max(0.0, np.random.exponential(2000 * md_factor))
        
        cpi = cpi_base + (idx * 0.12) + np.random.normal(0, 0.1)
        unemp = max(4.0, unemployment_base - (idx * 0.02) + np.random.normal(0, 0.05))

        features_data.append({
            'date': d.strftime('%Y-%m-%d'),
            'temperature': round(temp, 1),
            'fuel_price': round(fuel, 3),
            'markdown_1': round(md1, 2),
            'markdown_2': round(md2, 2),
            'markdown_3': round(md3, 2),
            'markdown_4': round(md4, 2),
            'markdown_5': round(md5, 2),
            'cpi': round(cpi, 3),
            'unemployment': round(unemp, 2),
            'is_holiday': is_holiday
        })
    df_features = pd.DataFrame(features_data)
    df_features.to_csv(os.path.join(DATA_RAW_DIR, "features.csv"), index=False)

    # 3. Weekly Sales
    sales_data = []
    for s_meta in stores_data:
        s_id = s_meta['store_id']
        stype = s_meta['store_type']
        type_multiplier = 1.4 if stype == 'A' else (1.0 if stype == 'B' else 0.65)
        
        for dept_id in range(1, num_depts + 1):
            dept_base = 12000 + (dept_id * 1400)
            
            for f_meta in features_data:
                d_str = f_meta['date']
                d_obj = datetime.strptime(d_str, '%Y-%m-%d')
                w_num = d_obj.isocalendar()[1]
                is_hol = f_meta['is_holiday']

                # Seasonal curve (surges in Q4)
                seasonal_boost = 1.0 + 0.25 * np.cos(2 * np.pi * (w_num - 50) / 52)
                holiday_boost = 1.55 if is_hol else 1.0
                markdown_boost = 1.0 + ((f_meta['markdown_1'] + f_meta['markdown_5']) / 30000.0)
                
                noise = np.random.normal(1.0, 0.08)
                weekly_rev = dept_base * type_multiplier * seasonal_boost * holiday_boost * markdown_boost * noise
                weekly_rev = max(500.0, weekly_rev)

                sales_data.append({
                    'store_id': s_id,
                    'dept_id': dept_id,
                    'date': d_str,
                    'weekly_sales': round(weekly_rev, 2),
                    'is_holiday': is_hol
                })
    df_sales = pd.DataFrame(sales_data)
    df_sales.to_csv(os.path.join(DATA_RAW_DIR, "sales.csv"), index=False)

    # 4. Populate SQLite Relational Database
    init_schema()
    conn = get_connection()
    df_stores.to_sql('stores', conn, if_exists='append', index=False)
    df_features.to_sql('economic_features', conn, if_exists='append', index=False)
    df_sales.to_sql('weekly_sales', conn, if_exists='append', index=False)
    conn.commit()
    conn.close()

    print(f"Created {len(df_stores)} stores, {len(df_features)} feature weeks, {len(df_sales)} weekly sales records in SQLite.")

if __name__ == "__main__":
    generate_retail_dataset()
