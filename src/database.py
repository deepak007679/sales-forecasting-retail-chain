import os
import sqlite3
import pandas as pd
from typing import List, Tuple, Any

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "retail_sales.db")
SQL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sql")

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_schema(db_path: str = DB_PATH):
    schema_path = os.path.join(SQL_DIR, "01_schema.sql")
    with get_connection(db_path) as conn:
        with open(schema_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
    print("Database schema initialized.")

def execute_query(query: str, params: Tuple[Any, ...] = (), db_path: str = DB_PATH) -> List[sqlite3.Row]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

def load_analytical_dataframe(db_path: str = DB_PATH) -> pd.DataFrame:
    sql = """
    SELECT 
        w.record_id,
        w.store_id,
        w.dept_id,
        w.date,
        w.weekly_sales,
        w.is_holiday,
        s.store_type,
        s.size_sqft,
        s.region,
        ef.temperature,
        ef.fuel_price,
        ef.markdown_1,
        ef.markdown_2,
        ef.markdown_3,
        ef.markdown_4,
        ef.markdown_5,
        ef.cpi,
        ef.unemployment
    FROM weekly_sales w
    JOIN stores s ON w.store_id = s.store_id
    JOIN economic_features ef ON w.date = ef.date
    ORDER BY w.store_id, w.dept_id, w.date;
    """
    with get_connection(db_path) as conn:
        df = pd.read_sql_query(sql, conn)
    df['date'] = pd.to_datetime(df['date'])
    return df
