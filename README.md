# 💊 Pharma Sales Analytics & Performance Dashboard

---

## 📘 Project Background

This is a personal data analytics project analyzing pharmaceutical sales data to generate actionable insights for sales management and product strategy.

The focus is on identifying performance drivers and optimizing product distribution across key geographic regions.

Key Performance Indicators (KPIs) tracked include:

* **Total Amount (USD)**
* **Total Boxes Shipped**
* **Total Transactions**
* **Average Sale Value (ASV)**

Insights and recommendations are provided across four main areas:

1.  **Sales Trends & Volume Analysis:** Evaluation of overall financial performance and transaction volume over time.
2.  **Product & Category Performance:** Identifying top-selling products, category contributions to revenue, and product mix.
3.  **Sales Person Performance:** Analyzing individual sales rep metrics (revenue, volume) and identifying top performers.
4.  **Geographic & Detail Analysis:** Deep dive into sales patterns filtered by specific sales reps, countries, and time periods.

🔗 **SQL ETL Script:**
**[View ETL & Analytics Script (etl\_pharma.sql)](Replace this link with your SQL file path)**

🐍 **Python ETL/Analysis Script:**
**[View Python ETL Script](Replace this link with your Python file path)**

📊 **Dashboard:**
**[Download Pharma Sales Dashboard.pbix](Replace this link with your PBIX file path)**

---

## 🧩 Data Structure & Initial Checks

The dashboard is built on consolidated and cleaned sales data. Key metrics across all regions show:

* **Total Amount:** $58.93K
* **Total Boxes Shipped:** 3K

The data is structured to support detailed analysis across products, sales personnel, and geography.

<p align="center">
  <img src="Images/pharma_erd.png" alt="Entity Relationship Diagram (ERD)">
</p>

---

## 📈 Executive Summary

### Overview of Findings

The company maintains a steady revenue stream of **$58.93K Total Amount** with an **Average Sale Value (ASV) of $177**. The market shows moderate growth volatility, with a peak in **August 2022**. Key findings include:

* **Top Performer:** **Rajesh Patel** leads all salespersons in total revenue.
* **Product Focus:** Digestive, Antiseptic, and Nasal Spray categories drive revenue by volume.
* **Transaction Volume:** The company completed **333 Total Transactions** across the period.

<p align="center">
  <img src="pharma.jpg" alt="Pharma Sales Overall Dashboard">
</p>

---

## 🔍 Insights Deep Dive

### **Category 1: Sales Trends & Volume Analysis**

* **Total Amount:** **$58.93K** from **333 Total Transactions**, confirming precise tracking of high-value transactions.
* **Sales Trends Over Time:** Consistent month-over-month sales, peaking in **August 2022 ($8.8K)** and lowest in **February 2022 ($7.3K)**.
* **Average Sale Value (ASV):** **$177**, indicating stable pricing and consistent basket size per transaction.

<p align="center">
  <img src="" alt="Sales Trend Chart">
</p>

### **Category 2: Product & Category Performance**

* Top revenue-generating products are **Digestive Enzyme, Antiseptic Cream, and Nasal Spray**.
* Sales Person **Priya Singh**'s detail view shows **Cough Syrup** as her top product ($1,626), followed by **Antiseptic Cream** ($1,540).
* When filtered by **Nikhil Batra**, **Cough Syrup** generates the highest total amount ($493), followed by **Nasal Spray** ($488).
* For **Priya Singh**, the largest categories by volume are **Cough Syrup (28%)** and **Antiseptic Cream (23%)**.

<p align="center">
  <img src="" alt="Product Sales by Category Chart">
</p>

### **Category 3: Sales Person Performance**

* **Rajesh Patel** is the top performer in Total Amount, followed by **Nikhil Batra** and **Priya Singh**.
* **Nikhil Batra**'s detail view shows he shipped **51** total boxes and sold **4** total products—key for commission tracking.
* **Priya Singh** has a personal ASV of **$169** with **54** total products sold and **558** boxes shipped, slightly below the company average of $177.

<p align="center">
  <img src="" alt="Top Sales Person Chart">
</p>

### **Category 4: Geographic & Detail Analysis**

* **Primary sales region:** **North America**, with most volume across the displayed regions.
* **Priya Singh**’s filtered sales trend peaks at **$1.79K in July 2022** and hits a low of **$377.24 in April 2022**.
* **Nikhil Batra in Canada** achieves an ASV of **$243**, significantly above the company average of $177, with a Total Amount of **$58.93K**.
* In the filtered view for **Nikhil Batra in Canada**, the sales trend jumps from **$478.18 (April 22)** to **$493.54 (May 22)**.

<p align="center">
  <img src="pharma3.jpg" alt="Detail View: Nikhil Batra Sales in Canada">
</p>

---

## 💡 Recommendations

1.  **Investigate Seasonal Peak:** Analyze factors behind **August 2022 peak ($8.8K)** to replicate success in other months.
2.  **Optimize Product Focus:** Shift marketing and inventory to **Digestive Enzyme, Antiseptic Cream, and Nasal Spray**, the top-performing products.
3.  **Target High-ASV Segments:** Examine Nikhil Batra’s **$243 ASV in Canada** to replicate success with other reps or products.
4.  **Sales Performance Coaching:** Develop coaching based on top performers like **Rajesh Patel** to uplift mid-to-low-tier salespersons.

---

## ⚙️ Assumptions & Caveats

* **Currency:** All figures are standardized in **USD**.
* **Time Filters:** Detail views use filters (Sales Person, Country, Date) and do not represent total company performance.
* **Geographic Data:** Sales by country map depends on accurate geo-coding.

<p align="center">
  <i>Created by Aïmane Benkhadda — Personal Data Analytics Project (Excel, SQL, Power BI, Python)</i>
  <br>
  <a href="mailto:aymanebenkhadda5959@gmail.com">aymanebenkhadda5959@gmail.com</a>
</p>
