import pandas as pd

# --- STEP 1: Column Aliases ---
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

# Core metric columns used in calculations
METRIC_COLUMNS = ["Impressions", "Clicks", "Spend", "Conversions"]

# --- STEP 2: Standardize Column Names ---
def standardize_columns(df):
    df.columns = [col.strip() for col in df.columns]
    df.rename(columns={k: v for k, v in COLUMN_ALIASES.items()}, inplace=True)
    return df

# --- STEP 3: Find the Best Grouping Column ---
def find_groupable_column(df):
    preferred_columns = [
        "Creative Name",
        "Creative ID",
        "Device Type",
        "Placement",
        "Domain",
        "App",
        "Country",
        "Geo",
        "Line Item",
        "Insertion Order"
    ]

    for col in preferred_columns:
        if col in df.columns:
            unique_vals = df[col].nunique()
            if 2 <= unique_vals <= 25:
                if "Impressions" in df.columns and df.groupby(col)["Impressions"].sum().max() >= 1000:
                    return col

    # Fallback to any other column that looks groupable
    for col in df.columns:
        if col in METRIC_COLUMNS:
            continue
        unique_vals = df[col].nunique()
        if 2 <= unique_vals <= 25:
            if "Impressions" in df.columns and df.groupby(col)["Impressions"].sum().max() >= 1000:
                return col

    return None

# --- STEP 4: Compute Auto-Metrics Safely ---
def add_autometrics(df):
    df["CTR"] = df["Clicks"] / df["Impressions"].replace(0, 1)
    df["CPM"] = df["Spend"] / df["Impressions"].replace(0, 1) * 1000
    df["CPC"] = df["Spend"] / df["Clicks"].replace(0, 1)
    df["Conversion Rate"] = df["Conversions"] / df["Clicks"].replace(0, 1)
    df["Cost per Conversion"] = df["Spend"] / df["Conversions"].replace(0, 1)
    return df

# --- STEP 5: Summarize Data by Group ---
def summarize_by_group(df, group_col):
    grouped = df.groupby(group_col).agg({
        "Impressions": "sum",
        "Clicks": "sum",
        "Spend": "sum",
        "Conversions": "sum"
    }).reset_index()

    grouped = add_autometrics(grouped)
    grouped = grouped.sort_values("Spend", ascending=False).head(5)
    return grouped

# --- STEP 6: Main Handler for Each Uploaded File ---
def process_uploaded_file(file):
    try:
        df = pd.read_excel(file.file)
        df = standardize_columns(df)

        group_col = find_groupable_column(df)
        if not group_col:
            return None, "No groupable column found"

        summary = summarize_by_group(df, group_col)

        return {
            "report_type": group_col.lower().replace(" ", "_"),
            "group_by": group_col,
            "summary": summary.to_dict(orient="records")
        }, None

    except Exception as e:
        return None, f"Failed to process file: {str(e)}"
