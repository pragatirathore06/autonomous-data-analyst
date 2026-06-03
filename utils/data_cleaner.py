import pandas as pd

def clean_data(df):

    report = {}

    # Missing values before cleaning
    report["missing_values_before"] = int(
        df.isnull().sum().sum()
    )

    # Duplicates before cleaning
    report["duplicates_before"] = int(
        df.duplicated().sum()
    )

    # Remove duplicates
    df = df.drop_duplicates()

    # Fill missing values safely
    for col in df.columns:

        if pd.api.types.is_numeric_dtype(df[col]):

            df[col] = df[col].fillna(
                df[col].mean()
            )

        else:

            df[col] = df[col].fillna(
                "Unknown"
            )

    report["missing_values_after"] = int(
        df.isnull().sum().sum()
    )

    report["duplicates_after"] = int(
        df.duplicated().sum()
    )

    return df, report