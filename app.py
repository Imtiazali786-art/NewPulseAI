import os
import re
import html

import streamlit as st
import feedparser

from dotenv import load_dotenv
from groq import Groq


# ==========================================
# PAGE SETTINGS
# ==========================================

st.set_page_config(
    page_title="NewPulse AI",
    page_icon="📰",
    layout="wide"
)


# ==========================================
# LOAD API KEY
# ==========================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY not found in .env file.")
    st.stop()

client = Groq(api_key=api_key)
# ==========================================
# FAVORITES
# ==========================================

if "favorites" not in st.session_state:
    st.session_state.favorites = []

# ==========================================
# HEADER
# ==========================================

st.title("📰 NewPulse AI")
st.subheader("Latest News + AI-Powered Summaries")

st.write(
    "Discover the latest news and understand important stories with AI."
)

st.divider()


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("⚙️ News Settings")

category = st.sidebar.selectbox(
    "🗂️ Choose Category",
    [
        "Top News",
        "Pakistan",
        "Technology",
        "Business",
        "Sports",
        "Entertainment",
        "Science",
        "Health"
    ]
)

number_of_articles = st.sidebar.slider(
    "📰 Number of Articles",
    3,
    10,
    5
)

summary_language = st.sidebar.selectbox(
    "🌐 AI Summary Language",
    ["English", "Urdu"]
)

st.sidebar.divider()

st.sidebar.info(
    "📰 News Source: Google News RSS\n\n"
    "🤖 AI: Groq"
)


# ==========================================
# NEWS URLS
# ==========================================

category_urls = {

    "Top News":
        "https://news.google.com/rss?hl=en-PK&gl=PK&ceid=PK:en",

    "Pakistan":
        "https://news.google.com/rss/search?q=Pakistan&hl=en-PK&gl=PK&ceid=PK:en",

    "Technology":
        "https://news.google.com/rss/search?q=technology&hl=en-PK&gl=PK&ceid=PK:en",

    "Business":
        "https://news.google.com/rss/search?q=business&hl=en-PK&gl=PK&ceid=PK:en",

    "Sports":
        "https://news.google.com/rss/search?q=sports&hl=en-PK&gl=PK&ceid=PK:en",

    "Entertainment":
        "https://news.google.com/rss/search?q=entertainment&hl=en-PK&gl=PK&ceid=PK:en",

    "Science":
        "https://news.google.com/rss/search?q=science&hl=en-PK&gl=PK&ceid=PK:en",

    "Health":
        "https://news.google.com/rss/search?q=health&hl=en-PK&gl=PK&ceid=PK:en"
}

news_url = category_urls[category]


# ==========================================
# SEARCH
# ==========================================

search = st.text_input(
    "🔍 Search News",
    placeholder="Search for AI, Pakistan, technology..."
)


# ==========================================
# LOAD NEWS
# ==========================================

with st.spinner("Loading latest news..."):

    feed = feedparser.parse(news_url)


if not feed.entries:

    st.error("No news articles found.")

    st.stop()


articles = feed.entries


# ==========================================
# SEARCH FILTER
# ==========================================

if search.strip():

    search_text = search.lower()

    articles = [

        article

        for article in articles

        if search_text in article.get(
            "title",
            ""
        ).lower()

        or search_text in article.get(
            "summary",
            ""
        ).lower()

    ]


# ==========================================
# RESULTS MESSAGE
# ==========================================

if search.strip():

    st.success(
        f"🔍 Search results for: {search}"
    )

else:

    st.success(
        f"📰 Latest {category} News"
    )


# ==========================================
# NEWS CONTEXT FOR AI
# ==========================================

news_context = ""


# ==========================================
# DISPLAY NEWS
# ==========================================

if not articles:

    st.warning(
        "No matching news found. Try another search."
    )

else:

    for index, article in enumerate(
        articles[:number_of_articles],
        start=1
    ):

        # ----------------------------------
        # TITLE
        # ----------------------------------

        title = article.get(
            "title",
            "Untitled News"
        )

        # ----------------------------------
        # LINK
        # ----------------------------------

        link = article.get(
            "link",
            "#"
        )

        # ----------------------------------
        # SOURCE
        # ----------------------------------

        source = article.get(
            "source",
            {}
        )

        if isinstance(source, dict):

            source_name = source.get(
                "title",
                "Google News"
            )

        else:

            source_name = "Google News"

        # ----------------------------------
        # TIME
        # ----------------------------------

        published_time = article.get(
            "published",
            "Time not available"
        )

        # ----------------------------------
        # SUMMARY
        # ----------------------------------

        raw_summary = article.get(
            "summary",
            "No description available."
        )

        # Remove HTML
        clean_summary = re.sub(
            r"<[^>]*>",
            " ",
            raw_summary
        )

        # Decode HTML characters
        clean_summary = html.unescape(
            clean_summary
        )

        # Remove extra spaces
        clean_summary = " ".join(
            clean_summary.split()
        )

        # ----------------------------------
        # AI NEWS CONTEXT
        # ----------------------------------

        news_context += (
            f"\nTITLE: {title}\n"
            f"SUMMARY: {clean_summary}\n"
        )

        # ----------------------------------
        # NEWS CARD
        # ----------------------------------
        with st.container(border=True):

            st.markdown(
                f"### 📰 {index}. {title}"
            )

            st.caption(
                f"🏢 {source_name} | 🕐 {published_time}"
            )

            st.write(
                clean_summary
            )
        # ----------------------------------
        # BUTTONS
        # ----------------------------------

        col1, col2, col3 = st.columns(3)

with col1:

    if st.button(
        "🤖 Summarize with AI",
        key=f"summary_{index}"
    ):

        with st.spinner(
            "AI is preparing the summary..."
        ):

            try:

                if summary_language == "Urdu":

                    language_instruction = (
                        "Write the summary in simple Urdu. "
                        "Use exactly 3 short bullet points."
                    )

                else:

                    language_instruction = (
                        "Write the summary in clear English. "
                        "Use exactly 3 short bullet points."
                    )

                response = client.chat.completions.create(

                    model="openai/gpt-oss-20b",

                    messages=[

                        {
                            "role": "system",
                            "content": (
                                "You are a professional news assistant. "
                                "Summarize only the information provided. "
                                "Do not invent facts. "
                                + language_instruction
                            )
                        },

                        {
                            "role": "user",
                            "content": (
                                f"News Title: {title}\n\n"
                                f"News Content: {clean_summary}"
                            )
                        }

                    ],

                    temperature=0.3
                )

                st.info(
                    response.choices[0].message.content
                )

            except Exception as e:

                st.error(
                    f"AI summary error: {e}"
                )


with col2:

    st.link_button(
        "🔗 Read Full News",
        link
    )


with col3:

    if st.button(
        "⭐ Favorite",
        key=f"favorite_{index}"
    ):

        favorite = {
            "title": title,
            "link": link,
            "source": source_name
        }

        if favorite not in st.session_state.favorites:

            st.session_state.favorites.append(
                favorite
            )

            st.success("⭐ Added to Favorites!")

        else:

            st.info("Already in Favorites!")

        
            with st.spinner(
                    "AI is preparing the summary..."
                ):

                    try:

                        if summary_language == "Urdu":

                            language_instruction = (
                                "Write the summary in simple Urdu. "
                                "Use exactly 3 short bullet points."
                            )

                        else:

                            language_instruction = (
                                "Write the summary in clear English. "
                                "Use exactly 3 short bullet points."
                            )

                        response = client.chat.completions.create(

                            model="openai/gpt-oss-20b",

                            messages=[

                                {
                                    "role": "system",
                                    "content": (
                                        "You are a professional news assistant. "
                                        "Summarize only the information provided. "
                                        "Do not invent facts. "
                                        + language_instruction
                                    )
                                },

                                {
                                    "role": "user",
                                    "content": (
                                        f"News Title: {title}\n\n"
                                        f"News Content: {clean_summary}"
                                    )
                                }

                            ],

                            temperature=0.3
                        )

                        st.info(
                            response.choices[
                                0
                            ].message.content
                        )

                    except Exception as e:

                        st.error(
                            f"AI summary error: {e}"
                        )

        with col2:

            st.link_button(
                "🔗 Read Full News",
                link
            )

        st.divider()


# ==========================================
# AI NEWS ASSISTANT
# ==========================================

st.header("🤖 AI News Assistant")

st.write(
    "Ask questions about the news currently displayed above."
)

user_question = st.text_input(
    "💬 Ask about these news stories",
    placeholder="Example: Explain the latest news in simple words"
)


if st.button(
    "🚀 Ask AI",
    key="news_assistant"
):

    if not user_question.strip():

        st.warning(
            "Please type a question first."
        )

    else:

        with st.spinner(
            "AI is reading the news..."
        ):

            try:

                response = client.chat.completions.create(

                    model="openai/gpt-oss-20b",

                    messages=[

                        {
                            "role": "system",
                            "content": (
                                "You are NewPulse AI, a helpful news assistant. "
                                "Answer using only the provided news context. "
                                "Keep the answer clear and simple. "
                                "Do not invent facts."
                            )
                        },

                        {
                            "role": "user",
                            "content": (
                                f"AVAILABLE NEWS:\n"
                                f"{news_context}\n\n"
                                f"USER QUESTION:\n"
                                f"{user_question}"
                            )
                        }

                    ],

                    temperature=0.3
                )

                st.success(
                    "🤖 AI Answer"
                )

                st.write(
                    response.choices[
                        0
                    ].message.content
                )

            except Exception as e:

                st.error(
                    f"AI assistant error: {e}"
                )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "NewPulse AI • News Discovery + AI Summaries + AI Assistant"
)