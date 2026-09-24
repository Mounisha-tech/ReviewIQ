import re

import nltk

from bs4 import BeautifulSoup

from nltk.corpus import stopwords


# =========================================================
# DOWNLOAD NLTK STOPWORDS
# =========================================================

nltk.download("stopwords", quiet=True)


# =========================================================
# STOPWORDS
# =========================================================

STOP_WORDS = set(
    stopwords.words("english")
)


# Words that are important for sentiment analysis
# and should NOT be removed.

NEGATION_WORDS = {

    "no",
    "not",
    "never",
    "neither",
    "nor",
    "cannot",

    "can't",
    "don't",
    "doesn't",
    "didn't",
    "isn't",
    "wasn't",
    "weren't",
    "won't",
    "wouldn't",
    "shouldn't",
    "couldn't"
}


# =========================================================
# CONTRACTIONS
# =========================================================

CONTRACTIONS = {

    "don't": "do not",
    "doesn't": "does not",
    "didn't": "did not",
    "isn't": "is not",
    "wasn't": "was not",
    "weren't": "were not",
    "can't": "cannot",
    "couldn't": "could not",
    "shouldn't": "should not",
    "wouldn't": "would not",
    "won't": "will not",
    "haven't": "have not",
    "hasn't": "has not",
    "hadn't": "had not"
}


# Remove negation words from the stopword list
# so that they are preserved.

STOP_WORDS = STOP_WORDS - NEGATION_WORDS


# =========================================================
# TEXT CLEANING
# =========================================================

def clean_text(text):
    """
    Clean a single review for NLP processing.
    """

    # 1. Handle missing values

    if text is None:
        return ""


    # 2. Convert to string

    text = str(text)


    # 3. Convert to lowercase

    text = text.lower()


    # 4. Expand contractions

    for contraction, expanded_form in CONTRACTIONS.items():

        text = text.replace(
            contraction,
            expanded_form
        )


    # 5. Remove HTML

    text = BeautifulSoup(
        text,
        "html.parser"
    ).get_text()


    # 6. Remove URLs

    text = re.sub(
        r"http\S+|www\S+",
        "",
        text
    )


    # 7. Remove punctuation and special characters

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )


    # 8. Normalize whitespace

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()


    # 9. Remove stopwords

    words = text.split()

    words = [
        word
        for word in words
        if word not in STOP_WORDS
    ]


    # 10. Convert words back into a sentence

    text = " ".join(words)

    return text


# =========================================================
# TESTING
# =========================================================

if __name__ == "__main__":

    test_reviews = [

        "THIS product is AMAZING!!! 😍",

        "<p>Very good product</p>",

        "Terrible!!! Check https://example.com",

        "This     product     is     okay.",

        "This is a very good product",

        "This product is not good",

        "I don't like this product",

        "I never buy products like this"
    ]


    print(
        "\n========== ReviewIQ NLP Preprocessing ==========\n"
    )


    for review in test_reviews:

        cleaned_review = clean_text(review)

        print("Original:")
        print(review)

        print("\nCleaned:")
        print(cleaned_review)

        print("\n" + "-" * 50)