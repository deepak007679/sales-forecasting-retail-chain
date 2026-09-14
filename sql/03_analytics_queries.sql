-- ====================================================================
-- PROJECT: Sales Forecasting for a Retail Chain
-- FILE: sql/03_analytics_queries.sql
-- PURPOSE: Advanced SQL Analytics for Retail Operations & Revenue Intelligence
-- ====================================================================

-- 1. Store-Level Total Revenue & Size Productivity Ranking
SELECT 
    s.store_id,
    s.store_type,
    s.size_sqft,
    s.region,
    COUNT(w.record_id) AS total_weekly_records,
    ROUND(SUM(w.weekly_sales), 2) AS total_revenue,
    ROUND(AVG(w.weekly_sales), 2) AS avg_weekly_sales,
    ROUND(SUM(w.weekly_sales) / s.size_sqft, 2) AS revenue_per_sqft
FROM stores s
JOIN weekly_sales w ON s.store_id = w.store_id
GROUP BY s.store_id, s.store_type, s.size_sqft, s.region
ORDER BY total_revenue DESC;

-- 2. Holiday vs Non-Holiday Sales Surge Factor
SELECT 
    w.is_holiday,
    CASE WHEN w.is_holiday = 1 THEN 'Holiday Week (Surge)' ELSE 'Regular Week' END AS week_category,
    COUNT(w.record_id) AS total_observations,
    ROUND(AVG(w.weekly_sales), 2) AS mean_weekly_sales,
    ROUND(MIN(w.weekly_sales), 2) AS min_sales,
    ROUND(MAX(w.weekly_sales), 2) AS peak_sales,
    ROUND(
        (AVG(w.weekly_sales) - (SELECT AVG(weekly_sales) FROM weekly_sales WHERE is_holiday = 0)) 
        / (SELECT AVG(weekly_sales) FROM weekly_sales WHERE is_holiday = 0) * 100.0, 
        2
    ) AS holiday_lift_percentage
FROM weekly_sales w
GROUP BY w.is_holiday;

-- 3. Top 5 Revenue-Driving Departments Across Chain
SELECT 
    w.dept_id,
    COUNT(DISTINCT w.store_id) AS store_presence_count,
    ROUND(SUM(w.weekly_sales), 2) AS aggregate_department_sales,
    ROUND(AVG(w.weekly_sales), 2) AS average_department_sales,
    ROUND((SUM(w.weekly_sales) * 100.0) / (SELECT SUM(weekly_sales) FROM weekly_sales), 2) AS revenue_contribution_pct
FROM weekly_sales w
GROUP BY w.dept_id
ORDER BY aggregate_department_sales DESC
LIMIT 5;

-- 4. 4-Week Rolling Sales Moving Average using Window Functions
SELECT 
    w.store_id,
    w.date,
    w.weekly_sales,
    ROUND(AVG(w.weekly_sales) OVER (
        PARTITION BY w.store_id, w.dept_id 
        ORDER BY w.date 
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ), 2) AS rolling_4w_avg_sales
FROM weekly_sales w
WHERE w.store_id = 1 AND w.dept_id = 1
ORDER BY w.date;

-- 5. Economic Correlation: Sales during High vs Low Unemployment Periods
SELECT 
    CASE 
        WHEN ef.unemployment >= 8.0 THEN 'High Unemployment (>=8%)'
        WHEN ef.unemployment >= 6.0 THEN 'Moderate Unemployment (6-8%)'
        ELSE 'Low Unemployment (<6%)'
    END AS economic_tier,
    COUNT(w.record_id) AS total_weeks_recorded,
    ROUND(AVG(w.weekly_sales), 2) AS average_sales,
    ROUND(AVG(ef.fuel_price), 2) AS mean_fuel_price,
    ROUND(AVG(ef.cpi), 2) AS mean_cpi
FROM weekly_sales w
JOIN economic_features ef ON w.date = ef.date
GROUP BY economic_tier
ORDER BY average_sales DESC;
