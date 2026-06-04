from google import genai
from dotenv import load_dotenv
import pandas as pd
import os
import re

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def build_table_context(df: pd.DataFrame) -> str:
    """
    Builds a rich table context string for the LLM:
    - Schema (column name + dtype)
    - Per-column null count
    - Numeric stats (min, max, mean, std)
    - Categorical columns: top 5 unique values
    - A small random sample (5 rows)
    """

    lines = []

    # --- Schema ---
    lines.append("### Schema")
    for col in df.columns:
        null_count = int(df[col].isnull().sum())
        lines.append(f"  - {col} ({df[col].dtype})  nulls: {null_count}")

    # --- Numeric stats ---
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if numeric_cols:
        lines.append("\n### Numeric Column Stats")
        stats = df[numeric_cols].describe().loc[["min", "max", "mean", "std"]]
        lines.append(stats.to_string())

    # --- Categorical value samples ---
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if cat_cols:
        lines.append("\n### Categorical Columns — Top Unique Values")
        for col in cat_cols:
            top = df[col].value_counts().head(5).index.tolist()
            lines.append(f"  - {col}: {top}")

    # --- Random sample rows ---
    lines.append("\n### Sample Rows (up to 5, random)")
    sample = df.sample(min(5, len(df)), random_state=42)
    lines.append(sample.to_string(index=False))

    return "\n".join(lines)


def generate_sql(
    question: str,
    df: pd.DataFrame,
    table_name: str = "sales",
    conversation_history: list[dict] | None = None,
    last_error: str | None = None,
    max_retries: int = 3,
) -> str:
    """
    Generates SQL from a natural language question.

    Args:
        question:              The user's natural language question.
        df:                    The actual DataFrame (used to build rich context).
        table_name:            The DuckDB table name to query against.
        conversation_history:  List of {"role": "user"/"assistant", "content": "..."}
                               dicts for multi-turn context.
        last_error:            If the previous SQL attempt failed, pass the error
                               message here so the model can self-correct.
        max_retries:           How many times to retry on invalid SQL before raising.
    """

    table_context = build_table_context(df)

    history_block = ""
    if conversation_history:
        pairs = []
        for msg in conversation_history[-6:]:   # keep last 3 Q/A pairs
            role = msg["role"].upper()
            pairs.append(f"{role}: {msg['content']}")
        history_block = "\n\nConversation so far:\n" + "\n".join(pairs)

    error_block = ""
    if last_error:
        error_block = f"\n\nThe previous SQL attempt failed with this error:\n{last_error}\nPlease fix it."

    prompt = f"""
You are a SQL expert working with DuckDB.

Table name: {table_name}

{table_context}
{history_block}
{error_block}

Rules:
1. Return ONLY raw SQL — no markdown fences, no explanation.
2. Use the exact table name: {table_name}
3. Use only the columns listed in the schema above.
4. Write DuckDB-compatible SQL.

Question: {question}
""".strip()

    last_exc = None

    for attempt in range(max_retries):
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        sql = response.text or ""

        # Strip any accidental markdown fences
        sql = re.sub(r"```(?:sql)?", "", sql, flags=re.IGNORECASE).replace("```", "")

        # Basic sanity check: must contain SELECT
        if re.search(r"\bSELECT\b", sql, re.IGNORECASE):
            return sql.strip()

        # If no SELECT found, retry with error feedback
        last_exc = f"Response did not contain a valid SELECT statement: {sql!r}"
        prompt += f"\n\nYour last response was invalid ({last_exc}). Try again."

    raise ValueError(
        f"Failed to generate valid SQL after {max_retries} attempts. "
        f"Last issue: {last_exc}"
    )