import os
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

from .data_processing import process_reviews
from .preprocessing import clean_text


# ---------------------------------------------------------
# Create Sentiment Label
# ---------------------------------------------------------

def create_sentiment_label(rating):
    """
    Convert a product rating into a sentiment label.
    """

    if rating <= 2:
        return "negative"
    elif rating == 3:
        return "neutral"
    else:
        return "positive"


# ---------------------------------------------------------
# Add Sentiment Labels
# ---------------------------------------------------------

def add_sentiment_labels(df):
    """
    Add a sentiment column based on product ratings.
    """

    df = df.copy()

    df["sentiment"] = df["rating"].apply(
        create_sentiment_label
    )

    return df


# ---------------------------------------------------------
# Train/Test Split
# ---------------------------------------------------------

def split_data(df):
    """
    Split review data into training and testing sets.
    """

    X = df["cleaned_review"]
    y = df["sentiment"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    return X_train, X_test, y_train, y_test


# ---------------------------------------------------------
# TF-IDF
# ---------------------------------------------------------

def create_tfidf_features(train_text, test_text):
    """
    Convert review text into TF-IDF numerical features.
    """

    vectorizer = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95
    )

    X_train = vectorizer.fit_transform(train_text)

    X_test = vectorizer.transform(test_text)

    return X_train, X_test, vectorizer


# ---------------------------------------------------------
# Train Logistic Regression Model
# ---------------------------------------------------------

def train_sentiment_model(X_train, y_train):
    """
    Train Logistic Regression using TF-IDF features.

    class_weight='balanced' helps handle the
    imbalance in the sentiment classes.
    """

    model = LogisticRegression(
        max_iter=1000,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(
        X_train,
        y_train
    )

    return model


# ---------------------------------------------------------
# Evaluate Model
# ---------------------------------------------------------

def evaluate_model(model, X_test, y_test):
    """
    Evaluate the sentiment classification model.
    """

    y_pred = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    report = classification_report(
        y_test,
        y_pred,
        zero_division=0
    )

    matrix = confusion_matrix(
        y_test,
        y_pred
    )

    return accuracy, report, matrix


# ---------------------------------------------------------
# Save Model
# ---------------------------------------------------------

def save_model(model, vectorizer):
    """
    Save the trained model and TF-IDF vectorizer.
    """

    os.makedirs("models", exist_ok=True)

    joblib.dump(
        model,
        "models/sentiment_model.pkl"
    )

    joblib.dump(
        vectorizer,
        "models/tfidf_vectorizer.pkl"
    )

    print("\nModel and vectorizer saved successfully.")


# ---------------------------------------------------------
# Load Model
# ---------------------------------------------------------

def load_sentiment_model():
    """
    Load the trained sentiment model
    and TF-IDF vectorizer.
    """

    model = joblib.load(
        "models/sentiment_model.pkl"
    )

    vectorizer = joblib.load(
        "models/tfidf_vectorizer.pkl"
    )

    return model, vectorizer


# ---------------------------------------------------------
# Predict Sentiment
# ---------------------------------------------------------

def predict_sentiment(review, model, vectorizer):
    """
    Predict sentiment for a single review.
    """

    review_vector = vectorizer.transform(
        [review]
    )

    prediction = model.predict(
        review_vector
    )

    return prediction[0]


# ---------------------------------------------------------
# Train Complete Sentiment Pipeline
# ---------------------------------------------------------

def train_pipeline():
    """
    Complete ReviewIQ sentiment training pipeline.
    """

    print("\n==========================================")
    print(" ReviewIQ Sentiment Model Training")
    print("==========================================\n")

    # -----------------------------------------------------
    # 1. Load and process dataset
    # -----------------------------------------------------

    print("1. Loading dataset...")

    df, quality_report = process_reviews(
        "data/amazon_reviews.csv"
    )

    print("Dataset loaded.")
    print("Number of reviews:", len(df))

    # -----------------------------------------------------
    # 2. Clean review text
    # -----------------------------------------------------

    print("\n2. Cleaning review text...")

    df["cleaned_review"] = df["review_text"].apply(
        clean_text
    )

    # Remove reviews with no meaningful text
    df = df[
        df["cleaned_review"].str.strip() != ""
    ].copy()

    print(
        "Reviews after cleaning:",
        len(df)
    )

    # -----------------------------------------------------
    # 3. Create sentiment labels
    # -----------------------------------------------------

    print("\n3. Creating sentiment labels...")

    df = add_sentiment_labels(df)

    print("\nSentiment distribution:")

    print(
        df["sentiment"].value_counts()
    )

    # -----------------------------------------------------
    # 4. Split dataset
    # -----------------------------------------------------

    print("\n4. Splitting dataset...")

    X_train, X_test, y_train, y_test = split_data(
        df
    )

    print(
        "Training reviews:",
        len(X_train)
    )

    print(
        "Testing reviews:",
        len(X_test)
    )

    # -----------------------------------------------------
    # 5. Create TF-IDF features
    # -----------------------------------------------------

    print("\n5. Creating TF-IDF features...")

    X_train_tfidf, X_test_tfidf, vectorizer = (
        create_tfidf_features(
            X_train,
            X_test
        )
    )

    print(
        "Training TF-IDF shape:",
        X_train_tfidf.shape
    )

    print(
        "Testing TF-IDF shape:",
        X_test_tfidf.shape
    )

    # -----------------------------------------------------
    # 6. Train Logistic Regression
    # -----------------------------------------------------

    print("\n6. Training Logistic Regression...")

    model = train_sentiment_model(
        X_train_tfidf,
        y_train
    )

    print("Model training completed.")

    # -----------------------------------------------------
    # 7. Evaluate model
    # -----------------------------------------------------

    print("\n7. Evaluating model...")

    accuracy, report, matrix = evaluate_model(
        model,
        X_test_tfidf,
        y_test
    )

    print("\n========== MODEL EVALUATION ==========\n")

    print(
        "Accuracy:",
        accuracy
    )

    print("\nClassification Report:")
    print(report)

    print("\nConfusion Matrix:")
    print(matrix)

    # -----------------------------------------------------
    # 8. Save model
    # -----------------------------------------------------

    print("\n8. Saving model...")

    save_model(
        model,
        vectorizer
    )

    return model, vectorizer


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":

    model, vectorizer = train_pipeline()

    # -----------------------------------------------------
    # Test predictions
    # -----------------------------------------------------

    test_reviews = [
        "This product is amazing",
        "This product is terrible",
        "The product is okay",
        "Excellent quality and very useful",
        "Worst product I have ever bought"
    ]

    print(
        "\n========== PREDICTION TEST ==========\n"
    )

    for review in test_reviews:

        sentiment = predict_sentiment(
            review,
            model,
            vectorizer
        )

        print(
            "Review:",
            review
        )

        print(
            "Predicted sentiment:",
            sentiment
        )

        print("-" * 50)