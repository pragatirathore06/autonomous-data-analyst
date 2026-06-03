from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def generate_sql(question, columns):

    prompt = f"""
You are a SQL expert.

Table Name: sales

Available Columns:
{columns}

Convert the user's question into SQL.

Rules:
1. Return ONLY SQL.
2. Use table name sales.
3. Use only the available columns.

Question:
{question}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    sql = response.text

    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")

    return sql.strip()