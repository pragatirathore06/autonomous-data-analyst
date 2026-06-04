# Autonomous Data Analyst

An AI-powered data analytics platform built with Streamlit, DuckDB, Plotly, and Google Gemini that enables users to upload datasets, generate insights, run SQL queries, visualize data, and interact with their data using natural language.

---

## Overview

Autonomous Data Analyst simplifies data exploration by combining traditional analytics with AI-powered insights. Users can upload CSV datasets, perform exploratory data analysis, generate visualizations, run SQL queries, and ask questions in natural language.

---

## Features

### Dataset Upload

* Upload CSV datasets
* Automatic data loading and preprocessing

### Data Cleaning

* Missing value handling
* Duplicate detection and removal
* Data quality reporting

### Exploratory Data Analysis

* Dataset preview
* Data type inspection
* Statistical summaries
* Dataset metrics

### Dynamic Visualizations

* Interactive bar charts
* Category-wise aggregations
* User-selected chart generation
* Correlation heatmaps

### SQL Query Runner

* Execute SQL queries directly on uploaded datasets
* Powered by DuckDB
* Instant query execution and results

### AI-Powered Insights

Uses Google Gemini to generate:

* Key Insights
* Trends
* Anomalies
* Recommendations

### Natural Language Data Querying

Ask questions such as:

* Which region generated the highest revenue?
* Show the top 5 products by sales.
* What is the average revenue by region?

The system automatically:

1. Converts natural language into SQL
2. Executes SQL using DuckDB
3. Displays results
4. Generates visualizations when applicable

### Chat History

* Stores previous AI queries
* Displays generated SQL
* Maintains previous answers

### Export Features

* Download query results as CSV
* Generate PDF reports

### PDF Report Generation

Generated reports include:

* Dataset Summary
* Data Cleaning Report
* AI Insights
* Generated Charts
* Correlation Heatmap

---

## Technology Stack

### Frontend

* Streamlit

### Data Processing

* Pandas
* NumPy

### Visualization

* Plotly
* Kaleido

### Database Engine

* DuckDB

### Artificial Intelligence

* Google Gemini 2.5 Flash

### Reporting

* ReportLab

---

## Project Structure

```text
autonomous-data-analyst/
│
├── agents/
│   └── sql_agent.py
│
├── utils/
│   ├── data_cleaner.py
│   ├── insights_generator.py
│   └── pdf_generator.py
│
├── data/
│   └── sample datasets
│
├── app.py
├── requirements.txt
├── README.md
└── .env
```

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/pragatirathore06/autonomous-data-analyst.git
cd autonomous-data-analyst
```

### Create a Virtual Environment

```bash
python -m venv venv
```

### Activate the Environment

Windows:

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

Obtain your API key from Google AI Studio.

---

## Running the Application

```bash
streamlit run app.py
```

---

## Sample Workflow

1. Upload a CSV dataset.
2. Review the dataset summary and cleaning report.
3. Explore visualizations and correlation heatmaps.
4. Generate AI-powered insights.
5. Ask questions about the dataset using natural language.
6. Export results as CSV or PDF reports.

---

## Future Enhancements

* Multi-file support
* Advanced visual analytics
* Predictive modeling
* Dashboard export
* User authentication
* Cloud deployment

---

## Author

Pragati Rathore

B.Tech Mechanical Engineering
Indian Institute of Technology Roorkee

GitHub: https://github.com/pragatirathore06

---

## License

This project is intended for educational and portfolio purposes.
