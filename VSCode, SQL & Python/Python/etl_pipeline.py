"""Load the source CSV into PostgreSQL and export a consistent Power BI snapshot."""
import argparse
import csv
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import psycopg2
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = HERE.parent / "CSV" / "pharmacy_otc_sales_data.csv"
SQL = HERE.parent / "SQL" / "etl_customers.sql"
HEADERS = ["Date", "Product", "Sales Person", "Boxes Shipped", "Amount ($)", "Country"]
EXPORTS = {
    "sales_export": "vw_sales_export",
    "sales_by_country": "summary_sales_country",
    "sales_by_salesperson": "summary_sales_person",
    "sales_by_product": "summary_product_sales",
    "deal_size": "summary_deal_size",
    "monthly_sales": "vw_monthly_sales",
    "data_quality": "vw_null_summary",
}


def read_view(cursor, name):
    # Only static view names from EXPORTS are supplied here.
    cursor.execute(f"SELECT * FROM analytics.{name}")
    return pd.DataFrame.from_records(cursor.fetchall(), columns=[d.name for d in cursor.description])


def compute_kpis(sales_df, top_sales_df, monthly_df):
    if sales_df.empty:
        raise ValueError("The source contains no transactions.")
    revenue = sales_df["amount_usd"].sum()
    leader = top_sales_df.sort_values(["total_sales", "sales_person"], ascending=[False, True]).iloc[0]
    months = monthly_df.sort_values(["year", "month"])
    growth = None
    if len(months) >= 2:
        previous, latest = months.tail(2).to_dict("records")
        gap = (latest["year"] - previous["year"]) * 12 + latest["month"] - previous["month"]
        if gap == 1 and previous["total_sales"] != 0:
            growth = round(100 * (latest["total_sales"] / previous["total_sales"] - 1), 2)
    return pd.DataFrame([{
        "total_revenue": revenue,
        "total_orders": len(sales_df),
        "avg_order_value": round(revenue / len(sales_df), 2),
        "avg_revenue_per_product": round(revenue / sales_df["product"].nunique(), 2),
        "top_salesperson": leader["sales_person"],
        "top_salesperson_revenue": leader["total_sales"],
        "monthly_growth_pct": growth,
    }])


def import_sales(cursor, source):
    cursor.execute("""
        CREATE TEMP TABLE incoming (
            source_row integer GENERATED ALWAYS AS IDENTITY, sale_date date NOT NULL,
            product text NOT NULL CHECK (trim(product) <> ''),
            sales_person text NOT NULL CHECK (trim(sales_person) <> ''),
            boxes_shipped integer NOT NULL CHECK (boxes_shipped >= 0),
            amount_usd numeric NOT NULL CHECK (amount_usd >= 0 AND amount_usd <> 'NaN'),
            country text NOT NULL CHECK (trim(country) <> '')
        ) ON COMMIT DROP
    """)
    with source.open(encoding="utf-8-sig", newline="") as stream:
        if next(csv.reader(stream), None) != HEADERS:
            raise ValueError(f"Unexpected CSV header in {source}. Expected {HEADERS}.")
        cursor.copy_expert(
            "COPY incoming (sale_date, product, sales_person, boxes_shipped, amount_usd, country) "
            "FROM STDIN WITH (FORMAT CSV)", stream)
    cursor.execute("SELECT COUNT(*) FROM incoming")
    if not cursor.fetchone()[0]:
        raise ValueError("The input CSV is empty.")
    cursor.execute("TRUNCATE analytics.sales_data RESTART IDENTITY")
    cursor.execute("""
        INSERT INTO analytics.sales_data (sale_date, product, sales_person, boxes_shipped, amount_usd, country)
        SELECT sale_date, product, sales_person, boxes_shipped, amount_usd, country
        FROM incoming ORDER BY source_row
    """)


def run_pipeline(source=SOURCE, output_dir=None):
    load_dotenv(ROOT / ".env")
    output_dir = Path(output_dir or os.getenv("OUTPUT_DIR", HERE / "outputs"))
    output_dir.mkdir(parents=True, exist_ok=True)
    connection = psycopg2.connect(
        dbname=os.environ["PG_DB"], user=os.environ["PG_USER"],
        password=os.getenv("PG_PASS"), host=os.getenv("PG_HOST", "localhost"),
        port=os.getenv("PG_PORT", "5432"),
    )
    try:
        with connection, connection.cursor() as cursor:
            # Hold the session lock until the matching CSV is published as well.
            cursor.execute("SELECT pg_advisory_lock(hashtext('pharma-sales-etl'))")
            cursor.execute(SQL.read_text(encoding="utf-8-sig"))
            import_sales(cursor, Path(source))
            reports = {label: read_view(cursor, view) for label, view in EXPORTS.items()}
            reports["sales_export"] = reports["sales_export"].sort_values("sale_id")
            reports["kpi_summary"] = compute_kpis(reports["sales_export"], reports["sales_by_salesperson"], reports["monthly_sales"])
        publish_reports(reports, output_dir)
        return reports
    finally:
        connection.close()


def publish_reports(reports, output_dir):
    # Historical files keep the original naming convention. Power BI can point to one stable file.
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    with TemporaryDirectory(dir=output_dir) as scratch:
        staging = Path(scratch)
        for label, data in reports.items():
            data.to_csv(staging / f"{label}_{stamp}.csv", index=False)
        reports["sales_export"].to_csv(staging / "sales_current.csv", index=False)
        for label in reports:
            filename = f"{label}_{stamp}.csv"
            (staging / filename).replace(output_dir / filename)
        (staging / "sales_current.csv").replace(output_dir / "sales_current.csv")
    logging.info("Exported %s transactions to %s", len(reports["sales_export"]), output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    run_pipeline(args.source, args.output_dir)
