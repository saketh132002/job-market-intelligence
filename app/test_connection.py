import os
from dotenv import load_dotenv
from databricks import sql

load_dotenv()

print("Connecting...")
connection = sql.connect(
    server_hostname=os.getenv("DATABRICKS_HOST"),
    http_path=os.getenv("DATABRICKS_HTTP_PATH"),
    access_token=os.getenv("DATABRICKS_TOKEN"),
)

cursor = connection.cursor()
cursor.execute("SELECT COUNT(*) AS n FROM jobmarket.gold.gold_role_summary")
result = cursor.fetchone()
print(f"✅ Connected. Role summary rows: {result.n}")

cursor.close()
connection.close()