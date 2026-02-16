# 🛒 Retail ELT Orchestration (Airflow Edition)

**Version:** 2.0 (Self-Bootstrapping Infrastructure)
**Architecture:** Apache Airflow + Oracle XE + Docker
**Methodology:** ELT (Extract, Load, Transform) with Zero Data Loss

## 🚀 Overview

This project implements a robust **Retail Data Warehouse** pipeline orchestrated by **Apache Airflow**. Unlike traditional setups that require manual database preparation, this project features a **"Zero-Touch" Initialization** workflow.

A dedicated Airflow DAG automatically provisions the entire database infrastructure (Users, Directories, Tables, and PL/SQL Packages), making the project portable and easy to deploy on any machine with Docker.

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

* **Docker Desktop** (Running and configured)
* **Git** (To clone the repository)

---

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YourUsername/retail-elt-airflow.git
cd retail-elt-airflow

```

### 2. Prepare the Project Structure

Ensure your folders match the structure below. This is critical for Docker volume mapping.

```text
retail-elt-airflow/
├── dags/
│   ├── retail_init_dag.py       # [Run Once] Infrastructure Setup
│   └── retail_etl_dag.py        # [Daily] Main ELT Pipeline
├── scripts/
│   ├── generate_data.py         # Data Generator
│   └── sql_runner.py            # Universal SQL Executor (Renamed from data_truncate.py)
├── sql/
│   └── init_oracle/             # SQL Source Code (01 to 06)
├── docker-compose.yaml          # Infrastructure Config
└── Dockerfile                   # Custom Airflow Image

```

### 3. Build and Launch

Run the following command to build the custom Airflow image (with Oracle drivers) and start the services.

```bash
docker-compose up -d --build

```

*Wait about 2-3 minutes for the containers to fully start and for the Oracle Database to initialize.*

---

## 🤖 Usage Guide

This project is divided into **two phases** managed by separate Airflow DAGs.

### Phase 1: Infrastructure Initialization (Run Once)

**DAG ID:** `retail_project_init`

This DAG bootstraps the empty Oracle database. It dynamically switches credentials to perform Admin tasks (`SYSTEM`) and App tasks (`RETAIL_DW`).

1. Open the Airflow UI: [http://localhost:8080](https://www.google.com/search?q=http://localhost:8080) (User/Pass: `admin`/`admin`).
2. Find the **`retail_project_init`** DAG.
3. **Unpause** the DAG (Toggle the switch to blue).
4. Click the **Trigger DAG** (Play button) > **Trigger**.
5. **Verify:** Click on the DAG name and go to the "Graph" view. Ensure all tasks turn **Dark Green (Success)**.
* *Create User (System)*
* *Create Directory (App)*
* *Grant Access (System)*
* *Deploy Schema (App)*



### Phase 2: Daily ELT Run (Recurring)

**DAG ID:** `retail_etl_pipeline`

Once the infrastructure is ready, you can run the main data pipeline.

1. Find the **`retail_etl_pipeline`** DAG.
2. **Unpause** and **Trigger** it.
3. **What happens?**
* **Reset:** Truncates analysis tables to prevent duplicates.
* **Generate:** Creates a new `sales_data.csv` with 1000 rows (including 5% invalid data).
* **Load:** Triggers the PL/SQL package to Archive, Validate, and Load data into the Star Schema.



---

## 📊 Verification

You can verify the data load by connecting to the Oracle Database using any SQL Client (DBeaver, SQL Developer, Datagrip).

**Connection Details:**

* **Host:** `localhost`
* **Port:** `1521`
* **Service Name:** `xepdb1`
* **User:** `RETAIL_DW`
* **Password:** `RetailPass123`

**Validation Queries:**

```sql
-- 1. Check Valid Sales (The Star Schema)
SELECT * FROM FACT_SALES;
SELECT * FROM DIM_CUSTOMER;

-- 2. Check Rejected Data (The Audit Trail)
-- You should see rows with "Data Quality: Missing Category"
SELECT * FROM ERR_SALES_REJECTS;

-- 3. Check Raw History (The Zero Data Loss Vault)
-- This contains 100% of the data generated
SELECT * FROM RAW_SALES_ARCHIVE;

```

---

## 🔧 Key Technical Features

### 1. Universal SQL Runner (`scripts/sql_runner.py`)

A custom Python utility that replaces manual SQL interaction. It:

* Parses complex SQL files and PL/SQL blocks.
* Handles delimiters (`/`) and semicolons automatically.
* Uses Environment Variables to switch between `SYSTEM` and `RETAIL_DW` users during the pipeline execution.

### 2. Zero Data Loss Architecture

Every single row generated is first copied to `RAW_SALES_ARCHIVE` before any transformation occurs. This allows for full replayability and auditing.

### 3. In-Database Transformation

We use **PL/SQL Stored Procedures** (`pkg_etl_retail`) to handle business logic. This is faster than processing in Python because the data never leaves the database engine.

---

**Author:** Pravin