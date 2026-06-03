from agents.sql_agent import generate_sql
import duckdb
import pandas as pd

# Load CSV
df = pd.read_csv("data/sales.csv")

# Ask Question
question = "Which region has highest revenue?"

# Generate SQL
sql = generate_sql(question)

print("Generated SQL:")
print(sql)

# Execute SQL
con = duckdb.connect()
con.register("sales", df)

result = con.execute(sql).fetchdf()

print("\nResult:")
print(result)