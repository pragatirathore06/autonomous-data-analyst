from google import genai
from dotenv import load_dotenv
from agents.sql_agent import build_table_context   # reuse the same rich context builder
import pandas as pd
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_insights(df: pd.DataFrame) -> str:
    """
    Generates business insights from the full dataset using a rich context
    instead of just the first 20 rows.

    Sends to the model:
      - Full schema with dtypes and null counts
      - Numeric stats (min/max/mean/std) for every numeric column
      - Top unique values for every categorical column
      - A random 5-row sample so the model can see real value formats
      - Row + column counts
    """

    table_context = build_table_context(df)

    prompt = f"""
You are a senior data analyst.

Dataset shape: {df.shape[0]} rows × {df.shape[1]} columns

{table_context}

Based on the schema, statistics, and sample above, provide a structured analysis:

1. **Key Insights** — most important patterns or facts in this data
2. **Trends** — any directional movement visible in the data
3. **Anomalies** — outliers, unexpected nulls, suspicious values
4. **Recommendations** — concrete next steps or analyses to run

Be specific. Reference actual column names and values where possible.
""".strip()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text