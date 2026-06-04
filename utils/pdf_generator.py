from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os


def create_pdf_report(
    filename,
    summary,
    cleaning_report,
    insights,
    chart_path=None,
    heatmap_path=None
):

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    content = []

    # -------------------------
    # Title
    # -------------------------

    content.append(
        Paragraph(
            "Autonomous Data Analyst Report",
            styles["Title"]
        )
    )

    content.append(
        Spacer(1, 20)
    )

    # -------------------------
    # Dataset Summary
    # -------------------------

    content.append(
        Paragraph(
            "<b>Dataset Summary</b>",
            styles["Heading2"]
        )
    )

    content.append(
        Paragraph(
            summary.replace("\n", "<br/>"),
            styles["BodyText"]
        )
    )

    content.append(
        Spacer(1, 12)
    )

    # -------------------------
    # Cleaning Report
    # -------------------------

    content.append(
        Paragraph(
            "<b>Data Cleaning Report</b>",
            styles["Heading2"]
        )
    )

    content.append(
        Paragraph(
            cleaning_report.replace("\n", "<br/>"),
            styles["BodyText"]
        )
    )

    content.append(
        Spacer(1, 12)
    )

    # -------------------------
    # AI Insights
    # -------------------------

    content.append(
        Paragraph(
            "<b>AI Insights</b>",
            styles["Heading2"]
        )
    )

    content.append(
        Paragraph(
            insights.replace("\n", "<br/>"),
            styles["BodyText"]
        )
    )

    content.append(
        Spacer(1, 20)
    )

    # -------------------------
    # Revenue Chart
    # -------------------------

    if chart_path and os.path.exists(chart_path):

        content.append(
            Paragraph(
                "<b>Chart Analysis</b>",
                styles["Heading2"]
            )
        )

        content.append(
            Spacer(1, 10)
        )

        content.append(
            Image(
                chart_path,
                width=450,
                height=250
            )
        )

        content.append(
            Spacer(1, 20)
        )

    # -------------------------
    # Correlation Heatmap
    # -------------------------

    if heatmap_path and os.path.exists(heatmap_path):

        content.append(
            Paragraph(
                "<b>Correlation Heatmap</b>",
                styles["Heading2"]
            )
        )

        content.append(
            Spacer(1, 10)
        )

        content.append(
            Image(
                heatmap_path,
                width=450,
                height=300
            )
        )

        content.append(
            Spacer(1, 20)
        )

    # -------------------------
    # Build PDF
    # -------------------------

    doc.build(content)

    return filename