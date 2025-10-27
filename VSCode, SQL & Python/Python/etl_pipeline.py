#!/usr/bin/env python3
"""
ETL pipeline for 'sales_data' dataset connected to PostgreSQL.
Compatible with the 'Smart Budget — Sales Analytics Pipeline' SQL script.
Creates clean CSV exports ready for Power BI & Excel visualization.
"""

import os
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
from dotenv import load_dotenv

# ============================================================
# 1️⃣ ENVIRONMENT SETUP
# ============================================================
load_dotenv()

PG_USER = os.getenv("PG_USER", "postgres")
PG_PASS = os.getenv("PG_PASS", "Aymaneb595.")
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB   = os.getenv("PG_DB", "smart_budget")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./outputs")

# Create outputs folder if it doesn’t exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# 2️⃣ DATABASE CONNECTION
# ============================================================
def get_engine():
    print("🔗 Connecting to PostgreSQL database...")
    conn_str = f"postgresql+psycopg2://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"
    engine = create_engine(conn_str)
    print("✅ Connection successful.")
    return engine

# ============================================================
# 3️⃣ VIEW LOADER
# ============================================================
def load_view(engine, view_name):
    print(f"📥 Loading view: {view_name}")
    df = pd.read_sql(f"SELECT * FROM {view_name};", engine)
    print(f"   → Loaded {len(df):,} rows.")
    return df

# ============================================================
# 4️⃣ CSV EXPORT FUNCTION
# ============================================================
def export_csv(df, name):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(OUTPUT_DIR, f"{name}_{ts}.csv")
    df.to_csv(path, index=False)
    print(f"💾 Exported: {path}")
    return path

# ============================================================
# 5️⃣ KPI GENERATION
# ============================================================
def compute_kpis(sales_df, top_sales_df, monthly_df):
    """Compute key performance indicators for Power BI / Excel."""
    if sales_df.empty:
        print("⚠️ No data in vw_sales_export — skipping KPI computation.")
        return pd.DataFrame()

    total_revenue = sales_df["amount_usd"].sum()
    total_orders = len(sales_df)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    avg_revenue_per_product = sales_df.groupby("product")["amount_usd"].sum().mean()

    # Top salesperson info
    top_salesperson = (
        top_sales_df.iloc[0]["sales_person"]
        if not top_sales_df.empty else "N/A"
    )
    top_salesperson_revenue = (
        top_sales_df.iloc[0]["total_sales"]
        if not top_sales_df.empty else 0
    )

    # Monthly growth
    if not monthly_df.empty:
        current_month_revenue = monthly_df.iloc[-1]["total_sales"]
        previous_month_revenue = (
            monthly_df.iloc[-2]["total_sales"] if len(monthly_df) > 1 else current_month_revenue
        )
        monthly_growth = (
            ((current_month_revenue - previous_month_revenue) / previous_month_revenue * 100)
            if previous_month_revenue != 0 else 0
        )
    else:
        monthly_growth = 0

    kpis = {
        "total_revenue": [round(total_revenue, 2)],
        "total_orders": [total_orders],
        "avg_order_value": [round(avg_order_value, 2)],
        "avg_revenue_per_product": [round(avg_revenue_per_product, 2)],
        "top_salesperson": [top_salesperson],
        "top_salesperson_revenue": [round(top_salesperson_revenue, 2)],
        "monthly_growth_%": [round(monthly_growth, 2)]
    }

    return pd.DataFrame(kpis)

# ============================================================
# 6️⃣ PIPELINE RUNNER
# ============================================================
def run_pipeline():
    engine = get_engine()

    # Views (matching your SQL pipeline)
    views = {
        "vw_sales_export": "sales_export",
        "summary_sales_country": "sales_by_country",
        "summary_sales_person": "sales_by_salesperson",
        "summary_product_sales": "sales_by_product",
        "summary_deal_size": "deal_size",
        "vw_monthly_sales": "monthly_sales",
        "vw_null_summary": "data_quality"
    }

    dataframes = {}
    for view_name, label in views.items():
        try:
            dataframes[label] = load_view(engine, view_name)
        except Exception as e:
            print(f"⚠️ Skipping {view_name} — {e}")

    print("\n📊 Exporting CSV files...")
    for label, df in dataframes.items():
        export_csv(df, label)

    print("\n📈 Generating KPI summary...")
    kpis_df = compute_kpis(
        sales_df=dataframes.get("sales_export", pd.DataFrame()),
        top_sales_df=dataframes.get("sales_by_salesperson", pd.DataFrame()),
        monthly_df=dataframes.get("monthly_sales", pd.DataFrame())
    )
    if not kpis_df.empty:
        export_csv(kpis_df, "kpi_summary")

    print("\n✅ ETL pipeline completed successfully.")
    print("📁 All outputs saved in:", os.path.abspath(OUTPUT_DIR))

# ============================================================
# 7️⃣ MAIN EXECUTION
# ============================================================
if __name__ == "__main__":
    run_pipeline()
