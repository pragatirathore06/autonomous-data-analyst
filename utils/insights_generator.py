from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def generate_insights(df):

    sample_data = df.head(20).to_string()

    prompt = f"""
You are a senior data analyst.

Analyze the dataset below and provide:

1. Key Insights
2. Trends
3. Anomalies
4. Recommendations

Dataset:

{sample_data}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text