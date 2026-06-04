import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb

from agents.sql_agent import generate_sql
from utils.data_cleaner import clean_data
from utils.insights_generator import generate_insights

# ─────────────────────────────────────────
# Page config
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Autonomous Data Analyst",
    layout="wide"
)

st.title("🤖 Autonomous Data Analyst")

# ─────────────────────────────────────────
# Session state initialisation
# ─────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []      # [{role, content}]

if "df" not in st.session_state:
    st.session_state.df = None

if "table_name" not in st.session_state:
    st.session_state.table_name = "data"


# ─────────────────────────────────────────
# Helper: auto chart for a result DataFrame
# ─────────────────────────────────────────
def auto_chart(result: pd.DataFrame):
    """
    If result has exactly one categorical + one numeric column,
    render a bar chart automatically.  Otherwise, just show the table.
    """
    cat_cols = result.select_dtypes(include=["object", "category"]).columns.tolist()
    num_cols = result.select_dtypes(include="number").columns.tolist()

    if len(cat_cols) == 1 and len(num_cols) == 1:
        fig = px.bar(
            result,
            x=cat_cols[0],
            y=num_cols[0],
            title=f"{num_cols[0]} by {cat_cols[0]}"
        )
        st.plotly_chart(fig, use_container_width=True)
    elif len(num_cols) == 2:
        fig = px.scatter(
            result,
            x=num_cols[0],
            y=num_cols[1],
            title=f"{num_cols[0]} vs {num_cols[1]}"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.dataframe(result)


# ─────────────────────────────────────────
# Helper: run SQL safely against a DuckDB
# ─────────────────────────────────────────
def run_sql(sql: str, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    con = duckdb.connect()
    try:
        con.register(table_name, df)
        return con.execute(sql).fetchdf()
    finally:
        con.close()


# ─────────────────────────────────────────
# File upload
# ─────────────────────────────────────────
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file is not None:

    # Only reload if a new file is uploaded
    if (
        st.session_state.df is None
        or st.session_state.get("last_filename") != uploaded_file.name
    ):
        raw_df = pd.read_csv(uploaded_file)
        df, report = clean_data(raw_df)

        st.session_state.df = df
        st.session_state.report = report
        st.session_state.table_name = (
            uploaded_file.name.replace(".csv", "").replace(" ", "_").lower()
        )
        st.session_state.last_filename = uploaded_file.name
        st.session_state.chat_history = []  # reset chat on new file

    df = st.session_state.df
    report = st.session_state.report
    table_name = st.session_state.table_name

    # ─────────────────────────────────────
    # Dataset Preview
    # ─────────────────────────────────────
    st.subheader("Dataset Preview")
    st.dataframe(df.head(50), use_container_width=True)

    # ─────────────────────────────────────
    # Summary metrics
    # ─────────────────────────────────────
    st.subheader("Dataset Summary")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Missing (before)", report["missing_values_before"])
    col4.metric("Duplicates (before)", report["duplicates_before"])

    # ─────────────────────────────────────
    # Data types + statistical summary
    # ─────────────────────────────────────
    with st.expander("🔎 Schema & Statistics"):
        left, right = st.columns(2)
        with left:
            st.write("**Column Types**")
            st.dataframe(
                pd.DataFrame(df.dtypes, columns=["Dtype"]),
                use_container_width=True
            )
        with right:
            st.write("**Statistical Summary**")
            num_df = df.select_dtypes(include="number")
            if not num_df.empty:
                st.dataframe(num_df.describe(), use_container_width=True)
            else:
                st.info("No numeric columns.")

    # ─────────────────────────────────────
    # Dynamic auto-charts
    # ─────────────────────────────────────
    with st.expander("📊 Auto Charts"):
        num_cols = df.select_dtypes(include="number").columns.tolist()
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

        if cat_cols and num_cols:
            chosen_cat = st.selectbox("Category axis", cat_cols, key="chart_cat")
            chosen_num = st.selectbox("Value axis", num_cols, key="chart_num")

            agg = (
                df.groupby(chosen_cat)[chosen_num]
                .sum()
                .reset_index()
                .sort_values(chosen_num, ascending=False)
                .head(20)
            )

            chart_type = st.radio(
                "Chart type",
                ["Bar", "Pie", "Line"],
                horizontal=True,
                key="chart_type"
            )

            if chart_type == "Bar":
                fig = px.bar(agg, x=chosen_cat, y=chosen_num,
                             title=f"{chosen_num} by {chosen_cat}")
            elif chart_type == "Pie":
                fig = px.pie(agg, names=chosen_cat, values=chosen_num,
                             title=f"{chosen_num} share by {chosen_cat}")
            else:
                fig = px.line(agg, x=chosen_cat, y=chosen_num,
                              title=f"{chosen_num} over {chosen_cat}")

            st.plotly_chart(fig, use_container_width=True)

        elif num_cols and len(num_cols) >= 2:
            x_col = st.selectbox("X axis", num_cols, key="scatter_x")
            y_col = st.selectbox("Y axis", num_cols, index=1, key="scatter_y")
            st.plotly_chart(
                px.scatter(df, x=x_col, y=y_col, title=f"{x_col} vs {y_col}"),
                use_container_width=True
            )
        else:
            st.info("Not enough column variety for an auto chart.")

    # ─────────────────────────────────────
    # SQL Query Runner
    # ─────────────────────────────────────
    with st.expander("🛠 SQL Query Runner"):
        query = st.text_area(
            "Enter SQL Query",
            value=f"SELECT * FROM {table_name} LIMIT 10"
        )
        if st.button("Run Query"):
            try:
                result = run_sql(query, df, table_name)
                st.success("Query executed successfully.")
                auto_chart(result)
            except Exception as e:
                st.error(f"SQL Error: {e}")

    # ─────────────────────────────────────
    # AI Insights
    # ─────────────────────────────────────
    with st.expander("💡 AI Generated Insights"):
        if st.button("Generate Insights"):
            with st.spinner("Analysing dataset..."):
                try:
                    insights = generate_insights(df)
                    st.markdown(insights)
                except Exception as e:
                    st.error(f"Could not generate insights: {e}")

    # ─────────────────────────────────────
    # Conversational AI Analyst
    # ─────────────────────────────────────
    st.subheader("💬 Ask AI About Your Data")

    # Render existing chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sql"):
                st.code(msg["sql"], language="sql")
            if msg.get("result") is not None:
                auto_chart(msg["result"])

    # Chat input
    question = st.chat_input("Ask a question about your data…")

    if question:
        # Show user message immediately
        with st.chat_message("user"):
            st.markdown(question)

        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                last_error = None
                sql = None
                result = None

                try:
                    sql = generate_sql(
                        question=question,
                        df=df,
                        table_name=table_name,
                        conversation_history=st.session_state.chat_history,
                        last_error=last_error,
                    )

                    result = run_sql(sql, df, table_name)
                    answer = f"Here are the results for: **{question}**"

                except Exception as e:
                    answer = f"⚠️ Could not answer that question. Error: `{e}`"
                    sql = sql  # may still have the bad SQL for display

                st.markdown(answer)
                if sql:
                    st.code(sql, language="sql")
                if result is not None:
                    auto_chart(result)

        # Store assistant response + artifacts in history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer,
            "sql": sql,
            "result": result,
        })

    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑 Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

else:
    st.info("Please upload a CSV file to get started.")