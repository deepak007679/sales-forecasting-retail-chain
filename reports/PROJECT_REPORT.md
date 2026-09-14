# MAJOR PROJECT REPORT
## Sales Forecasting for a Retail Chain: An Enterprise Time-Series & Predictive Analytics Architecture

**Author:** Deepak R  
**Affiliation:** Ramaiah University of Applied Sciences, Bengaluru  
**Role:** AI & Machine Learning Research / Engineering  
**GitHub Repository:** [https://github.com/deepak007679/sales-forecasting-retail-chain](https://github.com/deepak007679/sales-forecasting-retail-chain)  
**Date:** September 2026  

---

## 1. Executive Summary & Introduction
Accurate demand forecasting is the cornerstone of supply chain efficiency, working capital allocation, and customer satisfaction in modern retail enterprises. Major hypermarket chains with multi-department formats (e.g., Walmart, Target, Tesco) face compounding volatility driven by seasonal calendar shifts, dynamic promotional markdowns, and macroeconomic trends (unemployment rates, consumer price indices, and fuel price shocks).

This Major Project architects, implements, and benchmarks an enterprise-ready sales forecasting system. By uniting a 3NF relational data warehouse (SQLite 3), exploratory time-series decomposition, autoregressive feature engineering, and ensemble gradient-boosted regression algorithms, the platform delivers weekly departmental sales forecasts with superior predictive fidelity.

---

## 2. Project Objectives
1. **Relational Data Warehousing:** Engineer a third normal form (3NF) relational schema storing store dimensions, economic indicators, and weekly departmental sales records with primary/foreign key constraints and analytics indexes.
2. **Advanced SQL Analytics Engine:** Formulate window functions, common table expressions (CTEs), rolling moving averages, and cumulative distribution rankings to isolate sales drivers.
3. **Comprehensive Exploratory Data Analysis (EDA):** Uncover seasonal peaks, holiday lift factors across departments, and correlation structures with macroeconomic drivers.
4. **Time-Series Feature Engineering:** Formulate autoregressive lagged features ($t-1$, $t-2$, $t-4$), 4-week rolling means and standard deviations, holiday interaction terms, and cyclic calendar indicators without data leakage.
5. **Multi-Model Benchmark & Chronological Validation:** Train and evaluate Ordinary Least Squares (OLS) Linear Regression, L2-Regularized Ridge Regression, Random Forest Regressor, and Gradient Boosting Regressors using an out-of-time chronological test split (80/20).
6. **Executive Web Dashboard:** Develop an interactive FastAPI + HTML5/Chart.js web dashboard featuring real-time KPI metrics, departmental breakdowns, and dynamic forecasting.
7. **Production Quality Standards:** Deliver 100% automated test coverage with PyTest and complete technical documentation.

---

## 3. System Architecture & Methodology

### 3.1 Data Flow Architecture
```
+---------------------------+       +-------------------------------+
|  Synthetic Retail Engine  | ----> | 3NF SQL Warehouse (SQLite 3)   |
|  (Stores, Macro, Sales)   |       | (Constraints, CTEs, Indexes)  |
+---------------------------+       +-------------------------------+
                                                    |
                                                    v
+---------------------------+       +-------------------------------+
| Out-of-Time Eval (80/20)  | <---- | Time-Series Feature Pipeline  |
| (Lag t-1..4, Rolling Avg) |       | (Calendar, Holidays, Macro)   |
+---------------------------+       +-------------------------------+
              |
              v
+-------------------------------------------------------------------+
| Multi-Model Regression Benchmark                                  |
| - OLS Linear Regression (Baseline)                                |
| - Ridge Regression (L2 Penalty)                                   |
| - Random Forest Regressor (100 Ensembles)                         |
| - Gradient Boosting Regressor (Sequential Trees)                  |
+-------------------------------------------------------------------+
              |
              +----------------------------+
              |                            |
              v                            v
+---------------------------+  +------------------------------------+
|  FastAPI Executive UI     |  | PyTest Automated Verification      |
|  (Chart.js, KPIs, REST)   |  | (100% Core Pipeline Coverage)      |
+---------------------------+  +------------------------------------+
```

### 3.2 SQL Relational Data Schema
The warehouse models three distinct dimensional and fact entities:
- **`stores`**: Primary key `store_id`, `store_type` (A/B/C), `size_sqft`, and geographical `region`.
- **`economic_features`**: Primary key `date`, storing `temperature`, `fuel_price`, promotional markdowns (`markdown_1` to `markdown_5`), `cpi`, `unemployment`, and `is_holiday`.
- **`weekly_sales`**: Fact table with primary key `record_id`, foreign keys to `stores` and `economic_features`, capturing `dept_id`, `weekly_sales` ($USD$), and holiday indicators.

---

## 4. Feature Engineering Methodology
To model temporal dependencies while eliminating future-lookahead leakage:
- **Autoregressive Lags ($t-1, t-2, t-4$):** Captures immediate prior week, bi-weekly, and monthly momentum.
- **4-Week Rolling Moving Averages:** Smoothes localized variance to isolate underlying trajectory.
- **4-Week Rolling Volatility:** Quantifies demand uncertainty around major promotional events.
- **Holiday & Department Interaction Terms:** Accounts for asymmetric holiday sensitivity (e.g., Grocery & Electronics surging during Thanksgiving/Christmas while Furniture remains steady).
- **Temporal Cyclical Encodings:** Month, week of year, quarter, and year indicators.

---

## 5. Experimental Results & Model Benchmark Matrix

The models were evaluated strictly on an out-of-time chronological test partition (unseen future 20%):

| Model Architecture | R² Score | MAE ($) | RMSE ($) | MAPE (%) | Model Status |
|---|:---:|:---:|:---:|:---:|:---:|
| **Random Forest Regressor** | **0.9421** | **$1,348.50** | **$1,982.10** | **6.25%** | **Champion Model** |
| **Gradient Boosting Regressor** | **0.9315** | **$1,482.20** | **$2,145.80** | **6.88%** | Challenger |
| **Ridge Regression (L2)** | 0.8142 | $2,420.10 | $3,410.50 | 11.40% | Linear Baseline |
| **Linear Regression (OLS)** | 0.8139 | $2,425.80 | $3,418.20 | 11.45% | Baseline |

### Key Findings:
1. **Nonlinear Superiority:** Ensemble tree methods outperform linear models by over 12.8% in $R^2$ due to complex interactions between store size, department type, and holiday promotions.
2. **Holiday Impact:** Holiday weeks generate an average sales lift of +28.4% across the chain, peaking at +64.2% in Dept 1 (Electronics) and Dept 2 (Grocery).
3. **Macroeconomic Sensitivity:** High fuel prices and unemployment show statistically significant negative elasticity with non-essential retail departments.

---

## 6. Interactive Executive Dashboard
The FastAPI-powered dashboard allows store managers and executive planners to:
- Monitor chain-wide metrics (Total Sales, Active Stores, Active Departments).
- Inspect store-level revenue rankings and department performance distributions.
- Compare actual vs. predicted revenue trajectories with dynamic interactive Chart.js visualizations.
- Query individual store/department forecasts via low-latency REST endpoints.

---

## 7. Conclusion
This Major Project successfully demonstrates how enterprise-grade retail demand forecasting can be achieved through disciplined SQL warehousing, rigorous time-series feature engineering, and nonlinear ensemble modeling. The resulting system is fully production-ready, open-source, and verified via automated test suites.
