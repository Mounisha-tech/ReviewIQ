import pandas as pd
import re

def load_reviews(file_path):
    """
    Load review data from a csv file.
    """
    df=pd.read_csv(file_path)
    return df

def normalize_column_name(column_name):
    """
    Convert a column name into a standard snake_case format
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

    return column_name

def normalize_columns(df):
    """
    Normalize all column names in DataFrame
    """
    df=df.copy()

    df.columns=[normalize_column_name(column) for column in df.columns]

    return df

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

def map_columns(df):
    """
    Map different possible column names to the standard ReviewIQ column names
    """
    column_mapping={}

    for standard_name,aliases in COLUMN_ALIASES.items():
        for column in df.columns:
            if column in aliases:
                column_mapping[column]=standard_name
                break

    df=df.rename(columns=column_mapping)

    return df

def validate_required_columns(df):
    """
    Validate that all required ReviewIQ columns are present
    """
    required_columns=[
        "review_id",
        "product_id",
        "product_name",
        "review_text",
        "rating",
        "review_date"
    ]
    missing_columns=[
        column 
        for column in required_columns
        if column not in df.columns
    ]
    if missing_columns:
        return False,missing_columns
    
    return True,[]

if __name__ == "__main__":
    df = load_reviews("data/amazon_reviews.csv")

    print("Original columns:")
    print(df.columns.tolist())

    df = normalize_columns(df)

    print("\nNormalized columns:")
    print(df.columns.tolist())

    df = map_columns(df)

    print("\nMapped columns:")
    print(df.columns.tolist())

    is_valid, missing_columns = validate_required_columns(df)

    print("\nValidation result:")

    if is_valid:
        print("Dataset is valid!")
    else:
        print("Dataset is missing:", missing_columns)