import oracledb
import os
import sys
import re

# --- CONFIGURATION ---
# We use standard names (DB_USER) to allow overriding via Airflow ENV
DB_USER = os.getenv('DB_USER', 'RETAIL_DW')
DB_PASS = os.getenv('DB_PASS', 'RetailPass123')
DB_DSN  = os.getenv('DB_DSN', 'oracle-db:1521/xepdb1') 

if len(sys.argv) < 2:
    print("❌ Usage: python sql_runner.py <path_to_sql_file>")
    exit(1)

sql_file_path = sys.argv[1]
print(f"--- Running SQL Script: {sql_file_path} ---")
print(f"--- Connected as: {DB_USER} ---")

has_error = False

try:
    connection = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
    cursor = connection.cursor()

    with open(sql_file_path, 'r') as f:
        full_sql = f.read()

    # Regex: Split by '/' only if it's on a line by itself
    commands = re.split(r'^\s*/\s*$', full_sql, flags=re.MULTILINE)

    for cmd in commands:
        clean_cmd = cmd.strip()
        if not clean_cmd: continue 

        # Logic to detect PL/SQL vs Standard SQL
        lines = clean_cmd.splitlines()
        first_token = ""
        for line in lines:
            s_line = line.strip()
            if not s_line or s_line.startswith('--'): continue
            first_token = s_line.split()[0].upper()
            break
            
        is_plsql = first_token in ['DECLARE', 'BEGIN']
        if first_token == 'CREATE' and any(x in clean_cmd.upper() for x in ['PROCEDURE', 'PACKAGE', 'FUNCTION', 'TRIGGER']):
             is_plsql = True

        if is_plsql:
             if not clean_cmd.endswith(';'): clean_cmd += ';'
        else:
             if clean_cmd.endswith(';'): clean_cmd = clean_cmd[:-1]

        try:
            cursor.execute(clean_cmd)
        except oracledb.Error as e:
            error_str = str(e)
            # Ignore "Not Exists" errors for cleanup
            if any(x in error_str for x in ['ORA-00942', 'ORA-02289', 'ORA-04043', 'ORA-00955']):
                pass 
            else:
                print(f"❌ Error executing command:\n{clean_cmd[:50]}...")
                print(f"   Reason: {e}")
                has_error = True

    if has_error:
        print("🚨 Script finished with errors.")
        exit(1)
    else:
        print("✅ SQL Script Executed Successfully.")

except Exception as e:
    print(f"❌ Fatal Error: {e}")
    exit(1)
finally:
    if 'connection' in locals(): connection.close()