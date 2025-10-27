#!/usr/bin/env python3
"""
🚀 PROJECT: SMART BUDGET — PHARMA SALES ETL PIPELINE
AUTHOR: Aïmane Benkhadda
DATE: 2025-10-27
PURPOSE:
Automated ETL pipeline for pharma OTC sales data.
Loads clean data from PostgreSQL, computes KPIs, and exports CSVs for dashboards (Power BI / Excel).
"""

# ============================================================
# 0️⃣ IMPORTS & TOOLS
# ============================================================
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# ============================================================
# 1️⃣ LOGGING SETUP
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("pharma_etl_pipeline")

# ============================================================
# 2️⃣ ENVIRONMENT SETUP
# ============================================================
load_dotenv()  # Securely loads credentials from .env

PG_USER = os.getenv("PG_USER")
PG_PASS = os.getenv("PG_PASS")
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB   = os.getenv("PG_DB", "smart_budget")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./outputs")

# Ensure output folder exists
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# Validate credentials
if not PG_USER or not PG_PASS:
    log.error("PG_USER and PG_PASS must be set in .env file.")
    raise SystemExit(1)

# ============================================================
# 3️⃣ DATABASE CONNECTION
# ============================================================
def get_engine():
    """Create a secure PostgreSQL connection engine."""
    conn_str = f"postgresql+psycopg2://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"
    log.info("🔗 Connecting to PostgreSQL...")
    engine = create_engine(conn_str, pool_pre_ping=True)
    log.info("✅ DB engine created.")
    return engine

# ============================================================
# 4️⃣ LOAD VIEW HELPER
# ============================================================
def load_view(engine, view_name):
    """Fetch a view from PostgreSQL and return as a Pandas DataFrame."""
    log.info(f"📥 Loading view: {view_name}")
    try:
        df = pd.read_sql_table(view_name, con=engine, schema="public")
        log.info(f"   → Loaded {len(df):,} rows.")
        return df
    except Exception as e:
        log.warning(f"Failed to load {view_name} via read_sql_table: {e}, trying SELECT * ...")
        df = pd.read_sql(text(f"SELECT * FROM {view_name};"), con=engine)
        log.info(f"   → Loaded {len(df):,} rows via SELECT.")
        return df

# ============================================================
# 5️⃣ CSV EXPORT HELPER
# ============================================================
def export_csv(df: pd.DataFrame, name: str) -> str:
    """Export a DataFrame to a timestamped CSV file."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(OUTPUT_DIR, f"{name}_{ts}.csv")
    df.to_csv(path, index=False)
    log.info(f"💾 Exported: {path}")
    return path

# ============================================================
# 6️⃣ KPI CALCULATIONS
# ============================================================
def compute_kpis(sales_df: pd.DataFrame, top_sales_df: pd.DataFrame, monthly_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute key performance indicators for pharma sales:
    - Total revenue
    - Total orders
    - Average order value (AOV)
    - Avg revenue per product
    - Top salesperson
    - Monthly revenue growth %
    """
    if sales_df.empty:
        log.warning("⚠️ vw_sales_export is empty — skipping KPI computation.")
        return pd.DataFrame()

    # Total revenue and orders
    total_revenue = float(sales_df["amount_usd"].sum())
    total_orders = int(len(sales_df))
    avg_order_value = float(total_revenue / total_orders) if total_orders > 0 else 0

    # Avg revenue per product
    avg_revenue_per_product = float(sales_df.groupby("product")["amount_usd"].sum().mean())

    # Top salesperson info
    top_salesperson = top_sales_df.iloc[0]["sales_person"] if not top_sales_df.empty else "N/A"
    top_salesperson_revenue = float(top_sales_df.iloc[0]["total_sales"]) if not top_sales_df.empty else 0

    # Monthly growth %
    monthly_growth_pct = 0.0
    if not monthly_df.empty:
        mdf = monthly_df.sort_values(["year", "month"])
        last = float(mdf.iloc[-1]["total_sales"])
        prev = float(mdf.iloc[-2]["total_sales"]) if len(mdf) > 1 else last
        if prev != 0:
            monthly_growth_pct = (last - prev) / prev * 100

    # Package KPIs
    kpis = {
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "avg_order_value": round(avg_order_value, 2),
        "avg_revenue_per_product": round(avg_revenue_per_product, 2),
        "top_salesperson": top_salesperson,
        "top_salesperson_revenue": round(top_salesperson_revenue, 2),
        "monthly_growth_pct": round(monthly_growth_pct, 2)
    }

    return pd.DataFrame([kpis])

# ============================================================
# 7️⃣ PIPELINE EXECUTION
# ============================================================
def run_pipeline():
    engine = get_engine()

    # Views in the SQL pipeline
    views = {
        "vw_sales_export": "sales_export",
        "summary_sales_country": "sales_by_country",
        "summary_sales_person": "sales_by_salesperson",
        "summary_product_sales": "sales_by_product",
        "summary_deal_size": "deal_size",
        "vw_monthly_sales": "monthly_sales",
        "vw_null_summary": "data_quality"
    }

    # Load all views
    dfs = {}
    for view_name, label in views.items():
        try:
            dfs[label] = load_view(engine, view_name)
        except Exception as e:
            log.warning(f"⚠️ Skipping {view_name}: {e}")
            dfs[label] = pd.DataFrame()

    # Export CSVs
    for label, df in dfs.items():
        export_csv(df, label)

    # Compute KPI summary
    kpi_df = compute_kpis(
        sales_df=dfs.get("sales_export", pd.DataFrame()),
        top_sales_df=dfs.get("sales_by_salesperson", pd.DataFrame()),
        monthly_df=dfs.get("monthly_sales", pd.DataFrame())
    )
    export_csv(kpi_df, "kpi_summary")

    log.info("✅ Pharma ETL pipeline completed. Outputs in: %s", os.path.abspath(OUTPUT_DIR))

# ============================================================
# 8️⃣ MAIN EXECUTION
# ============================================================
if __name__ == "__main__":
    run_pipeline()
