from __future__ import annotations

from pathlib import Path

import streamlit as st

from data_helpers import (
    build_leaderboard_table,
    build_sentiment_chart_data,
    get_available_subreddits,
    load_leaderboard,
)
from ranking import RankingConfig

DATA_PATH = Path("./data/comments.db")


def render_dashboard(db_path: Path = DATA_PATH) -> None:
    st.set_page_config(
        page_title="AI Model Ranking Dashboard",
        page_icon="📊",
        layout="wide",
    )

    st.title("AI Model Ranking Dashboard")
    st.markdown(
        "Use this dashboard to explore community sentiment rankings for AI models derived from Reddit discussions. "
        "The leaderboard is generated from sentiment-weighted model mentions and engagement signals."
    )

    with st.sidebar:
        st.header("Filters")
        window = st.selectbox("Time window", ["30d", "all"], index=0)
        subreddits = get_available_subreddits(db_path)
        subreddit_options = ["All"] + subreddits
        subreddit = st.selectbox("Subreddit", subreddit_options)
        if subreddit == "All":
            subreddit = None
        limit = st.slider("Top models", min_value=1, max_value=20, value=10)
        st.markdown("---")
        st.write("Data source:")
        st.write(f"`{db_path}`")

    config = RankingConfig(min_support=1)
    leaderboard = load_leaderboard(
        window=window,
        subreddit=subreddit,
        limit=limit,
        db_path=db_path,
        config=config,
    )

    if not leaderboard:
        st.warning("No leaderboard data is available for the selected filters.")
        st.stop()

    st.subheader("Model Leaderboard")
    leaderboard_table = build_leaderboard_table(leaderboard)
    st.dataframe(leaderboard_table, use_container_width=True)

    chart_data = build_sentiment_chart_data(leaderboard)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Sentiment Distribution")
        st.bar_chart(chart_data)
    with col2:
        st.subheader("Methodology")
        st.markdown(
            "- Positive, neutral, and negative sentiment are derived from Phase 2 sentiment labels.\n"
            "- Each comment contribution is weighted by sentiment confidence, engagement, and subreddit bias.\n"
            "- The score shown in the leaderboard is a normalized weighted average per model.\n"
        )

    st.markdown("---")

    for model in leaderboard:
        with st.expander(f"{model['model_name']} — score: {model['score']:.4f}"):
            st.write(
                f"Support count: {model['support_count']} | "
                f"positive: {model['positive_count']}, negative: {model['negative_count']}, neutral: {model['neutral_count']}"
            )
            st.write("**Top supporting comments**")
            for comment in model["top_supporting_comments"]:
                st.markdown(
                    f"**{comment['subreddit']}** — {comment['sentiment_label'].title()} "
                    f"(score={comment['sentiment_score']:.2f}, contribution={comment['contribution']:.4f})"
                )
                st.caption(comment["comment_text"])

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "### Notes\n"
        "This dashboard is an MVP visualization built on the Phase 3 ranking engine. "
        "Filter by subreddit and time window to see how rankings change over the selected dataset."
    )


def main() -> None:
    render_dashboard(DATA_PATH)


if __name__ == "__main__":
    main()
