from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

# --- PATH CONFIGURATION ---
# Based on docker-compose volumes
SCRIPT_PATH = "/opt/airflow/scripts/sql_runner.py"
SQL_DIR = "/opt/airflow/sql/init_oracle"

# --- CREDENTIALS ---
# 1. Admin (SYSTEM) - Used for creating users/grants
ADMIN_ENV = {
    'DB_USER': 'SYSTEM',
    'DB_PASS': 'AdminPassword123', # Default for gvenzl/oracle-xe
    'DB_DSN':  'oracle-db:1521/xepdb1'
}

# 2. App User (RETAIL_DW) - Used for creating tables
APP_ENV = {
    'DB_USER': 'RETAIL_DW',
    'DB_PASS': 'RetailPass123',
    'DB_DSN':  'oracle-db:1521/xepdb1'
}

with DAG(
    'retail_project_init',
    description='One-Time Setup: Users, Directories, and Schema',
    schedule_interval=None, # Manual Trigger Only
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['retail', 'setup', 'admin'],
) as dag:

    # --- STEP 1: ADMIN TASKS ---
    create_user = BashOperator(
        task_id='1_create_user_system',
        bash_command=f'python3 {SCRIPT_PATH} {SQL_DIR}/01_setup_users.sql',
        env=ADMIN_ENV
    )

    # --- STEP 2: USER TASK (Directory) ---
    # RETAIL_DW creates the logical directory object
    create_dir = BashOperator(
        task_id='2_create_directory_app',
        bash_command=f'python3 {SCRIPT_PATH} {SQL_DIR}/02_directory_creation.sql',
        env=APP_ENV
    )

    # --- STEP 3: ADMIN TASK (Grant) ---
    # SYSTEM grants read/write permissions on that directory
    grant_dir = BashOperator(
        task_id='3_grant_access_system',
        bash_command=f'python3 {SCRIPT_PATH} {SQL_DIR}/03_grant_to_dir_sys.sql',
        env=ADMIN_ENV
    )

    # --- STEP 4: SCHEMA BUILD ---
    deploy_archive = BashOperator(
        task_id='4a_deploy_archive_tables',
        bash_command=f'python3 {SCRIPT_PATH} {SQL_DIR}/04_archive_table_DDL.sql',
        env=APP_ENV
    )

    deploy_schema = BashOperator(
        task_id='4b_deploy_analysis_tables',
        bash_command=f'python3 {SCRIPT_PATH} {SQL_DIR}/05_ddl_tables.sql',
        env=APP_ENV
    )

    deploy_pkg = BashOperator(
        task_id='4c_compile_plsql',
        bash_command=f'python3 {SCRIPT_PATH} {SQL_DIR}/06_plsql_pkg.sql',
        env=APP_ENV
    )

    # --- EXECUTION ORDER ---
    create_user >> create_dir >> grant_dir >> deploy_archive >> deploy_schema >> deploy_pkg