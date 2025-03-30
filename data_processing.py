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

METRIC_COLUMNS = ["Impressions", "Clicks", "Spend", "Conversions"]

# --- STEP 2: Standardize Column Names ---
def standardize_columns(df):
    df.columns = [col.strip() for col in df.columns]
    df.rename(columns={k: v for k, v in COLUMN_ALIASES.items()}, inplace=True)
    return df

# --- STEP 3: Grouping Column Detection (≥ 5 unique values) ---
def find_groupable_column(df):
    cols = {col.lower().strip(): col for col in df.columns}

    preferred_columns = [
        "creative",
        "creative name",
        "creative id",
        "device type",
        "placement",
        "domain",
        "app",
        "country",
        "geo",
        "line item",
        "insertion order"
    ]

    for pref in preferred_columns:
        if pref in cols:
            actual_col = cols[pref]
            if df[actual_col].nunique() >= 5:
                return actual_col

    for col in df.columns:
        if col in METRIC_COLUMNS:
            continue
        if df[col].nunique() >= 5:
            return col

    return None

# --- STEP 4: Auto-metric Calculation ---
def add_autometrics(df):
    df["CTR"] = df["Clicks"] / df["Impressions"].replace(0, 1)
    df["CPM"] = df["Spend"] / df["Impressions"].replace(0, 1) * 1000
    df["CPC"] = df["Spend"] / df["Clicks"].replace(0, 1)
    df["Conversion Rate"] = df["Conversions"] / df["Clicks"].replace(0, 1)
    df["Cost per Conversion"] = df["Spend"] / df["Conversions"].replace(0, 1)
    df["Impact Score"] = df["Spend"] * df["CTR"]  # Custom ranking logic
    return df

# --- STEP 5: Top + Bottom 5 by Impact Score ---
def summarize_by_group(df, group_col):
    grouped = df.groupby(group_col).agg({
        "Impressions": "sum",
        "Clicks": "sum",
        "Spend": "sum",
        "Conversions": "sum"
    }).reset_index()

    grouped = add_autometrics(grouped)
    grouped = grouped[grouped["Impressions"] >= 1000]

    # Top 5 by Impact (Spend × CTR)
    top5 = grouped.sort_values("Impact Score", ascending=False).head(5)

    # Bottom 5 by Impact (Spend > 0 + low CTR)
    bottom5 = grouped[grouped["Spend"] > 0].sort_values("Impact Score", ascending=True).head(5)

    # Combine and remove any duplicates
    combined = pd.concat([top5, bottom5]).drop_duplicates(subset=[group_col])

    return {
        "group_by": group_col,
        "top_5": top5.to_dict(orient="records"),
        "bottom_5": bottom5.to_dict(orient="records"),
        "combined": combined.to_dict(orient="records")
    }

# --- STEP 6: Main Processor ---
def process_uploaded_file(file):
    try:
        df = pd.read_excel(file.file)
        df = standardize_columns(df)

        group_col = find_groupable_column(df)
        if not group_col:
            return None, "No groupable column found"

        print(f"✅ Grouped by: '{group_col}' in file: {file.filename}")

        summary = summarize_by_group(df, group_col)

        return {
            "report_type": group_col.lower().replace(" ", "_"),
            "source_file": file.filename,
            "group_by": summary["group_by"],
            "top_5": summary["top_5"],
            "bottom_5": summary["bottom_5"],
            "summary": summary["combined"]
        }, None

    except Exception as e:
        return None, f"❌ Failed to process file: {str(e)}"
