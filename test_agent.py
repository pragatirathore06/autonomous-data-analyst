import pandas as pd
from agents.sql_agent import generate_sql

df = pd.read_csv("data/sales.csv")

question = "Which region generated the highest revenue?"

sql = generate_sql(
    question=question,
    df=df,
    table_name="sales"
)

print(sql)