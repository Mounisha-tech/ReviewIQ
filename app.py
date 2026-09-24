import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
import html

from src.pipeline import run_reviewiq_pipeline


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="ReviewIQ | Seller Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def clean_display_text(text):
    """
    Remove accidental HTML/code formatting from generated
    recommendation text before displaying it.
    """

    if text is None:
        return ""

    text = str(text)

    # Remove fenced code blocks such as ```html ... ```
    text = re.sub(r"```(?:html|HTML|text|plaintext)?", "", text)
    text = text.replace("```", "")

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Convert HTML entities
    text = html.unescape(text)

    # Remove excessive whitespace
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

    return text.strip()


def safe_title(text):
    """Clean product/category names before displaying."""
    if text is None:
        return "Product"

    text = str(text)
    text = re.sub(r"<[^>]+>", "", text)

    return html.unescape(text).strip()


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL
       ===================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 78% 0%,
                rgba(45, 105, 175, 0.20),
                transparent 28%
            ),
            radial-gradient(
                circle at 10% 80%,
                rgba(35, 75, 130, 0.10),
                transparent 30%
            ),
            #080b11;

        color: #f5f7fa;
    }

    .main {
        background: transparent;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    section[data-testid="stSidebar"] {
        background: #0b1018;
        border-right: 1px solid #202936;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #ffffff;
    }


    /* =====================================================
       HEADER
       ===================================================== */

    .hero-title {
        font-size: 42px;
        font-weight: 750;
        letter-spacing: -1.5px;
        color: #ffffff;
        margin-bottom: 2px;
    }

    .hero-subtitle {
        color: #78879a;
        font-size: 14px;
        margin-bottom: 28px;
    }

    .product-title {
        font-size: 30px;
        font-weight: 700;
        color: #ffffff;
        margin-top: 5px;
        margin-bottom: 25px;
    }


    /* =====================================================
       SECTION TITLES
       ===================================================== */

    .section-title {
        font-size: 23px;
        font-weight: 700;
        color: #ffffff;
        margin-top: 25px;
        margin-bottom: 8px;
    }

    .section-subtitle {
        color: #758397;
        font-size: 13px;
        margin-bottom: 20px;
    }


    /* =====================================================
       KPI CARDS
       ===================================================== */

    .kpi-card {
        background:
            linear-gradient(
                145deg,
                rgba(27, 35, 48, 0.96),
                rgba(13, 18, 26, 0.98)
            );

        border: 1px solid #263142;
        border-radius: 16px;

        padding: 20px 22px;

        min-height: 120px;

        box-shadow:
            0 10px 35px rgba(0, 0, 0, 0.25);

        transition: all 0.2s ease;
    }

    .kpi-card:hover {
        border-color: #365c84;
        transform: translateY(-2px);
    }

    .kpi-label {
        color: #8592a4;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 10px;
    }

    .kpi-value {
        color: #ffffff;
        font-size: 31px;
        font-weight: 750;
        letter-spacing: -0.5px;
    }

    .kpi-icon {
        float: right;
        font-size: 19px;
        opacity: 0.8;
    }


    /* =====================================================
       PANELS
       ===================================================== */

    .dashboard-panel {
        background:
            linear-gradient(
                145deg,
                rgba(20, 27, 38, 0.96),
                rgba(11, 15, 22, 0.96)
            );

        border: 1px solid #242e3d;
        border-radius: 18px;

        padding: 22px;

        box-shadow:
            0 12px 40px rgba(0, 0, 0, 0.25);
    }


    /* =====================================================
       INSIGHT CARDS
       ===================================================== */

    .insight-card {
        background: #131a24;

        border: 1px solid #263140;

        border-radius: 12px;

        padding: 15px 18px;

        margin-bottom: 10px;

        display: flex;

        justify-content: space-between;

        align-items: center;
    }

    .strength-card {
        border-left: 3px solid #35e889;
    }

    .weakness-card {
        border-left: 3px solid #ff5c68;
    }

    .insight-name {
        color: #ffffff;
        font-size: 15px;
        font-weight: 600;
    }

    .insight-count {
        color: #7f8da0;
        font-size: 12px;
        margin-top: 3px;
    }


    /* =====================================================
       RECOMMENDATION CARDS
       ===================================================== */

    .recommendation-card {
        background:
            linear-gradient(
                145deg,
                #141b25,
                #10151d
            );

        border: 1px solid #273241;

        border-radius: 14px;

        padding: 18px 20px;

        margin-bottom: 12px;

        box-shadow:
            0 8px 25px rgba(0, 0, 0, 0.15);
    }

    .recommendation-title {
        color: #ffffff;
        font-size: 17px;
        font-weight: 650;
        margin-bottom: 7px;
    }

    .recommendation-text {
        color: #a7b1bf;
        font-size: 14px;
        line-height: 1.6;
    }

    .priority-high {
        color: #ff6874;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.8px;
    }

    .priority-medium {
        color: #f3c969;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.8px;
    }

    .priority-low {
        color: #52df9a;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.8px;
    }


    /* =====================================================
       BUTTON
       ===================================================== */

    .stButton > button {
        border-radius: 10px;

        border: 1px solid #315f8e;

        background:
            linear-gradient(
                135deg,
                #245c91,
                #1b4268
            );

        color: white;

        font-weight: 600;
    }

    .stButton > button:hover {
        border-color: #4c86bb;

        background:
            linear-gradient(
                135deg,
                #2b6da7,
                #245278
            );
    }


    /* =====================================================
       CHART CONTAINER
       ===================================================== */

    .chart-panel {
        background:
            linear-gradient(
                145deg,
                rgba(18, 24, 34, 0.95),
                rgba(10, 14, 21, 0.95)
            );

        border: 1px solid #222c39;

        border-radius: 18px;

        padding: 12px;

        box-shadow:
            0 10px 35px rgba(0, 0, 0, 0.20);
    }


    /* =====================================================
       FOOTER
       ===================================================== */

    .footer {
        text-align: center;

        color: #566274;

        font-size: 12px;

        padding: 25px 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="hero-title">📊 ReviewIQ</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="hero-subtitle">'
    'Intelligent Review Analysis System • Seller Analytics'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 📊 ReviewIQ")

    st.caption("Seller Analytics Dashboard")

    st.divider()

    st.markdown("### Upload Reviews")

    uploaded_file = st.file_uploader(
        "Upload a CSV file",
        type=["csv"],
        help="Upload a product review dataset in CSV format."
    )

    st.divider()

    st.markdown(
        """
        **V1 Analytics**

        • Product performance  
        • Sentiment analysis  
        • Rating analysis  
        • Product strengths  
        • Product weaknesses  
        • Recommendations
        """
    )


# =========================================================
# FILE UPLOAD
# =========================================================

if uploaded_file is None:

    st.markdown(
        """
        <div class="dashboard-panel">

        <h2 style="color:white;">
        Welcome to ReviewIQ
        </h2>

        <p style="color:#8d98a7;">
        Upload your product review dataset to generate
        seller-side analytics and actionable insights.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# =========================================================
# SAVE UPLOADED FILE
# =========================================================

temp_file = "data/uploaded_reviews.csv"

with open(temp_file, "wb") as file:

    file.write(
        uploaded_file.getbuffer()
    )


# =========================================================
# ANALYZE BUTTON
# =========================================================

st.markdown("")

if st.button(
    "🚀 Analyze Reviews",
    type="primary",
    use_container_width=True
):

    with st.spinner(
        "Processing reviews and generating insights..."
    ):

        try:

            results = run_reviewiq_pipeline(
                temp_file
            )

            st.session_state["results"] = results

            st.success(
                "Analysis completed successfully!"
            )

        except Exception as error:

            st.error(
                f"Error while processing dataset: {error}"
            )

            st.stop()


# =========================================================
# CHECK RESULTS
# =========================================================

if "results" not in st.session_state:

    st.info(
        "Click **Analyze Reviews** to generate seller insights."
    )

    st.stop()


results = st.session_state["results"]


# =========================================================
# GET ANALYTICS
# =========================================================

product_metrics = results["product_metrics"]

sentiment_metrics = results["sentiment_metrics"]


# =========================================================
# GET DATA
# =========================================================

data = None

if "data" in results:

    data = results["data"]

elif "df" in results:

    data = results["df"]


# =========================================================
# PRODUCT NAME
# =========================================================

product_name = "Product"

if (
    isinstance(data, pd.DataFrame)
    and "product_name" in data.columns
    and not data["product_name"].empty
):

    product_name = safe_title(
        data["product_name"].iloc[0]
    )


# =========================================================
# PRODUCT OVERVIEW
# =========================================================
# =========================================================
# PRODUCT OVERVIEW
# =========================================================

st.markdown("---")

st.markdown("## Product Overview")

st.caption(
    "A quick snapshot of the product's review performance."
)

# Product name
st.markdown(
    f"# {product_name}"
)


# =========================================================
# KPI VALUES
# =========================================================

total_reviews = product_metrics["total_reviews"]

average_rating = product_metrics["average_rating"]

positive_percentage = sentiment_metrics[
    "positive_percentage"
]

negative_percentage = sentiment_metrics[
    "negative_percentage"
]


# =========================================================
# KPI CARDS
# =========================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(
    4,
    gap="medium"
)


# =========================================================
# TOTAL REVIEWS
# =========================================================

with kpi1:

    with st.container(border=True):

        st.metric(
            label="💬 Total Reviews",
            value=f"{total_reviews:,}"
        )

        st.caption(
            "Reviews analyzed"
        )


# =========================================================
# AVERAGE RATING
# =========================================================

with kpi2:

    with st.container(border=True):

        st.metric(
            label="⭐ Average Rating",
            value=f"{average_rating:.2f} / 5"
        )

        st.caption(
            "Overall customer rating"
        )


# =========================================================
# POSITIVE REVIEWS
# =========================================================

with kpi3:

    with st.container(border=True):

        st.metric(
            label="🟢 Positive Reviews",
            value=f"{positive_percentage:.1f}%"
        )

        st.caption(
            f"{sentiment_metrics['positive_count']:,} reviews"
        )


# =========================================================
# NEGATIVE REVIEWS
# =========================================================

with kpi4:

    with st.container(border=True):

        st.metric(
            label="🔴 Negative Reviews",
            value=f"{negative_percentage:.1f}%"
        )

        st.caption(
            f"{sentiment_metrics['negative_count']:,} reviews"
        )

# =========================================================
# SENTIMENT ANALYSIS
# =========================================================
# =========================================================
# SENTIMENT ANALYSIS
# =========================================================

st.markdown("---")

st.markdown("## Sentiment Overview")

st.caption(
    "Customer sentiment across the analyzed reviews."
)


# =========================================================
# SENTIMENT DATA
# =========================================================

sentiment_counts = pd.Series({
    "Positive": sentiment_metrics["positive_count"],
    "Neutral": sentiment_metrics["neutral_count"],
    "Negative": sentiment_metrics["negative_count"]
})


# =========================================================
# DONUT CHART
# =========================================================

fig_sentiment = go.Figure(
    data=[
        go.Pie(
            labels=sentiment_counts.index,
            values=sentiment_counts.values,

            hole=0.68,

            textinfo="percent",

            textfont=dict(
                color="#ffffff",
                size=14
            ),

            marker=dict(
                colors=[
                    "#35E889",   # Positive
                    "#F2C94C",   # Neutral
                    "#FF5C68"    # Negative
                ],
                line=dict(
                    color="#090c12",
                    width=3
                )
            ),

            hovertemplate=(
                "<b>%{label}</b><br>"
                "%{value} reviews<br>"
                "%{percent}<extra></extra>"
            )
        )
    ]
)

fig_sentiment.update_layout(
    title=None,

    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",

    font=dict(
        color="#cbd5e1"
    ),

    legend=dict(
        orientation="h",
        y=-0.05,
        x=0.5,
        xanchor="center"
    ),

    margin=dict(
        l=10,
        r=10,
        t=10,
        b=30
    ),

    height=420,

    showlegend=True
)


# =========================================================
# SENTIMENT LAYOUT
# =========================================================

chart_col, breakdown_col = st.columns(
    [1.35, 1],
    gap="large"
)


# =========================================================
# CHART
# =========================================================

with chart_col:

    st.plotly_chart(
        fig_sentiment,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


# =========================================================
# SENTIMENT BREAKDOWN
# =========================================================

with breakdown_col:

    st.markdown("### Sentiment Breakdown")

    # -------------------------
    # POSITIVE
    # -------------------------

    st.markdown("#### 🟢 Positive")

    st.write(
        f"{sentiment_metrics['positive_count']:,} reviews "
        f"• {sentiment_metrics['positive_percentage']:.1f}%"
    )

    st.divider()


    # -------------------------
    # NEUTRAL
    # -------------------------

    st.markdown("#### 🟡 Neutral")

    st.write(
        f"{sentiment_metrics['neutral_count']:,} reviews "
        f"• {sentiment_metrics['neutral_percentage']:.1f}%"
    )

    st.divider()


    # -------------------------
    # NEGATIVE
    # -------------------------

    st.markdown("#### 🔴 Negative")

    st.write(
        f"{sentiment_metrics['negative_count']:,} reviews "
        f"• {sentiment_metrics['negative_percentage']:.1f}%"
    )


# =========================================================
# RATING ANALYSIS
# =========================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">Rating Analysis</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Distribution of customer ratings from 1 to 5 stars.'
    '</div>',
    unsafe_allow_html=True
)


rating_distribution = (
    product_metrics["rating_distribution"]
    .reindex(
        [1, 2, 3, 4, 5],
        fill_value=0
    )
)


# =========================================================
# RATING CHART
# =========================================================

fig_rating = go.Figure()


fig_rating.add_trace(
    go.Bar(

        x=["1 ★", "2 ★", "3 ★", "4 ★", "5 ★"],

        y=rating_distribution.values,

        text=rating_distribution.values,

        textposition="outside",

        textfont=dict(
            color="#dce7f5",
            size=13
        ),

        marker=dict(
            color=[
                "#ff5c68",
                "#ff7b72",
                "#f2c94c",
                "#72d89a",
                "#35e889"
            ],

            line=dict(
                width=0
            )
        ),

        hovertemplate=
            "<b>%{x}</b>"
            "<br>Reviews: %{y}"
            "<extra></extra>"
    )
)


fig_rating.update_layout(

    paper_bgcolor="rgba(0,0,0,0)",

    plot_bgcolor="rgba(0,0,0,0)",

    font=dict(
        color="#cbd5e1"
    ),

    xaxis=dict(

        title=None,

        showgrid=False,

        tickfont=dict(
            size=13
        )
    ),

    yaxis=dict(

        title="Number of Reviews",

        gridcolor="#252d39",

        zeroline=False
    ),

    margin=dict(
        l=20,
        r=20,
        t=25,
        b=20
    ),

    height=420,

    showlegend=False
)



st.plotly_chart(
    fig_rating,
    use_container_width=True,
    config={
        "displayModeBar": False
    }
)

st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# PRODUCT INSIGHTS
# =========================================================

st.markdown("---")

st.markdown("## Product Insights")

st.caption(
    "Key aspects customers appreciate and areas receiving negative feedback."
)

insights = results.get("insights", {})

strengths = insights.get("strengths", {})
weaknesses = insights.get("weaknesses", {})


# =========================================================
# TWO-COLUMN LAYOUT
# =========================================================

strength_col, weakness_col = st.columns(
    2,
    gap="large"
)


# =========================================================
# STRENGTHS
# =========================================================

with strength_col:

    st.markdown("### 💪 Strengths")

    if strengths:

        for category, count in strengths.items():

            category_name = str(category).title()
            count = int(count)

            with st.container(border=True):

                st.markdown(
                    f"### 🟢 {category_name}"
                )

                st.write(
                    f"**{count}** positive review(s) "
                    f"mention this aspect."
                )

                st.progress(
                    min(count / max(strengths.values()), 1.0)
                )

    else:

        st.info(
            "No significant strengths detected."
        )


# =========================================================
# AREAS OF CONCERN
# =========================================================

with weakness_col:

    st.markdown("### ⚠️ Areas of Concern")

    if weaknesses:

        for category, count in weaknesses.items():

            category_name = str(category).title()
            count = int(count)

            with st.container(border=True):

                st.markdown(
                    f"### 🔴 {category_name}"
                )

                st.write(
                    f"**{count}** negative review(s) "
                    f"mention this aspect."
                )

                st.progress(
                    min(count / max(weaknesses.values()), 1.0)
                )

    else:

        st.info(
            "No significant areas of concern detected."
        )

# =========================================================
# ACTIONABLE RECOMMENDATIONS
# =========================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">Actionable Recommendations</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Translate review patterns into practical product improvements.'
    '</div>',
    unsafe_allow_html=True
)

recommendations = results.get("recommendations", [])

if recommendations:

    improvement_recommendations = [
        r for r in recommendations
        if r.get("type") == "improvement"
    ]

    strength_recommendations = [
        r for r in recommendations
        if r.get("type") == "strength"
    ]

    # =====================================================
    # AREAS TO IMPROVE
    # =====================================================

    if improvement_recommendations:

        st.markdown("### ⚠️ Areas to Improve")

        for recommendation in improvement_recommendations:

            priority = recommendation.get(
                "priority",
                "Low"
            )

            category = recommendation.get(
                "category",
                "Unknown"
            )

            mentions = recommendation.get(
                "mentions",
                0
            )

            message = recommendation.get(
                "message",
                "No recommendation available."
            )

            # Remove accidental HTML if recommendation
            # generator contains HTML
            import re

            clean_message = re.sub(
                r"<[^>]+>",
                "",
                str(message)
            ).strip()

            clean_category = re.sub(
                r"<[^>]+>",
                "",
                str(category)
            ).strip()

            # Priority indicator
            if priority == "High":
                priority_icon = "🔴"
            elif priority == "Medium":
                priority_icon = "🟡"
            else:
                priority_icon = "🟢"

            # Native Streamlit container
            with st.container(border=True):

                st.markdown(
                    f"#### 🔧 {clean_category.title()}"
                )

                st.caption(
                    f"{priority_icon} "
                    f"{priority.upper()} PRIORITY "
                    f"• {mentions} negative review(s)"
                )

                st.write(
                    clean_message
                )


    # =====================================================
    # STRENGTHS TO MAINTAIN
    # =====================================================

    if strength_recommendations:

        st.markdown("### 💪 Strengths to Maintain")

        for recommendation in strength_recommendations:

            category = recommendation.get(
                "category",
                "Unknown"
            )

            mentions = recommendation.get(
                "mentions",
                0
            )

            message = recommendation.get(
                "message",
                "No recommendation available."
            )

            # Remove accidental HTML
            import re

            clean_message = re.sub(
                r"<[^>]+>",
                "",
                str(message)
            ).strip()

            clean_category = re.sub(
                r"<[^>]+>",
                "",
                str(category)
            ).strip()

            with st.container(border=True):

                st.markdown(
                    f"#### 🟢 {clean_category.title()}"
                )

                st.caption(
                    f"🟢 MAINTAIN "
                    f"• {mentions} positive review(s)"
                )

                st.write(
                    clean_message
                )

else:

    st.info(
        "No actionable recommendations were generated."
    )