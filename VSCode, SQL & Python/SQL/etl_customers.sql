/* =========================================================
   🚀 PROJECT: SMART BUDGET — SALES ANALYTICS PIPELINE
   DATABASE: db
   AUTHOR: Aïmane Benkhadda
   DATE: 2025-10-21
   PURPOSE:
     Unified SQL pipeline for sales dataset.
     Produces clean, analytics-ready views for Power BI & Python.
   ========================================================= */


/* =========================================================
   1️⃣ CREATE DATABASE & MAIN TABLE
   ========================================================= */
CREATE DATABASE db;

-- Connect to the database before creating tables:
-- \c db

-- Drop and recreate main table (from CSV import)
DROP TABLE IF EXISTS sales_data;

CREATE TABLE sales_data (
    sale_id         SERIAL PRIMARY KEY,
    sale_date       DATE,
    product         VARCHAR,
    sales_person    VARCHAR,
    boxes_shipped   INT,
    amount_usd      NUMERIC,
    country         VARCHAR
);

-- ✅ Load CSV (adjust local path)
COPY sales_data (sale_date, product, sales_person, boxes_shipped, amount_usd, country)
FROM 'C:\Users\ayman\OneDrive\Desktop\Second Project\VSCode, SQL & Python\CSV\pharmacy_otc_sales_data.csv'
DELIMITER ',' CSV HEADER;


/* =========================================================
   2️⃣ CLEANING — CREATE CLEAN BASE VIEW
   ========================================================= */
CREATE OR REPLACE VIEW sales_data_clean AS
SELECT
    sale_id,
    sale_date,
    INITCAP(TRIM(product)) AS product,
    INITCAP(TRIM(sales_person)) AS sales_person,
    COALESCE(boxes_shipped, 0) AS boxes_shipped,
    COALESCE(amount_usd, 0) AS amount_usd,
    INITCAP(TRIM(country)) AS country,

    -- 🧮 Derived metrics
    DATE_PART('year', sale_date) AS year,
    DATE_PART('month', sale_date) AS month,
    TO_CHAR(sale_date, 'Mon YYYY') AS month_label,

    CASE
        WHEN amount_usd >= 1000 THEN 'High Value'
        WHEN amount_usd BETWEEN 500 AND 999 THEN 'Medium Value'
        WHEN amount_usd BETWEEN 100 AND 499 THEN 'Low Value'
        ELSE 'Small Value'
    END AS deal_size_category

FROM sales_data
WHERE
    sale_date IS NOT NULL
    AND amount_usd IS NOT NULL
    AND country IS NOT NULL;


/* =========================================================
   3️⃣ SUMMARY VIEWS FOR POWER BI / PYTHON
   ========================================================= */

-- 🌍 Total Sales by Country
CREATE OR REPLACE VIEW summary_sales_country AS
SELECT 
    country,
    SUM(amount_usd) AS total_sales,
    COUNT(*) AS total_transactions
FROM sales_data_clean
GROUP BY country
ORDER BY total_sales DESC;


-- 👤 Total Sales by Sales Person
CREATE OR REPLACE VIEW summary_sales_person AS
SELECT 
    sales_person,
    SUM(amount_usd) AS total_sales,
    SUM(boxes_shipped) AS total_boxes,
    COUNT(*) AS total_orders
FROM sales_data_clean
GROUP BY sales_person
ORDER BY total_sales DESC;


-- 📦 Product Performance
CREATE OR REPLACE VIEW summary_product_sales AS
SELECT
    product,
    COUNT(*) AS total_orders,
    SUM(boxes_shipped) AS total_boxes,
    SUM(amount_usd) AS total_sales
FROM sales_data_clean
GROUP BY product
ORDER BY total_sales DESC;


-- 👑 Top 10 Sales Persons by Revenue
CREATE OR REPLACE VIEW summary_top_salespersons AS
SELECT
    sales_person,
    SUM(amount_usd) AS total_sales,
    SUM(boxes_shipped) AS total_boxes
FROM sales_data_clean
GROUP BY sales_person
ORDER BY total_sales DESC
LIMIT 10;


-- 📅 Monthly Sales Trend
CREATE OR REPLACE VIEW vw_monthly_sales AS
SELECT
    year,
    month,
    month_label,
    SUM(amount_usd) AS total_sales
FROM sales_data_clean
GROUP BY year, month, month_label
ORDER BY year, month;


-- 💰 Deal Size Distribution
CREATE OR REPLACE VIEW summary_deal_size AS
SELECT
    deal_size_category,
    COUNT(sale_id) AS total_orders,
    SUM(amount_usd) AS total_sales
FROM sales_data_clean
GROUP BY deal_size_category
ORDER BY total_sales DESC;


-- 🧾 Revenue by Product & Country (for heatmaps)
CREATE OR REPLACE VIEW vw_sales_product_country AS
SELECT
    product,
    country,
    SUM(amount_usd) AS total_sales
FROM sales_data_clean
GROUP BY product, country
ORDER BY total_sales DESC;


-- 🧹 Data Quality Summary
CREATE OR REPLACE VIEW vw_null_summary AS
SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE product IS NULL) AS missing_product,
    COUNT(*) FILTER (WHERE sales_person IS NULL) AS missing_sales_person,
    COUNT(*) FILTER (WHERE country IS NULL) AS missing_country,
    COUNT(*) FILTER (WHERE amount_usd IS NULL OR amount_usd = 0) AS missing_amount,
    COUNT(*) FILTER (WHERE boxes_shipped IS NULL) AS missing_boxes
FROM sales_data;


/* =========================================================
   4️⃣ EXPORT VIEW — For Power BI / Python Connection
   ========================================================= */
CREATE OR REPLACE VIEW vw_sales_export AS
SELECT * FROM sales_data_clean;


/* =========================================================
   ✅ END OF PIPELINE — CLEAN, SCALABLE & DASHBOARD-READY
   ========================================================= */
