-- ====================================================================
-- PROJECT: Sales Forecasting for a Retail Chain (Major Project)
-- FILE: sql/01_schema.sql
-- PURPOSE: Relational DDL for retail data warehouse schema.
-- AUTHOR: Deepak R
-- ====================================================================

DROP TABLE IF EXISTS weekly_sales;
DROP TABLE IF EXISTS economic_features;
DROP TABLE IF EXISTS stores;

-- 1. Stores Dimension Table
CREATE TABLE stores (
    store_id INTEGER PRIMARY KEY,
    store_type VARCHAR(10) NOT NULL CHECK(store_type IN ('A', 'B', 'C')),
    size_sqft INTEGER NOT NULL CHECK(size_sqft > 0),
    region VARCHAR(50) NOT NULL
);

-- 2. Economic & Environmental Features Table
CREATE TABLE economic_features (
    date DATE NOT NULL,
    temperature REAL NOT NULL,
    fuel_price REAL NOT NULL,
    markdown_1 REAL DEFAULT 0.0,
    markdown_2 REAL DEFAULT 0.0,
    markdown_3 REAL DEFAULT 0.0,
    markdown_4 REAL DEFAULT 0.0,
    markdown_5 REAL DEFAULT 0.0,
    cpi REAL NOT NULL,
    unemployment REAL NOT NULL,
    is_holiday INTEGER DEFAULT 0 CHECK(is_holiday IN (0, 1)),
    PRIMARY KEY (date)
);

-- 3. Weekly Sales Fact Table
CREATE TABLE weekly_sales (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    store_id INTEGER NOT NULL,
    dept_id INTEGER NOT NULL,
    date DATE NOT NULL,
    weekly_sales REAL NOT NULL CHECK(weekly_sales >= 0),
    is_holiday INTEGER DEFAULT 0 CHECK(is_holiday IN (0, 1)),
    FOREIGN KEY (store_id) REFERENCES stores(store_id) ON DELETE CASCADE,
    FOREIGN KEY (date) REFERENCES economic_features(date) ON DELETE CASCADE,
    UNIQUE(store_id, dept_id, date)
);

-- Indices for rapid analytical aggregations
CREATE INDEX idx_sales_store_date ON weekly_sales(store_id, date);
CREATE INDEX idx_sales_dept ON weekly_sales(dept_id);
CREATE INDEX idx_sales_holiday ON weekly_sales(is_holiday);
