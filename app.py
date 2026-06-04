import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb

from agents.sql_agent import generate_sql
from utils.data_cleaner import clean_data
from utils.insights_generator import generate_insights
from utils.pdf_generator import create_pdf_report


def run_sql(sql, df, table_name):

    con = duckdb.connect()

    try:
        con.register(table_name, df)

        return con.execute(sql).fetchdf()

    finally:
        con.close()


def auto_chart(result):

    cat_cols = result.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    num_cols = result.select_dtypes(
        include="number"
    ).columns.tolist()

    if len(cat_cols) == 1 and len(num_cols) == 1:

        fig = px.bar(
            result,
            x=cat_cols[0],
            y=num_cols[0]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

st.set_page_config(
    page_title="Autonomous Data Analyst",
    layout="wide"
)

st.title("🤖 Autonomous Data Analyst")

# Session State

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "insights" not in st.session_state:
    st.session_state.insights = ""

uploaded_file = st.file_uploader(
    "Upload CSV File",
    type=["csv"]
)

if uploaded_file is not None:

    # -----------------------------
    # Load and Clean Data
    # -----------------------------

    df = pd.read_csv(uploaded_file)

    df, report = clean_data(df)

    table_name = (
        uploaded_file.name
        .replace(".csv", "")
        .replace(" ", "_")
        .lower()
    )

    # -----------------------------
    # Dataset Preview
    # -----------------------------

    st.subheader("Dataset Preview")
    st.dataframe(df)

    # -----------------------------
    # Dataset Summary
    # -----------------------------

    st.subheader("Dataset Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Rows", df.shape[0])

    with col2:
        st.metric("Columns", df.shape[1])

    st.write("Column Names")
    st.write(df.columns.tolist())

    # -----------------------------
    # Data Cleaning Report
    # -----------------------------

    st.subheader("Data Cleaning Report")

    st.write(
        f"Missing Values Before: {report['missing_values_before']}"
    )

    st.write(
        f"Missing Values After: {report['missing_values_after']}"
    )

    st.write(
        f"Duplicates Before: {report['duplicates_before']}"
    )

    st.write(
        f"Duplicates After: {report['duplicates_after']}"
    )

    # -----------------------------
    # Data Types
    # -----------------------------

    st.subheader("Data Types")

    st.dataframe(
        pd.DataFrame(
            df.dtypes,
            columns=["Datatype"]
        )
    )

    # -----------------------------
    # Statistical Summary
    # -----------------------------

    st.subheader("Statistical Summary")

    try:
        st.dataframe(df.describe())

    except Exception:
        st.warning(
            "No numerical columns available."
        )

    # -----------------------------
    # Auto Generated Charts
    # -----------------------------

    st.subheader("Auto Generated Charts")

    numeric_cols = df.select_dtypes(
        include="number"
    ).columns.tolist()

    categorical_cols = df.select_dtypes(
        include=["object"]
    ).columns.tolist()

    if len(numeric_cols) > 0 and len(categorical_cols) > 0:

        selected_cat = st.selectbox(
            "Select Category Column",
            categorical_cols
        )

        selected_num = st.selectbox(
            "Select Numeric Column",
            numeric_cols
        )

        chart_data = (
            df.groupby(selected_cat)[selected_num]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            chart_data,
            x=selected_cat,
            y=selected_num,
            title=f"{selected_num} by {selected_cat}"
        )
        fig.write_image("chart.png")

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "No suitable columns found for chart generation."
        )

    # -----------------------------
    # Correlation Heatmap
    # -----------------------------

    st.subheader("Correlation Heatmap")

    numeric_df = df.select_dtypes(
        include="number"
    )

    if numeric_df.shape[1] >= 2:

        corr_matrix = numeric_df.corr()

        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            title="Correlation Heatmap"
            )
        fig.write_image("heatmap.png")

        st.plotly_chart(
            fig,
            use_container_width=True
            )

    else:

        st.info(
            "Need at least 2 numeric columns for correlation analysis."
        )

    # -----------------------------
    # SQL Query Runner
    # -----------------------------

    st.subheader("SQL Query Runner")

    query = st.text_area(
        "Enter SQL Query",
        value="SELECT * FROM sales"
    )

    if st.button("Run Query"):

        try:

            con = duckdb.connect()

            con.register(
                "sales",
                df
            )

            result = con.execute(
                query
            ).fetchdf()

            st.success(
                "Query Executed Successfully"
            )

            st.dataframe(result)

        except Exception as e:

            st.error(str(e))

    # -----------------------------
    # AI Insights
    # -----------------------------

    st.subheader("AI Generated Insights")

    if "insights" not in st.session_state:
        st.session_state.insights = ""

    if st.button("Generate Insights"):

        with st.spinner(
            "Analyzing dataset..."
        ):

            st.session_state.insights = generate_insights(df)

    st.write(st.session_state.insights)

    # -----------------------------
    # PDF Report
    # -----------------------------

    st.subheader("Download Report")

    if st.button("Generate PDF Report"):

        summary = f"""
Rows: {df.shape[0]}
Columns: {df.shape[1]}
Column Names: {df.columns.tolist()}
"""

        cleaning_report = f"""
Missing Before: {report['missing_values_before']}
Missing After: {report['missing_values_after']}
Duplicates Before: {report['duplicates_before']}
Duplicates After: {report['duplicates_after']}
"""

        pdf_file = create_pdf_report(
            "analysis_report.pdf",
            summary,
            cleaning_report,
            st.session_state.insights,
            chart_path="chart.png",
            heatmap_path="heatmap.png"
        )

        with open(pdf_file, "rb") as file:

            st.download_button(
                label="Download PDF",
                data=file,
                file_name="analysis_report.pdf",
                mime="application/pdf"
            )

    # -----------------------------
    # AI Analyst
    # -----------------------------

    st.subheader(
        "Ask AI About Your Data"
    )

    question = st.text_input(
        "Ask a Question",
        placeholder="Which product generated the most revenue?"
    )

    if st.button("Ask AI"):
        

        try:

            sql = generate_sql(
                question=question,
                df=df,
                table_name=table_name,
                conversation_history=st.session_state.chat_history
            )

            st.subheader(
                "Generated SQL"
            )

            st.code(
                sql,
                language="sql"
            )

            result = run_sql(
                sql,
                df,
                table_name
            )

            st.subheader(
                "Answer"
            )

            st.dataframe(result)

            auto_chart(result)


            st.download_button(
                label="Download Result CSV",
                data=result.to_csv(index=False),
                file_name="query_result.csv",
                mime="text/csv"
            )


            st.session_state.chat_history.append({
                "question": question,
                "sql": sql,
                "answer": result.to_string(index=False)
            })

        except Exception as e:

            st.error(str(e))


        # -----------------------------
        # Clear Chat
        # -----------------------------

        if st.session_state.chat_history:

            if st.button("🗑 Clear Chat"):
        
                st.session_state.chat_history = []

                st.rerun()

        # -----------------------------
        # Chat History
        # -----------------------------

        if st.session_state.chat_history:

            st.subheader("Chat History")

            for idx, item in enumerate(
                st.session_state.chat_history,
                start=1
            ):
        
                with st.expander(
                    f"Question {idx}: {item['question']}"
                ):
        
                    st.write("Generated SQL")

                    st.code(
                        item["sql"],
                        language="sql"
                    )

                    st.write("Answer")

                    st.text(
                        item["answer"]
                    )
        
else:

    st.info(
        "Please upload a CSV file."
    )