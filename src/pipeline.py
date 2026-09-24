import pandas as pd

from .data_processing import process_reviews
from .preprocessing import clean_text
from .sentiment import (
    load_sentiment_model,
    predict_sentiment
)

from .analytics import (
    calculate_product_metrics,
    calculate_sentiment_metrics,
    analyze_product_strengths_weaknesses,
    generate_recommendations
)


# =========================================================
# COMPLETE REVIEWIQ PIPELINE
# =========================================================

def run_reviewiq_pipeline(file_path):
    """
    Run the complete ReviewIQ seller analytics pipeline.

    Flow:

    CSV
      ↓
    Data Processing
      ↓
    Text Cleaning
      ↓
    Sentiment Prediction
      ↓
    Product Metrics
      ↓
    Sentiment Metrics
      ↓
    Strengths & Weaknesses
      ↓
    Recommendations
    """

    print("\n========== ReviewIQ Pipeline ==========\n")

    # =====================================================
    # 1. LOAD + VALIDATE DATA
    # =====================================================

    print("1. Loading dataset...")

    df, quality_report = process_reviews(
        file_path
    )

    print(
        f"   Loaded {len(df)} reviews."
    )

    # =====================================================
    # 2. CLEAN REVIEW TEXT
    # =====================================================

    print("\n2. Cleaning review text...")

    df = df.copy()

    df["cleaned_review"] = (
        df["review_text"]
        .fillna("")
        .apply(clean_text)
    )

    print(
        "   Text preprocessing completed."
    )

    # =====================================================
    # 3. LOAD TRAINED SENTIMENT MODEL
    # =====================================================

    print("\n3. Loading sentiment model...")

    model, vectorizer = load_sentiment_model()

    print(
        "   Sentiment model loaded."
    )

    # =====================================================
    # 4. PREDICT SENTIMENT
    # =====================================================

    print("\n4. Predicting sentiment...")

    df["sentiment"] = df[
        "cleaned_review"
    ].apply(
        lambda review: predict_sentiment(
            review,
            model,
            vectorizer
        )
    )

    print(
        "   Sentiment prediction completed."
    )

    # =====================================================
    # 5. CALCULATE PRODUCT METRICS
    # =====================================================

    print(
        "\n5. Calculating product metrics..."
    )

    product_metrics = calculate_product_metrics(
        df
    )

    print(
        "   Product metrics calculated."
    )

    # =====================================================
    # 6. CALCULATE SENTIMENT METRICS
    # =====================================================

    print(
        "\n6. Calculating sentiment metrics..."
    )

    sentiment_metrics = calculate_sentiment_metrics(
        df
    )

    print(
        "   Sentiment metrics calculated."
    )

    # =====================================================
    # 7. ANALYZE STRENGTHS + WEAKNESSES
    # =====================================================

    print(
        "\n7. Analyzing product strengths and weaknesses..."
    )

    insights = analyze_product_strengths_weaknesses(
        df
    )

    print(
        "   Product insights generated."
    )

    # =====================================================
    # 8. GENERATE RECOMMENDATIONS
    # =====================================================

    print(
        "\n8. Generating recommendations..."
    )

    recommendations = generate_recommendations(
        insights["strengths"],
        insights["weaknesses"],
        sentiment_metrics["negative_count"]
    )

    print(
        "   Recommendations generated."
    )

    # =====================================================
    # 9. RETURN ALL RESULTS
    # =====================================================

    print(
        "\n9. ReviewIQ pipeline completed successfully."
    )

    return {
        # Processed dataset
        "data": df,

        # Data quality information
        "quality_report": quality_report,

        # Product-level metrics
        "product_metrics": product_metrics,

        # Sentiment-level metrics
        "sentiment_metrics": sentiment_metrics,

        # Product strengths + weaknesses
        "insights": insights,

        # Seller recommendations
        "recommendations": recommendations
    }


# =========================================================
# DIRECT PIPELINE TEST
# =========================================================

if __name__ == "__main__":

    results = run_reviewiq_pipeline(
        "data/amazon_reviews.csv"
    )

    print(
        "\n========== PIPELINE TEST ==========\n"
    )

    # -----------------------------------------------------
    # Product Metrics
    # -----------------------------------------------------

    print("Total Reviews:")

    print(
        results["product_metrics"][
            "total_reviews"
        ]
    )

    print("\nAverage Rating:")

    print(
        results["product_metrics"][
            "average_rating"
        ]
    )

    # -----------------------------------------------------
    # Sentiment Metrics
    # -----------------------------------------------------

    print("\nPositive Reviews:")

    print(
        results["sentiment_metrics"][
            "positive_count"
        ]
    )

    print("\nNeutral Reviews:")

    print(
        results["sentiment_metrics"][
            "neutral_count"
        ]
    )

    print("\nNegative Reviews:")

    print(
        results["sentiment_metrics"][
            "negative_count"
        ]
    )

    # -----------------------------------------------------
    # Strengths
    # -----------------------------------------------------

    print("\nProduct Strengths:")

    print(
        results["insights"]["strengths"]
    )

    # -----------------------------------------------------
    # Weaknesses
    # -----------------------------------------------------

    print("\nProduct Weaknesses:")

    print(
        results["insights"]["weaknesses"]
    )

    # -----------------------------------------------------
    # Recommendations
    # -----------------------------------------------------

    print("\nRecommendations:")

    for recommendation in results[
        "recommendations"
    ]:

        print(
            recommendation
        )

    print(
        "\n===================================="
    )