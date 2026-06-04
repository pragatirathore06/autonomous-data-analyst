from google import genai
from dotenv import load_dotenv
from agents.sql_agent import build_table_context
import pandas as pd
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_insights(df: pd.DataFrame) -> str:

    table_context = build_table_context(df)

    prompt = f"""
You are a senior data analyst.

Dataset Shape:
{df.shape[0]} rows × {df.shape[1]} columns

{table_context}

Analyze the dataset and provide:

# Key Insights
Important patterns in the data.

# Trends
Interesting trends and observations.

# Anomalies
Outliers, missing values, unusual records.

# Recommendations
Actionable recommendations.

Use bullet points.

Be specific and reference actual column names.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text