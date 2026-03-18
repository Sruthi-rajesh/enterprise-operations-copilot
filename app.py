import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX")
OLLAMA_MODEL = "gemma3:4b"

st.set_page_config(
    page_title="Enterprise Operations Copilot",
    page_icon="🤖",
    layout="wide"
)


def search_documents(search_text: str, top: int = 3):
    url = f"{AZURE_SEARCH_ENDPOINT}/indexes/{AZURE_SEARCH_INDEX}/docs/search?api-version=2023-11-01"
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_SEARCH_KEY,
    }
    payload = {
        "search": search_text,
        "top": top,
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\n", " ").replace("\r", " ")
    return " ".join(text.split())


def short_snippet(text: str, limit: int = 240) -> str:
    text = clean_text(text)
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "..."


def doc_badge(title: str) -> str:
    title_lower = title.lower()
    if "faq" in title_lower:
        return "FAQ"
    if "crm" in title_lower:
        return "CRM"
    if "policy" in title_lower:
        return "Policy"
    if "checklist" in title_lower:
        return "Checklist"
    if "handoff" in title_lower:
        return "Process"
    if "onboarding" in title_lower:
        return "SOP"
    return "Document"


def build_context(documents):
    blocks = []
    for doc in documents:
        title = doc.get("title", "Untitled Document")
        content = clean_text(doc.get("content", ""))
        if content:
            blocks.append(f"Source: {title}\nContent: {content[:1200]}")
    return "\n\n".join(blocks)


def extract_source_titles(documents):
    seen = set()
    titles = []
    for doc in documents:
        title = doc.get("title", "Untitled Document")
        if title not in seen:
            seen.add(title)
            titles.append(title)
    return titles


def generate_answer_with_ollama(question: str, documents):
    context = build_context(documents)

    prompt = f"""
You are an enterprise operations assistant.

Answer the user's question using ONLY the context below.
If the context is insufficient, say exactly:
"I could not find enough support in the indexed documents."

Rules:
- If the question is not directly answered in the documents, say so clearly first.
- Then provide the closest relevant information supported by the context.
- Distinguish between direct support and related support.
- Use lowercase natural phrasing unless a term is explicitly capitalized in the source.
- If the question is not directly answered, begin with one short sentence stating that clearly.
- Then summarize the closest supported operational interpretation.
- Be concise and professional.
- Use simple business language.
- Do not invent facts.
- Do not use outside knowledge.
- Maximum 5 bullet points.
- Do not include a sources section in the answer.

Return your answer in this format:

Summary:
<2-3 sentence answer>

Key Points:
- ...
- ...
- ...

Question:
{question}

Context:
{context}
"""

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False,
    }

    response = requests.post(
        "http://localhost:11434/api/chat",
        json=payload,
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    return data["message"]["content"]


st.markdown("""
<style>
    .main, [data-testid="stAppViewContainer"] {
        background: #f8fafc !important;
    }

    .block-container {
        max-width: 1150px;
        padding-top: 1.4rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, h4, h5, h6, p, label, div, span {
        color: #1f2937 !important;
    }

    .hero-wrap {
        background: linear-gradient(135deg, #f8fbff 0%, #eef5ff 100%);
        border: 1px solid #dbe7f7;
        border-radius: 30px;
        padding: 1.6rem;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
        margin-bottom: 1.3rem;
    }

    .hero-title {
        font-size: 2.9rem;
        font-weight: 800;
        line-height: 1.05;
        letter-spacing: -0.03em;
        margin-bottom: 0.6rem;
        color: #0f172a !important;
    }

    .hero-chat {
        display: inline-block;
        background: #ffffff;
        border: 1px solid #e5edf8;
        border-radius: 18px;
        padding: 0.85rem 1rem;
        font-size: 1.02rem;
        color: #334155 !important;
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.05);
        margin-bottom: 0.9rem;
    }

    .hero-sub {
        color: #64748b !important;
        font-size: 0.98rem;
    }

    .search-label {
        font-size: 1rem;
        font-weight: 800;
        margin-top: 0.4rem;
        margin-bottom: 0.55rem;
        color: #1e293b !important;
    }

    .chips-note {
        color: #64748b !important;
        font-size: 0.92rem;
        margin-top: 0.4rem;
        margin-bottom: 0.35rem;
    }

    div.stButton > button[kind="secondary"] {
        background: #fecaca !important;
        color: #7f1d1d !important;
        border: 1px solid #fca5a5 !important;
        padding: 0.7rem 1.15rem !important;
        border-radius: 999px !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.08) !important;
    }

    div.stButton > button[kind="secondary"]:hover {
        background: #fca5a5 !important;
        color: #7f1d1d !important;
        border: 1px solid #f87171 !important;
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: #ffffff !important;
        border: none !important;
        padding: 0.9rem 1.6rem !important;
        border-radius: 16px !important;
        font-weight: 800 !important;
        box-shadow: 0 8px 18px rgba(37, 99, 235, 0.20) !important;
    }

    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1d4ed8, #1e40af) !important;
        color: #ffffff !important;
        border: none !important;
    }

    .stTextInput > div > div > input {
        border-radius: 22px !important;
        padding: 1rem 1.1rem !important;
        background: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #d1d5db !important;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);
        font-size: 1.02rem !important;
    }

    .stTextInput label {
        font-weight: 800 !important;
        color: #1f2937 !important;
        margin-bottom: 0.35rem !important;
    }

    .answer-card {
        background: #ffffff;
        border: 1px solid #dbeafe;
        border-radius: 24px;
        padding: 1.2rem 1.3rem;
        box-shadow: 0 10px 24px rgba(37, 99, 235, 0.06);
        margin-top: 1.1rem;
        margin-bottom: 1.1rem;
    }

    .answer-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #1d4ed8 !important;
        margin-bottom: 0.6rem;
    }

    .sources-card {
        background: #ffffff;
        border: 1px solid #f3e8ff;
        border-radius: 22px;
        padding: 1rem 1.2rem;
        box-shadow: 0 8px 20px rgba(168, 85, 247, 0.06);
        margin-bottom: 1rem;
    }

    .sources-title {
        font-size: 1.2rem;
        font-weight: 800;
        color: #7c3aed !important;
        margin-bottom: 0.7rem;
    }

    .source-pill {
        display: inline-block;
        background: #f5f3ff;
        color: #5b21b6 !important;
        border: 1px solid #ddd6fe;
        border-radius: 999px;
        padding: 0.45rem 0.8rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
        font-size: 0.9rem;
    }

    .results-header {
        font-size: 1.8rem;
        font-weight: 800;
        margin-top: 1.35rem;
        margin-bottom: 1rem;
        color: #0f172a !important;
    }

    .result-card {
        background: #ffffff;
        border: 1px solid #d9f2df;
        border-radius: 24px;
        padding: 1.15rem 1.2rem 1rem 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 10px 24px rgba(34, 197, 94, 0.06);
    }

    .result-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        margin-bottom: 0.7rem;
    }

    .result-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #14532d !important;
        margin: 0;
    }

    .result-badge {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 800;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        background: #dcfce7;
        color: #166534 !important;
        border: 1px solid #bbf7d0;
        white-space: nowrap;
    }

    .meta-row {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-bottom: 0.8rem;
    }

    .meta-pill {
        display: inline-block;
        font-size: 0.8rem;
        color: #166534 !important;
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        padding: 0.3rem 0.7rem;
        border-radius: 999px;
        font-weight: 700;
    }

    .snippet-box {
        background: #f9fffb;
        border-radius: 16px;
        padding: 0.95rem 1rem;
        color: #14532d !important;
        line-height: 1.7;
        border: 1px solid #d9f2df;
    }

    .empty-box {
        background: #ffffff;
        border: 1px dashed #cbd5e1;
        border-radius: 20px;
        padding: 1.2rem;
        color: #334155 !important;
        margin-top: 1rem;
    }

    .small-note {
        color: #64748b !important;
        font-size: 0.9rem;
    }

    details {
        background: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 18px !important;
        padding: 0.4rem 0.8rem !important;
        margin-top: 0.45rem !important;
    }

    summary {
        color: #334155 !important;
        font-weight: 700 !important;
    }

    .stCodeBlock, pre, code {
        background: #f8fafc !important;
        color: #1f2937 !important;
        border-radius: 14px !important;
    }
</style>
""", unsafe_allow_html=True)

suggestions = [
    "onboarding",
    "escalation",
    "CRM stage",
    "kickoff",
]

if "query_text" not in st.session_state:
    st.session_state.query_text = ""

def set_query(value: str):
    st.session_state.query_text = value


hero_col1, hero_col2 = st.columns([0.9, 3.6], gap="medium")

with hero_col1:
    image_path = "download.jpeg"
    if os.path.exists(image_path):
        st.image(image_path, width=170)
    else:
        st.markdown("""
        <div style="
            width:170px;
            height:170px;
            border-radius:28px;
            background:linear-gradient(135deg,#dbeafe,#e0f2fe);
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:3rem;
            box-shadow: inset 0 0 0 1px rgba(59,130,246,0.10);
        ">🤖</div>
        """, unsafe_allow_html=True)

with hero_col2:
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-title">Enterprise Operations Copilot</div>
        <div class="hero-chat">Hi — how can I help you today?</div>
        <div class="hero-sub">
            Search across SOPs, policies, handoff documents, FAQs, and CRM process guides.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="search-label">Enter a search query</div>', unsafe_allow_html=True)

query = st.text_input(
    "Enter a search query",
    value=st.session_state.query_text,
    placeholder="Try: onboarding, escalation, CRM stage, kickoff",
    label_visibility="collapsed",
)

st.markdown('<div class="chips-note">Suggested searches</div>', unsafe_allow_html=True)

chip_cols = st.columns(len(suggestions))
for i, suggestion in enumerate(suggestions):
    with chip_cols[i]:
        if st.button(suggestion, key=f"suggestion_{i}"):
            set_query(suggestion)
            st.rerun()

search_col1, _ = st.columns([0.22, 0.78])
with search_col1:
    search_clicked = st.button("Search", key="main_search_button", type="primary")

if search_clicked:
    st.session_state.query_text = query

if search_clicked:
    if not query.strip():
        st.warning("Please enter a search query.")
    else:
        try:
            results = search_documents(query, top=3)
            documents = results.get("value", [])

            if not documents:
                st.markdown("""
                <div class="empty-box">
                    <strong>No results found.</strong><br>
                    Try a shorter keyword like <em>onboarding</em>, <em>CRM</em>, or <em>escalation</em>.
                </div>
                """, unsafe_allow_html=True)
            else:
                answer = generate_answer_with_ollama(query, documents)
                if not answer.strip():
                    answer = "I could not find enough support in the indexed documents."

                source_titles = extract_source_titles(documents)

                st.markdown(f"""
                <div class="answer-card">
                    <div class="answer-title">Grounded Answer</div>
                    <div>{answer}</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(
                    '<div class="small-note">This answer is generated only from the indexed enterprise documents.</div>',
                    unsafe_allow_html=True,
                )

                sources_html = "".join(
                    [f'<span class="source-pill">{title}</span>' for title in source_titles]
                )

                st.markdown(f"""
                <div class="sources-card">
                    <div class="sources-title">Sources Used</div>
                    <div>{sources_html}</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(
                    '<div class="results-header">Supporting Search Results</div>',
                    unsafe_allow_html=True,
                )

                for i, doc in enumerate(documents, start=1):
                    title = doc.get("title", "Untitled Document")
                    full_content = clean_text(doc.get("content", ""))
                    preview = short_snippet(full_content, limit=260)
                    score = doc.get("@search.score", "N/A")
                    badge = doc_badge(title)

                    st.markdown(f"""
                    <div class="result-card">
                        <div class="result-top">
                            <div class="result-title">{i}. {title}</div>
                            <div class="result-badge">{badge}</div>
                        </div>
                        <div class="meta-row">
                            <div class="meta-pill">Score: {score}</div>
                            <div class="meta-pill">Top match</div>
                        </div>
                        <div class="snippet-box">{preview}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.expander("View full excerpt"):
                        st.code(full_content[:2500] if full_content else "No excerpt available.")

                st.markdown(
                    '<div class="small-note">Answer generated from the top Azure AI Search results using a local Ollama model.</div>',
                    unsafe_allow_html=True,
                )

        except Exception as e:
            st.error(f"Error running search or generation: {e}")  
            