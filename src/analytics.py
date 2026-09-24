import re
import pandas as pd


# =========================================================
# ISSUE KEYWORDS
# =========================================================

ISSUE_KEYWORDS = {

    "battery": [
        "battery",
        "charging",
        "charge",
        "backup"
    ],

    "quality": [
        "quality",
        "material",
        "build"
    ],

    "delivery": [
        "delivery",
        "shipping",
        "late",
        "package"
    ],

    "price": [
        "expensive",
        "costly",
        "price",
        "cost"
    ],

    "size": [
        "size",
        "fit",
        "fitting"
    ],

    "performance": [
        "slow",
        "performance",
        "speed"
    ],

    "durability": [
        "broke",
        "broken",
        "damaged",
        "durability"
    ]
}


# =========================================================
# STRENGTH KEYWORDS
# =========================================================

STRENGTH_KEYWORDS = {

    "battery": [
        "battery",
        "charging",
        "charge",
        "backup",
        "lasts"
    ],

    "quality": [
        "quality",
        "material",
        "build"
    ],

    "delivery": [
        "delivery",
        "shipping",
        "package"
    ],

    "design": [
        "design",
        "look",
        "looks",
        "appearance"
    ],

    "performance": [
        "performance",
        "speed",
        "fast",
        "quick"
    ],

    "value": [
        "value",
        "worth",
        "price"
    ]
}


# =========================================================
# RECOMMENDATION MESSAGES
# =========================================================

RECOMMENDATION_MESSAGES = {

    "battery": (
        "Review battery performance and investigate "
        "recurring battery or charging complaints."
    ),

    "quality": (
        "Investigate product material and build quality "
        "to reduce recurring quality complaints."
    ),

    "delivery": (
        "Review shipping and delivery processes to "
        "reduce late-delivery complaints."
    ),

    "price": (
        "Evaluate product pricing and perceived value "
        "against customer expectations."
    ),

    "size": (
        "Review product sizing and fit information "
        "to reduce sizing-related complaints."
    ),

    "performance": (
        "Investigate performance-related complaints "
        "and identify potential product improvements."
    ),

    "durability": (
        "Review product durability and investigate "
        "reports of damage or breakage."
    )
}


# =========================================================
# HELPER FUNCTION
# =========================================================

def contains_keyword(review, keyword):
    """
    Check whether a keyword appears as a complete word
    or phrase inside a review.
    """

    pattern = r"\b" + re.escape(keyword) + r"\b"

    return re.search(
        pattern,
        review,
        flags=re.IGNORECASE
    ) is not None


# =========================================================
# 1. PRODUCT PERFORMANCE METRICS
# =========================================================

def calculate_product_metrics(df):
    """
    Calculate basic product performance metrics.
    """

    total_reviews = len(df)

    average_rating = df["rating"].mean()

    rating_distribution = (
        df["rating"]
        .value_counts()
        .sort_index()
    )

    sentiment_distribution = (
        df["sentiment"]
        .value_counts()
    )

    sentiment_percentage = (
        df["sentiment"]
        .value_counts(normalize=True)
        * 100
    )

    return {
        "total_reviews": total_reviews,
        "average_rating": average_rating,
        "rating_distribution": rating_distribution,
        "sentiment_distribution": sentiment_distribution,
        "sentiment_percentage": sentiment_percentage
    }


# =========================================================
# 2. SENTIMENT ANALYTICS
# =========================================================

def calculate_sentiment_metrics(df):
    """
    Calculate detailed sentiment analytics.
    """

    sentiment_counts = (
        df["sentiment"]
        .value_counts()
    )

    sentiment_percentages = (
        df["sentiment"]
        .value_counts(normalize=True)
        * 100
    )

    positive_count = sentiment_counts.get(
        "positive",
        0
    )

    neutral_count = sentiment_counts.get(
        "neutral",
        0
    )

    negative_count = sentiment_counts.get(
        "negative",
        0
    )

    positive_percentage = sentiment_percentages.get(
        "positive",
        0
    )

    neutral_percentage = sentiment_percentages.get(
        "neutral",
        0
    )

    negative_percentage = sentiment_percentages.get(
        "negative",
        0
    )

    sentiment_average_rating = (
        df.groupby("sentiment")["rating"]
        .mean()
    )

    return {
        "positive_count": positive_count,
        "neutral_count": neutral_count,
        "negative_count": negative_count,

        "positive_percentage": positive_percentage,
        "neutral_percentage": neutral_percentage,
        "negative_percentage": negative_percentage,

        "sentiment_counts": sentiment_counts,
        "sentiment_percentages": sentiment_percentages,

        "sentiment_average_rating":
            sentiment_average_rating
    }


# =========================================================
# 3. NEGATIVE ISSUE ANALYSIS
# =========================================================

def analyze_negative_issues(df):
    """
    Identify common issues mentioned
    in negative reviews.
    """

    negative_reviews = df[
        df["sentiment"] == "negative"
    ]

    issue_counts = {}

    for review in negative_reviews["cleaned_review"]:

        review = str(review).lower()

        for issue, keywords in ISSUE_KEYWORDS.items():

            for keyword in keywords:

                if contains_keyword(
                    review,
                    keyword
                ):

                    issue_counts[issue] = (
                        issue_counts.get(issue, 0) + 1
                    )

                    # Count each issue only once
                    # per review
                    break

    # Sort issues by number of mentions
    issue_counts = dict(
        sorted(
            issue_counts.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )

    return issue_counts


# =========================================================
# 4. PRODUCT STRENGTH ANALYSIS
# =========================================================

def analyze_product_strengths(df):
    """
    Identify common strengths mentioned
    in positive reviews.
    """

    positive_reviews = df[
        df["sentiment"] == "positive"
    ]

    strength_counts = {}

    for review in positive_reviews["cleaned_review"]:

        review = str(review).lower()

        for strength, keywords in STRENGTH_KEYWORDS.items():

            for keyword in keywords:

                if contains_keyword(
                    review,
                    keyword
                ):

                    strength_counts[strength] = (
                        strength_counts.get(strength, 0) + 1
                    )

                    # Count each strength only once
                    # per review
                    break

    strength_counts = dict(
        sorted(
            strength_counts.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )

    return strength_counts


# =========================================================
# 5. STRENGTHS + WEAKNESSES
# =========================================================

def analyze_product_strengths_weaknesses(df):
    """
    Analyze both product strengths and weaknesses.
    """

    strengths = analyze_product_strengths(df)

    weaknesses = analyze_negative_issues(df)

    return {
        "strengths": strengths,
        "weaknesses": weaknesses
    }


# =========================================================
# 6. RECOMMENDATION ENGINE
# =========================================================

def generate_recommendations(
    strengths,
    weaknesses,
    total_negative_reviews
):
    """
    Generate actionable recommendations
    based on product strengths and weaknesses.

    Priority is determined using the percentage
    of negative reviews mentioning each issue.
    """

    recommendations = []

    # -----------------------------------------------------
    # Recommendations based on weaknesses
    # -----------------------------------------------------

    for issue, count in weaknesses.items():

        # Calculate percentage of negative reviews
        # mentioning this issue
        if total_negative_reviews > 0:

            percentage = (
                count /
                total_negative_reviews
            ) * 100

        else:

            percentage = 0

        # Determine priority
        if percentage >= 10:

            priority = "High"

        elif percentage >= 5:

            priority = "Medium"

        else:

            priority = "Low"

        message = RECOMMENDATION_MESSAGES.get(
            issue,

            (
                f"Investigate and improve {issue}. "
                f"{count} negative reviews mention "
                f"this issue."
            )
        )

        recommendation = {

            "type": "improvement",

            "category": issue,

            "mentions": count,

            "percentage": round(
                percentage,
                2
            ),

            "priority": priority,

            "message": message
        }

        recommendations.append(
            recommendation
        )

    # -----------------------------------------------------
    # Recommendations based on strengths
    # -----------------------------------------------------

    for strength, count in strengths.items():

        recommendation = {

            "type": "strength",

            "category": strength,

            "mentions": count,

            "priority": "Maintain",

            "message": (
                f"Maintain the current {strength} "
                f"performance. "
                f"{count} positive reviews mention "
                f"this aspect."
            )
        }

        recommendations.append(
            recommendation
        )

    return recommendations


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    test_data = {

        "rating": [
            5,
            5,
            4,
            2,
            1,
            2
        ],

        "sentiment": [
            "positive",
            "positive",
            "positive",
            "negative",
            "negative",
            "negative"
        ],

        "cleaned_review": [

            "excellent battery backup",

            "great battery life",

            "beautiful design and fast performance",

            "poor build quality",

            "material quality is terrible",

            "battery is bad and product broke"
        ]
    }

    # Create DataFrame
    df = pd.DataFrame(test_data)

    # -----------------------------------------------------
    # Product metrics
    # -----------------------------------------------------

    product_metrics = calculate_product_metrics(
        df
    )

    # -----------------------------------------------------
    # Sentiment metrics
    # -----------------------------------------------------

    sentiment_metrics = calculate_sentiment_metrics(
        df
    )

    # -----------------------------------------------------
    # Strengths and weaknesses
    # -----------------------------------------------------

    insights = analyze_product_strengths_weaknesses(
        df
    )

    # -----------------------------------------------------
    # Total negative reviews
    # -----------------------------------------------------

    total_negative_reviews = (
        sentiment_metrics["negative_count"]
    )

    # -----------------------------------------------------
    # Recommendations
    # -----------------------------------------------------

    recommendations = generate_recommendations(

        insights["strengths"],

        insights["weaknesses"],

        total_negative_reviews
    )

    # =====================================================
    # PRINT RESULTS
    # =====================================================

    print(
        "\n========== ReviewIQ Product Analytics ==========\n"
    )

    print("Total Reviews:")

    print(
        product_metrics["total_reviews"]
    )

    print("\nAverage Rating:")

    print(
        product_metrics["average_rating"]
    )

    print("\nRating Distribution:")

    print(
        product_metrics["rating_distribution"]
    )

    print(
        "\n\n========== Sentiment Analytics ==========\n"
    )

    print("Positive Reviews:")

    print(
        sentiment_metrics["positive_count"]
    )

    print("Neutral Reviews:")

    print(
        sentiment_metrics["neutral_count"]
    )

    print("Negative Reviews:")

    print(
        sentiment_metrics["negative_count"]
    )

    print("\nPositive Percentage:")

    print(
        sentiment_metrics["positive_percentage"]
    )

    print("\nNeutral Percentage:")

    print(
        sentiment_metrics["neutral_percentage"]
    )

    print("\nNegative Percentage:")

    print(
        sentiment_metrics["negative_percentage"]
    )

    print(
        "\nAverage Rating by Sentiment:"
    )

    print(
        sentiment_metrics[
            "sentiment_average_rating"
        ]
    )

    print(
        "\n\n========== Product Strengths ==========\n"
    )

    for strength, count in insights["strengths"].items():

        print(
            f"{strength}: {count}"
        )

    print(
        "\n\n========== Product Weaknesses ==========\n"
    )

    for weakness, count in insights["weaknesses"].items():

        print(
            f"{weakness}: {count}"
        )

    print(
        "\n\n========== ReviewIQ Recommendations ==========\n"
    )

    for recommendation in recommendations:

        print(
            f"Type: {recommendation['type']}"
        )

        print(
            f"Category: {recommendation['category']}"
        )

        print(
            f"Mentions: {recommendation['mentions']}"
        )

        # Show percentage only for improvements
        if recommendation["type"] == "improvement":

            print(
                f"Negative Review Percentage: "
                f"{recommendation['percentage']}%"
            )

        print(
            f"Priority: {recommendation['priority']}"
        )

        print(
            f"Recommendation: "
            f"{recommendation['message']}"
        )

        print("-" * 50)