import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz
import re
import html
from pathlib import Path


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="FAQ Knowledge Studio",
    page_icon="✦",
    layout="wide"
)


# --------------------------------------------------
# LOAD CUSTOM CSS
# --------------------------------------------------

css_file = Path("style.css")
if not css_file.exists():
    css_file = Path("styles.css")

if css_file.exists():
    with open(css_file, encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

# --------------------------------------------------
# LOAD FAQ DATA
# --------------------------------------------------

try:
    faq_data = pd.read_csv("faq.csv")
except FileNotFoundError:
    st.error("❌ faq.csv file not found.")
    st.stop()

required_columns = ["Question", "Answer", "Category"]

if not all(col in faq_data.columns for col in required_columns):
    st.error("faq.csv must contain Question, Answer and Category columns.")
    st.stop()

faq_data["Question"] = (
    faq_data["Question"]
    .astype(str)
    .str.strip()
)

faq_data["Answer"] = (
    faq_data["Answer"]
    .astype(str)
    .str.strip()
)

faq_data["Category"] = (
    faq_data["Category"]
    .astype(str)
    .str.strip()
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "questions_asked" not in st.session_state:
    st.session_state.questions_asked = 0

if "answers_found" not in st.session_state:
    st.session_state.answers_found = 0

if "questions_not_found" not in st.session_state:
    st.session_state.questions_not_found = 0

if "selected_category" not in st.session_state:
    st.session_state.selected_category = "All Categories"


# --------------------------------------------------
# WELCOME MESSAGE
# --------------------------------------------------

welcome_message = {
    "role": "assistant",
    "content": (
        "Hello. I’m your FAQ Knowledge Studio assistant. "
        "Ask a question and I’ll guide you to the most useful answer in the workspace."
    )
}

if not st.session_state.messages:
    st.session_state.messages = [welcome_message]


# --------------------------------------------------
# FAQ CATEGORIES
# --------------------------------------------------

categories = [
    "All Categories"
] + sorted(
    faq_data["Category"].unique().tolist()
)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown(
        '<div class="sidebar-shell">'
        '<div class="sidebar-brand">FAQ Knowledge Studio</div>'
        '<div class="sidebar-copy">A refined workspace for asking, discovering, and understanding your FAQ library.</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-panel">'
        '<div class="sidebar-section">Workspace controls</div>'
        '<div class="sidebar-line">• Category-aware discovery</div>'
        '<div class="sidebar-line">• Confidence-guided answers</div>'
        '<div class="sidebar-line">• Intelligent suggestions</div>'
        '<div class="sidebar-line">• Session insights</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-panel">'
        '<div class="sidebar-section">Focus the library</div>',
        unsafe_allow_html=True
    )

    sidebar_index = categories.index(st.session_state.selected_category)
    sidebar_category = st.selectbox(
        "Choose a category:",
        categories,
        index=sidebar_index
    )

    if sidebar_category != st.session_state.selected_category:
        st.session_state.selected_category = sidebar_category
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.caption("Built with Python, Streamlit, Pandas & RapidFuzz")

# --------------------------------------------------
# CURRENT CATEGORY
# --------------------------------------------------

selected_category = st.session_state.selected_category

# --------------------------------------------------
# CATEGORY FILTER
# --------------------------------------------------

if selected_category == "All Categories":
    filtered_faq_data = faq_data.copy()
else:
    filtered_faq_data = faq_data[
        faq_data["Category"] == selected_category
    ].copy()

if filtered_faq_data.empty:
    st.warning("No FAQs available in this category.")
    st.stop()

# --------------------------------------------------
# TEXT CLEANING
# --------------------------------------------------

def clean_text(text):

    text = str(text).lower()

    phrases = [
        "can you tell me about",
        "could you tell me about",
        "please tell me about",
        "tell me about",
        "can you explain",
        "please explain",
        "what is",
        "what are",
        "tell me",
        "please tell me",
        "explain"
    ]

    for phrase in phrases:
        text = text.replace(phrase, "")

    text = re.sub(
        r"[^a-z0-9\s]",
        "",
        text
    )

    text = " ".join(text.split())

    return text


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    '<div class="studio-shell">'
    '<div class="hero-section">'
    '<div class="hero-eyebrow">Premium FAQ workspace</div>'
    '<div class="hero-title">Ask • Discover • Understand</div>'
    '<div class="hero-copy">A refined knowledge studio for finding the right answer with clarity, confidence, and calm editorial focus.</div>'
    '<div class="hero-flow">'
    '<span>Natural language discovery</span>'
    '<span>Focused category browsing</span>'
    '<span>Clear guidance</span>'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)

control_col1, control_col2 = st.columns([1.25, 0.75], gap="small")

with control_col1:
    if st.button("Reset workspace", key="clear_chat", use_container_width=True):
        st.session_state.messages = [welcome_message]
        st.session_state.questions_asked = 0
        st.session_state.answers_found = 0
        st.session_state.questions_not_found = 0
        st.rerun()

with control_col2:
    current_view = selected_category if selected_category != "All Categories" else "All categories"
    st.markdown(
        f'<div class="view-badge">Focused view · {current_view}</div>',
        unsafe_allow_html=True
    )

st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# MAIN LAYOUT
# --------------------------------------------------

main_col, side_col = st.columns([1.45, 0.85], gap="large")

with main_col:

    st.markdown(
        '<div class="workspace-panel">'
        '<div class="panel-heading">Conversation studio</div>'
        '<div class="panel-copy">The live discussion is presented here as a calm, professional knowledge exchange.</div>',
        unsafe_allow_html=True
    )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown(
                    f'<div class="message-bubble user-bubble"><div class="bubble-label">Your question</div><div class="bubble-text">{html.escape(message["content"])}</div></div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="message-bubble assistant-bubble"><div class="bubble-label">Knowledge answer</div><div class="bubble-text">{html.escape(message["content"])}</div></div>',
                    unsafe_allow_html=True
                )

    st.markdown('</div>', unsafe_allow_html=True)

    if len(st.session_state.messages) == 1:
        st.markdown(
            '<div class="section-label">Suggested openings</div>',
            unsafe_allow_html=True
        )

        starter_col1, starter_col2, starter_col3 = st.columns(3)

        with starter_col1:
            if st.button("What is Python?", key="suggest_python", use_container_width=True):
                st.session_state.selected_question = "What is Python?"
                st.rerun()

        with starter_col2:
            if st.button("What is AI?", key="suggest_ai", use_container_width=True):
                st.session_state.selected_question = "What is AI?"
                st.rerun()

        with starter_col3:
            if st.button("What is Machine Learning?", key="suggest_ml", use_container_width=True):
                st.session_state.selected_question = "What is machine learning?"
                st.rerun()

    st.markdown(
        '<div class="composer-shell">',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="composer-label">Ask anything from the knowledge base</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="composer-caption">Type a clear question and the studio will surface the most relevant FAQ answer.</div>',
        unsafe_allow_html=True
    )

    user_question = st.chat_input("Ask your question...")

    st.markdown('</div>', unsafe_allow_html=True)

    if "selected_question" in st.session_state:
        user_question = st.session_state.selected_question
        del st.session_state.selected_question

    if user_question:
        cleaned_input = clean_text(user_question)

        if not cleaned_input:
            st.warning("Please enter a meaningful question.")
            st.stop()

        st.session_state.questions_asked += 1
        st.session_state.messages.append({"role": "user", "content": user_question})

        with st.chat_message("user"):
            st.write(user_question)

        cleaned_user_question = clean_text(user_question)
        cleaned_questions = [
            clean_text(question)
            for question in filtered_faq_data["Question"]
        ]

        result = process.extractOne(
            cleaned_user_question,
            cleaned_questions,
            scorer=fuzz.WRatio
        )

        if result is None:
            st.error("No FAQ data available.")
            st.stop()

        best_cleaned_question, score, index = result

        if score >= 70:
            matched_row = filtered_faq_data.iloc[index]
            bot_response = matched_row["Answer"]
            matched_question = matched_row["Question"]
            matched_category = matched_row["Category"]
            st.session_state.answers_found += 1
            confidence_message = f"Match confidence: {score:.1f}%"
            matched_info = (
                f"Matched FAQ: {matched_question}\n\n"
                f"Category: {matched_category}"
            )
            suggestions = []
        else:
            bot_response = (
                "I couldn't find a confident match for your question.\n\n"
                "Try rephrasing it or explore one of the available knowledge categories."
            )
            st.session_state.questions_not_found += 1
            confidence_message = f"Match confidence: {score:.1f}%"
            matched_info = ""
            suggestions = process.extract(
                cleaned_user_question,
                cleaned_questions,
                scorer=fuzz.WRatio,
                limit=3
            )

        st.session_state.messages.append({"role": "assistant", "content": bot_response})

        with st.chat_message("assistant"):
            st.markdown(
                f'<div class="answer-shell"><div class="answer-label">Knowledge answer</div><div class="answer-body">{html.escape(bot_response)}</div></div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="confidence-card"><div class="confidence-top"><span>Match confidence</span><strong>{score:.1f}%</strong></div><div class="confidence-bar"><div class="confidence-fill" style="width: {min(max(score, 0), 100)}%"></div></div></div>',
                unsafe_allow_html=True
            )
            if matched_info:
                st.markdown(
                    f'<div class="meta-row">{html.escape(matched_info)}</div>',
                    unsafe_allow_html=True
                )
            elif suggestions:
                st.markdown('<div class="section-label">You may want to ask</div>', unsafe_allow_html=True)
                suggestion_items = []
                for suggestion in suggestions:
                    suggestion_question = filtered_faq_data.iloc[suggestion[2]]["Question"]
                    suggestion_items.append(f'<span class="pill-chip">{html.escape(suggestion_question)}</span>')
                st.markdown(f'<div class="chip-row">{" ".join(suggestion_items)}</div>', unsafe_allow_html=True)

with side_col:

    st.markdown(
        '<div class="workspace-panel compact-panel">'
        '<div class="panel-heading">Knowledge map</div>'
        '<div class="panel-copy">Browse the library by topic and stay anchored to the right category.</div>',
        unsafe_allow_html=True
    )

    topic_categories = [category for category in categories if category != "All Categories"]
    for category in topic_categories:
        if st.button(category, key=f"faq_category_{category}", use_container_width=True):
            st.session_state.selected_category = category
            st.rerun()

    if st.button("View all FAQs", use_container_width=True):
        st.session_state.selected_category = "All Categories"
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="workspace-panel compact-panel">'
        '<div class="panel-heading">Studio signals</div>'
        '<div class="panel-copy">A distilled view of the current session and the knowledge library activity.</div>',
        unsafe_allow_html=True
    )

    analytics_html = f"""
    <div class="stats-grid">
        <div class="stat-block">
            <span>Total FAQs</span>
            <strong>{len(faq_data)}</strong>
        </div>
        <div class="stat-block">
            <span>Questions asked</span>
            <strong>{st.session_state.questions_asked}</strong>
        </div>
        <div class="stat-block">
            <span>Answers found</span>
            <strong>{st.session_state.answers_found}</strong>
        </div>
        <div class="stat-block">
            <span>Not found</span>
            <strong>{st.session_state.questions_not_found}</strong>
        </div>
    </div>
    """
    st.markdown(analytics_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if len(st.session_state.messages) > 1:
        chat_history = ""
        for message in st.session_state.messages:
            if message["role"] == "user":
                chat_history += f"You:\n{message['content']}\n\n"
            else:
                chat_history += f"FAQ Knowledge Studio:\n{message['content']}\n\n"
        st.download_button(
            label="Download chat history",
            data=chat_history,
            file_name="faq_chat_history.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.markdown("""<div class="workspace-panel compact-panel" style="margin-top:10px;"><div class="panel-copy">Ask at least one question to download your chat history.</div>
    </div>
    """,
    unsafe_allow_html=True
)
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# REFERENCE SHELF
# --------------------------------------------------

st.markdown(
    '<div class="workspace-panel">'
    '<div class="panel-heading">Reference shelf</div>'
    '<div class="panel-copy">Search and scan the knowledge base without losing the calm rhythm of the studio.</div>',
    unsafe_allow_html=True
)

search_query = st.text_input(
    "Search questions or answers:",
    placeholder="Try keywords such as Python, AI, or Machine Learning"
)

if search_query:
    search_text = search_query.lower().strip()
    search_results = filtered_faq_data[
        filtered_faq_data["Question"].str.lower().str.contains(search_text, na=False)
        |
        filtered_faq_data["Answer"].str.lower().str.contains(search_text, na=False)
    ]

    if not search_results.empty:
        st.success(f"Found {len(search_results)} matching FAQ(s).")
        st.dataframe(
            search_results[["Question", "Answer", "Category"]].reset_index(drop=True),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No FAQ found for your search.")

st.markdown('<div class="section-label">Knowledge library</div>', unsafe_allow_html=True)

display_faq = filtered_faq_data[["Question", "Answer", "Category"]].reset_index(drop=True)
st.dataframe(display_faq, use_container_width=True, hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)
