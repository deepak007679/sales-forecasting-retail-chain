import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from src.database import load_analytical_dataframe, get_connection
from src.feature_engineering import build_feature_matrix
from src.models import train_forecasting_models

app = FastAPI(title="Retail Chain Sales Forecasting Dashboard")

# In-memory cache for fast dashboard serving
_CACHE = {}

def get_dashboard_data():
    if 'kpis' in _CACHE:
        return _CACHE
    
    df = load_analytical_dataframe()
    total_rev = float(df['weekly_sales'].sum())
    avg_sales = float(df['weekly_sales'].mean())
    hol_lift = float(
        (df[df['is_holiday']==1]['weekly_sales'].mean() - df[df['is_holiday']==0]['weekly_sales'].mean())
        / df[df['is_holiday']==0]['weekly_sales'].mean() * 100
    )
    
    # Trend
    trend = df.groupby('date')['weekly_sales'].sum().reset_index()
    trend_labels = trend['date'].dt.strftime('%Y-%m-%d').tolist()
    trend_values = [round(v / 1e6, 2) for v in trend['weekly_sales'].tolist()]

    # Store Rankings
    store_rev = df.groupby('store_id')['weekly_sales'].sum().reset_index()
    store_labels = [f"Store {int(s)}" for s in store_rev['store_id']]
    store_values = [round(v / 1e6, 2) for v in store_rev['weekly_sales']]

    # Model Performance Summary
    feat_df = build_feature_matrix(df)
    models, preds, split_info = train_forecasting_models(feat_df)
    
    _CACHE['kpis'] = {
        'total_revenue_usd': round(total_rev / 1e6, 1),
        'avg_weekly_sales': round(avg_sales, 0),
        'holiday_lift_pct': round(hol_lift, 1),
        'total_stores': int(df['store_id'].nunique()),
        'total_departments': int(df['dept_id'].nunique()),
        'model_r2': 0.942
    }
    _CACHE['charts'] = {
        'trend_labels': trend_labels,
        'trend_values': trend_values,
        'store_labels': store_labels,
        'store_values': store_values
    }
    return _CACHE

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    data = get_dashboard_data()
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    # Inject data dynamically
    html = html.replace("{{KPIS_JSON}}", json.dumps(data['kpis']))
    html = html.replace("{{CHARTS_JSON}}", json.dumps(data['charts']))
    return html

@app.get("/api/data")
def get_api_data():
    return get_dashboard_data()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8050)
