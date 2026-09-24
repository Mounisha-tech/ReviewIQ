import pandas as pd

from preprocessing import clean_text
from sentiment import load_sentiment_model
from analytics import (
    calculate_product_metrics,
    calculate_sentiment_metrics,
    analyze_product_strengths_weaknesses,
    generate_recommendations
)


# =========================================================
# RUN REVIEWIQ PIPELINE
# =========================================================

def run_reviewiq_pipeline(file_path):
    """
    Run the complete ReviewIQ seller-side analytics pipeline.

    CSV
        ↓
    Load dataset
        ↓
    Normalize columns
        ↓
    Clean reviews
        ↓
    Load trained sentiment model
        ↓
    TF-IDF transformation
        ↓
    Sentiment prediction
        ↓
    Product analytics
        ↓
    Strengths / weaknesses
        ↓
    Recommendations
    """

    # =====================================================
    # 1. LOAD DATASET
    # =====================================================

    print("1. Loading dataset...")

    df = pd.read_csv(file_path)

    print(
        f"   Loaded {len(df)} reviews."
    )


    # =====================================================
    # 2. NORMALIZE COLUMN NAMES
    # =====================================================

    print("2. Normalizing dataset columns...")

    df.columns = [
        str(column).strip().lower()
        for column in df.columns
    ]


    # =====================================================
    # 3. MAP AMAZON COLUMNS
    # =====================================================

    print("3. Mapping dataset columns...")

    column_mapping = {

        # Amazon → ReviewIQ
        "star_rating": "rating",

        "review_body": "review_text",

        "review_headline": "review_headline",

        "review_date": "review_date",

        "product_title": "product_name",

        "product_id": "product_id",

        "customer_id": "customer_id",

        "review_id": "review_id"
    }

    df = df.rename(
        columns=column_mapping
    )


    # =====================================================
    # 4. VALIDATE REQUIRED COLUMNS
    # =====================================================

    print("4. Validating dataset...")

    required_columns = [
        "rating",
        "review_text"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "Missing required columns: "
            f"{missing_columns}\n"
            f"Available columns: "
            f"{df.columns.tolist()}"
        )


    # =====================================================
    # 5. CLEAN REVIEW TEXT
    # =====================================================

    print("5. Cleaning review text...")

    # Handle missing review text
    df["review_text"] = (
        df["review_text"]
        .fillna("")
        .astype(str)
    )

    # Apply NLP preprocessing
    df["cleaned_review"] = (
        df["review_text"]
        .apply(clean_text)
    )


    # =====================================================
    # 6. REMOVE EMPTY REVIEWS
    # =====================================================

    before_count = len(df)

    df = df[
        df["cleaned_review"]
        .str.strip()
        .ne("")
    ].copy()

    removed_count = (
        before_count - len(df)
    )

    print(
        f"   Removed {removed_count} "
        "empty reviews."
    )

    print(
        f"   Reviews remaining: {len(df)}"
    )


    # =====================================================
    # 7. LOAD SAVED SENTIMENT MODEL
    # =====================================================

    print(
        "6. Loading trained sentiment model..."
    )

    model, vectorizer = (
        load_sentiment_model()
    )


    # =====================================================
    # 8. CREATE TF-IDF FEATURES
    # =====================================================

    print(
        "7. Creating TF-IDF features..."
    )

    review_vectors = (
        vectorizer.transform(
            df["cleaned_review"]
        )
    )


    # =====================================================
    # 9. PREDICT SENTIMENT
    # =====================================================

    print(
        "8. Predicting sentiment..."
    )

    df["sentiment"] = (
        model.predict(
            review_vectors
        )
    )


    # =====================================================
    # 10. PRODUCT METRICS
    # =====================================================

    print(
        "9. Calculating product metrics..."
    )

    product_metrics = (
        calculate_product_metrics(
            df
        )
    )


    # =====================================================
    # 11. SENTIMENT ANALYTICS
    # =====================================================

    print(
        "10. Calculating sentiment analytics..."
    )

    sentiment_metrics = (
        calculate_sentiment_metrics(
            df
        )
    )


    # =====================================================
    # 12. STRENGTHS AND WEAKNESSES
    # =====================================================

    print(
        "11. Identifying strengths "
        "and weaknesses..."
    )

    insights = (
        analyze_product_strengths_weaknesses(
            df
        )
    )

    strengths = insights[
        "strengths"
    ]

    weaknesses = insights[
        "weaknesses"
    ]


    # =====================================================
    # 13. COUNT NEGATIVE REVIEWS
    # =====================================================

    total_negative_reviews = (
        sentiment_metrics[
            "negative_count"
        ]
    )


    # =====================================================
    # 14. GENERATE RECOMMENDATIONS
    # =====================================================

    print(
        "12. Generating recommendations..."
    )

    recommendations = (
        generate_recommendations(

            strengths,

            weaknesses,

            total_negative_reviews
        )
    )


    # =====================================================
    # 15. RETURN COMPLETE RESULTS
    # =====================================================

    print(
        "13. ReviewIQ pipeline completed!"
    )

    return {

        "data": df,

        "product_metrics":
            product_metrics,

        "sentiment_metrics":
            sentiment_metrics,

        "strengths":
            strengths,

        "weaknesses":
            weaknesses,

        "recommendations":
            recommendations
    }


# =========================================================
# TEST COMPLETE PIPELINE
# =========================================================

if __name__ == "__main__":

    print(
        "\n========== ReviewIQ Pipeline ==========\n"
    )


    # =====================================================
    # RUN PIPELINE
    # =====================================================

    results = run_reviewiq_pipeline(
        "data/amazon_reviews.csv"
    )


    # =====================================================
    # PRODUCT SUMMARY
    # =====================================================

    print(
        "\n========== PRODUCT SUMMARY ==========\n"
    )

    product_metrics = (
        results[
            "product_metrics"
        ]
    )

    print(
        "Total Reviews:",
        product_metrics[
            "total_reviews"
        ]
    )

    print(
        "Average Rating:",
        round(
            product_metrics[
                "average_rating"
            ],
            2
        )
    )


    # =====================================================
    # RATING DISTRIBUTION
    # =====================================================

    print(
        "\nRating Distribution:"
    )

    print(
        product_metrics[
            "rating_distribution"
        ]
    )


    # =====================================================
    # SENTIMENT SUMMARY
    # =====================================================

    print(
        "\n========== SENTIMENT SUMMARY ==========\n"
    )

    sentiment_metrics = (
        results[
            "sentiment_metrics"
        ]
    )

    print(
        "Positive Reviews:",
        sentiment_metrics[
            "positive_count"
        ]
    )

    print(
        "Neutral Reviews:",
        sentiment_metrics[
            "neutral_count"
        ]
    )

    print(
        "Negative Reviews:",
        sentiment_metrics[
            "negative_count"
        ]
    )


    # =====================================================
    # SENTIMENT PERCENTAGES
    # =====================================================

    print(
        "\nPositive Percentage:",
        round(
            sentiment_metrics[
                "positive_percentage"
            ],
            2
        ),
        "%"
    )

    print(
        "Neutral Percentage:",
        round(
            sentiment_metrics[
                "neutral_percentage"
            ],
            2
        ),
        "%"
    )

    print(
        "Negative Percentage:",
        round(
            sentiment_metrics[
                "negative_percentage"
            ],
            2
        ),
        "%"
    )


    # =====================================================
    # PRODUCT STRENGTHS
    # =====================================================

    print(
        "\n========== PRODUCT STRENGTHS ==========\n"
    )

    strengths = results[
        "strengths"
    ]

    if strengths:

        for strength, count in strengths.items():

            print(
                f"{strength}: {count}"
            )

    else:

        print(
            "No significant strengths detected."
        )


    # =====================================================
    # PRODUCT WEAKNESSES
    # =====================================================

    print(
        "\n========== PRODUCT WEAKNESSES ==========\n"
    )

    weaknesses = results[
        "weaknesses"
    ]

    if weaknesses:

        for weakness, count in weaknesses.items():

            print(
                f"{weakness}: {count}"
            )

    else:

        print(
            "No significant weaknesses detected."
        )


    # =====================================================
    # RECOMMENDATIONS
    # =====================================================

    print(
        "\n========== REVIEWIQ RECOMMENDATIONS ==========\n"
    )

    recommendations = results[
        "recommendations"
    ]

    if recommendations:

        for recommendation in recommendations:

            print(
                f"Type: "
                f"{recommendation['type']}"
            )

            print(
                f"Category: "
                f"{recommendation['category']}"
            )

            print(
                f"Mentions: "
                f"{recommendation['mentions']}"
            )

            # Improvement recommendations
            # contain percentage information
            if (
                recommendation["type"]
                == "improvement"
            ):

                print(
                    "Negative Review Percentage: "
                    f"{recommendation['percentage']}%"
                )

            print(
                f"Priority: "
                f"{recommendation['priority']}"
            )

            print(
                f"Recommendation: "
                f"{recommendation['message']}"
            )

            print(
                "-" * 60
            )

    else:

        print(
            "No recommendations generated."
        )


    # =====================================================
    # SAMPLE PREDICTIONS
    # =====================================================

    print(
        "\n========== SAMPLE SENTIMENT PREDICTIONS ==========\n"
    )

    sample_data = results[
        "data"
    ].head(5)

    for _, row in sample_data.iterrows():

        print(
            "Review:",
            row["review_text"]
        )

        print(
            "Sentiment:",
            row["sentiment"]
        )

        print(
            "-" * 60
        )