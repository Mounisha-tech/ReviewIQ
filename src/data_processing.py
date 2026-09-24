import pandas as pd
import re


# =========================================================
# 1. LOAD REVIEWS
# =========================================================

def load_reviews(file_path):
    """
    Load review data from a CSV file.
    """
    df = pd.read_csv(file_path)
    return df


# =========================================================
# 2. NORMALIZE COLUMN NAMES
# =========================================================

def normalize_column_name(column_name):
    """
    Convert a column name into standard snake_case format.
    """

    column_name = re.sub(
        r"([A-Z]+)([A-Z][a-z])",
        r"\1_\2",
        str(column_name)
    )

    column_name = re.sub(
        r"([a-z0-9])([A-Z])",
        r"\1_\2",
        column_name
    )

    column_name = column_name.lower()

    column_name = re.sub(
        r"[^a-z0-9]+",
        "_",
        column_name
    )

    column_name = column_name.strip("_")

    return column_name


def normalize_columns(df):
    """
    Normalize all column names in a DataFrame.
    """

    df = df.copy()

    df.columns = [
        normalize_column_name(column)
        for column in df.columns
    ]

    return df


# =========================================================
# 3. COLUMN ALIASES
# =========================================================

COLUMN_ALIASES = {

    "review_id": [
        "review_id",
        "reviewid",
        "review_identifier"
    ],

    "product_id": [
        "product_id",
        "productid",
        "item_id",
        "itemid",
        "product_code"
    ],

    "product_name": [
        "product_name",
        "productname",
        "product_title",
        "producttitle",
        "item_name",
        "itemname"
    ],

    "review_text": [
        "review_text",
        "reviewtext",
        "review_body",
        "reviewbody",
        "review",
        "comment",
        "feedback"
    ],

    "rating": [
        "rating",
        "star_rating",
        "starrating",
        "stars",
        "score"
    ],

    "review_date": [
        "review_date",
        "reviewdate",
        "date",
        "date_posted",
        "dateposted"
    ]
}


# =========================================================
# 4. MAP COLUMNS
# =========================================================

def map_columns(df):
    """
    Map different possible column names
    to standard ReviewIQ column names.
    """

    column_mapping = {}

    for standard_name, aliases in COLUMN_ALIASES.items():

        for column in df.columns:

            if column in aliases:

                column_mapping[column] = standard_name

                break

    df = df.rename(
        columns=column_mapping
    )

    return df


# =========================================================
# 5. VALIDATE REQUIRED COLUMNS
# =========================================================

def validate_required_columns(df):
    """
    Validate that all required ReviewIQ columns
    are present.
    """

    required_columns = [
        "review_id",
        "product_id",
        "product_name",
        "review_text",
        "rating",
        "review_date"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        return False, missing_columns

    return True, []


# =========================================================
# 6. CHECK MISSING VALUES
# =========================================================

def check_missing_values(df):
    """
    Check for missing values in important
    ReviewIQ columns.
    """

    important_columns = [
        "review_id",
        "product_id",
        "product_name",
        "review_text",
        "rating",
        "review_date"
    ]

    missing_values = {}

    for column in important_columns:

        missing_values[column] = (
            df[column].isna().sum()
        )

    return missing_values


# =========================================================
# 7. CHECK INVALID RATINGS
# =========================================================

def check_invalid_ratings(df):
    """
    Count ratings outside the valid range of 1 to 5.
    """

    numeric_ratings = pd.to_numeric(
        df["rating"],
        errors="coerce"
    )

    invalid_ratings = (
        numeric_ratings.isna()
        |
        (numeric_ratings < 1)
        |
        (numeric_ratings > 5)
    )

    return invalid_ratings.sum()


# =========================================================
# 8. CHECK DUPLICATE REVIEWS
# =========================================================

def check_duplicate_reviews(df):
    """
    Count duplicate review IDs.
    """

    return df["review_id"].duplicated().sum()


# =========================================================
# 9. CHECK EMPTY REVIEWS
# =========================================================

def check_empty_reviews(df):
    """
    Count reviews that contain no meaningful text.
    """

    empty_reviews = (
        df["review_text"]
        .fillna("")
        .astype(str)
        .str.strip()
        .eq("")
        .sum()
    )

    return empty_reviews


# =========================================================
# 10. CHECK INVALID DATES
# =========================================================

def check_invalid_dates(df):
    """
    Count invalid review dates.
    """

    converted_dates = pd.to_datetime(
        df["review_date"],
        errors="coerce"
    )

    return converted_dates.isna().sum()


# =========================================================
# 11. COMPLETE DATA INGESTION PIPELINE
# =========================================================

def process_reviews(file_path):
    """
    Complete ReviewIQ data ingestion pipeline.

    Loads, normalizes, maps, validates,
    and checks the review dataset.
    """

    # -----------------------------------------------------
    # Step 1: Load data
    # -----------------------------------------------------

    df = load_reviews(file_path)

    # -----------------------------------------------------
    # Step 2: Normalize column names
    # -----------------------------------------------------

    df = normalize_columns(df)

    # -----------------------------------------------------
    # Step 3: Map columns to standard names
    # -----------------------------------------------------

    df = map_columns(df)

    # -----------------------------------------------------
    # Step 4: Validate required columns
    # -----------------------------------------------------

    is_valid, missing_columns = (
        validate_required_columns(df)
    )

    if not is_valid:

        raise ValueError(
            "Dataset is missing required columns: "
            f"{missing_columns}"
        )

    # -----------------------------------------------------
    # Step 5: Run data quality checks
    # -----------------------------------------------------

    quality_report = {

        "missing_values":
            check_missing_values(df),

        "invalid_ratings":
            check_invalid_ratings(df),

        "duplicate_reviews":
            check_duplicate_reviews(df),

        "empty_reviews":
            check_empty_reviews(df),

        "invalid_dates":
            check_invalid_dates(df)
    }

    return df, quality_report


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    df, quality_report = process_reviews(
        "data/amazon_reviews.csv"
    )

    print(
        "\n========== ReviewIQ Data Ingestion ==========\n"
    )

    print("Processed dataset:")
    print(df.head())

    print("\nProcessed columns:")
    print(df.columns.tolist())

    print("\nDataset shape:")
    print(df.shape)

    print("\nQuality report:")
    print(quality_report)