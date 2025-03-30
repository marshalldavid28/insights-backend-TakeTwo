import pandas as pd

# Aliases to normalize column names
COLUMN_ALIASES = {
    "Revenue (Adv Currency)": "Spend",
    "Spends": "Spend",
    "Cost": "Spend",
    "Impr.": "Impressions",
    "Impr": "Impressions",
    "Clicks": "Clicks",
    "Total Conversions": "Conversions",
    "Conversions": "Conversions",
}

METRIC_COLUMNS = ["Impressions", "Clicks", "Spend", "Conversions"]

def standardize_columns(df):
    df.columns = [col.strip() for col in df.columns]
    df.rename(columns={k: v for k, v in COLUMN_ALIASES.items()}, inplace=True)
    return df

def find_groupable_column(df):
    preferred_columns = [
        "Creative", "Creative Name", "Creative ID",
        "Device Type", "Placement", "Domain", "App",
        "Country", "Geo", "Line Item", "Insertion Order"
    ]
    for col in preferred_columns:
        if col in df.columns and df[col].nunique() >= 5:
            return col
    return None

def add_metrics(df):
    df["CTR"] = df["Clicks"] / df["Impressions"].replace(0, 1)
    df["CPM"] = df["Spend"] / df["Impressions"].replace(0, 1) * 1000
    df["CPC"] = df["Spend"] / df["Clicks"].replace(0, 1)
    df["Conversion Rate"] = df["Conversions"] / df["Clicks"].replace(0, 1)
    df["Cost per Conversion"] = df["Spend"] / df["Conversions"].replace(0, 1)
    df["Impact Score"] = df["CTR"] * df["Spend"]
    return df

def summarize_by_group(df, group_col):
    grouped = df.groupby(group_col).agg({
        "Impressions": "sum",
        "Clicks": "sum",
        "Spend": "sum",
        "Conversions": "sum"
    }).reset_index()
    grouped = add_metrics(grouped)

    top_5 = grouped.sort_values("Impact Score", ascending=False).head(5).to_dict(orient="records")
    bottom_5 = grouped.sort_values("Impact Score", ascending=True).head(5).to_dict(orient="records")
    summary = grouped.to_dict(orient="records")

    return top_5, bottom_5, summary

def process_uploaded_file(file_obj):
    try:
        df = pd.read_excel(file_obj)
        df = standardize_columns(df)
        group_col = find_groupable_column(df)

        if not group_col:
            return None, "No groupable column found"

        top_5, bottom_5, summary = summarize_by_group(df, group_col)
        df_with_metrics = add_metrics(df)

        return {
            "group_by": group_col,
            "report_type": group_col.lower().replace(" ", "_"),
            "top_5": top_5,
            "bottom_5": bottom_5,
            "summary": summary,
            "full_data": df_with_metrics.to_dict(orient="records")
        }, None
    except Exception as e:
        return None, f"Failed to process file: {str(e)}"
