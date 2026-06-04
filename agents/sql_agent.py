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
    Builds rich context about the dataframe
    """

    lines = []

    # Schema
    lines.append("### Schema")

    for col in df.columns:
        null_count = int(df[col].isnull().sum())
        lines.append(
            f"- {col} ({df[col].dtype}) nulls: {null_count}"
        )

    # Numeric stats
    numeric_cols = df.select_dtypes(
        include="number"
    ).columns.tolist()

    if numeric_cols:

        lines.append("\n### Numeric Column Stats")

        stats = (
            df[numeric_cols]
            .describe()
            .loc[["min", "max", "mean", "std"]]
        )

        lines.append(stats.to_string())

    # Categorical values
    cat_cols = df.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    if cat_cols:

        lines.append(
            "\n### Categorical Columns — Top Unique Values"
        )

        for col in cat_cols:

            top = (
                df[col]
                .value_counts()
                .head(5)
                .index
                .tolist()
            )

            lines.append(
                f"- {col}: {top}"
            )

    # Sample rows
    lines.append("\n### Sample Rows")

    sample = df.sample(
        min(5, len(df)),
        random_state=42
    )

    lines.append(
        sample.to_string(index=False)
    )

    return "\n".join(lines)


def generate_sql(
    question: str,
    df: pd.DataFrame,
    table_name: str = "sales",
    conversation_history=None,
    last_error=None,
    max_retries: int = 3,
):

    table_context = build_table_context(df)

    history_block = ""

    if conversation_history:

        pairs = []

        for msg in conversation_history[-6:]:

            role = msg["role"].upper()

            pairs.append(
                f"{role}: {msg['content']}"
            )

        history_block = (
            "\n\nConversation so far:\n"
            + "\n".join(pairs)
        )

    error_block = ""

    if last_error:

        error_block = f"""
The previous SQL attempt failed:

{last_error}

Please fix it.
"""

    prompt = f"""
You are a SQL expert working with DuckDB.

Table name: {table_name}

{table_context}

{history_block}

{error_block}

Rules:

1. Return ONLY SQL.
2. No markdown.
3. Use exact table name {table_name}.
4. Use only columns in schema.
5. Write DuckDB compatible SQL.

Question:
{question}
"""

    last_exc = None

    for _ in range(max_retries):

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        sql = response.text or ""

        sql = re.sub(
            r"```(?:sql)?",
            "",
            sql,
            flags=re.IGNORECASE
        )

        sql = sql.replace(
            "```",
            ""
        )

        sql = sql.strip()

        if re.search(
            r"\bSELECT\b",
            sql,
            re.IGNORECASE
        ):
            return sql

        last_exc = (
            f"Invalid SQL generated: {sql}"
        )

        prompt += f"""

Previous response invalid.

{last_exc}

Try again.
"""

    raise ValueError(
        f"Failed to generate valid SQL. {last_exc}"
    )