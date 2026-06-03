import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb

from agents.sql_agent import generate_sql
from utils.data_cleaner import clean_data
from utils.insights_generator import generate_insights

st.set_page_config(
    page_title="Autonomous Data Analyst",
    layout="wide"
)

st.title("🤖 Autonomous Data Analyst")

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

    except:
        st.warning(
            "No numerical columns available."
        )

    # -----------------------------
    # Charts
    # -----------------------------

    if "Region" in df.columns and "Revenue" in df.columns:

        st.subheader("Revenue by Region")

        region_data = (
            df.groupby("Region")["Revenue"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            region_data,
            x="Region",
            y="Revenue",
            title="Revenue by Region"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    if "Product" in df.columns and "Revenue" in df.columns:

        st.subheader("Revenue Share by Product")

        product_data = (
            df.groupby("Product")["Revenue"]
            .sum()
            .reset_index()
        )

        fig2 = px.pie(
            product_data,
            names="Product",
            values="Revenue",
            title="Revenue Share by Product"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
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

    st.subheader(
        "AI Generated Insights"
    )

    if st.button(
        "Generate Insights"
    ):

        with st.spinner(
            "Analyzing dataset..."
        ):

            insights = generate_insights(df)

            st.write(insights)

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
                question,
                df.columns.tolist()
            )

            st.subheader(
                "Generated SQL"
            )

            st.code(
                sql,
                language="sql"
            )

            con = duckdb.connect()

            con.register(
                "sales",
                df
            )

            result = con.execute(
                sql
            ).fetchdf()

            st.subheader(
                "Answer"
            )

            st.dataframe(result)

        except Exception as e:

            st.error(str(e))

else:

    st.info(
        "Please upload a CSV file."
    )