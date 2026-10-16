from datetime import datetime
from pathlib import Path

import joblib
import streamlit as st

from src.action_extractor import extract_action_items
from src.classifier import MODEL_PATH
from src.date_extractor import extract_dates
from src.entity_extractor import extract_entities
from src.pdf_extractor import extract_notice_text
from src.preprocessing import clean_text
from src.report_generator import generate_report
from src.summarizer import summarize_text


PROJECT_ROOT = Path(__file__).resolve().parent
SAMPLE_NOTICE = (
    "The campus placement registration portal is open for final-year students. "
    "Complete your profile and upload your resume by 24 October 2026 to participate "
    "in company recruitment drives. The placement office is in Block A."
)

st.set_page_config(
    page_title="Smart Notice Analyzer",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(
    """
    <style>
    :root {
        color-scheme: light;
        --ink: #172033;
        --brand: #176b5b;
        --border: #dce4ec;
    }
    [data-testid="stAppViewContainer"] {
        background: #f4f7fb;
        color: var(--ink);
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] { background: #edf2f7; }
    .block-container {
        max-width: 1080px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    h1, h2, h3, p, label, [data-testid="stWidgetLabel"],
    [data-testid="stCaptionContainer"], [data-testid="stMarkdownContainer"] {
        color: var(--ink) !important;
    }
    h1, h2, h3 { letter-spacing: -0.02em; }
    .hero {
        padding: 1.8rem 2rem;
        margin-bottom: 1.7rem;
        border: 1px solid #d9e7e4;
        border-radius: 18px;
        background: linear-gradient(120deg, #e7f4f0 0%, #f7fafc 72%);
    }
    .hero .eyebrow {
        margin: 0 0 0.45rem;
        color: #176b5b;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
    .hero h1 {
        margin: 0;
        color: #172033 !important;
        font-size: clamp(2rem, 4vw, 2.7rem);
        line-height: 1.15;
    }
    .hero p {
        max-width: 680px;
        margin: 0.65rem 0 0;
        color: #48566b !important;
        font-size: 1.03rem;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--border);
        border-radius: 14px;
        background: #fff;
    }
    textarea, input {
        color: var(--ink) !important;
        background: #fff !important;
        border-color: #cbd5e1 !important;
    }
    textarea::placeholder { color: #738095 !important; opacity: 1; }
    [data-testid="stMetric"] {
        min-height: 112px;
        border: 1px solid var(--border);
        border-top: 3px solid var(--brand);
        border-radius: 12px;
        background: #fff;
        padding: 0.8rem 1rem;
        box-shadow: 0 2px 8px rgba(23, 32, 51, 0.04);
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
        color: var(--ink) !important;
    }
    [data-testid="stBaseButton-primary"] {
        border-color: var(--brand);
        background: var(--brand);
        color: #fff;
        font-weight: 650;
    }
    [data-testid="stBaseButton-primary"]:hover {
        border-color: #105347;
        background: #105347;
        color: #fff;
    }
    [data-testid="stDataFrame"] { border: 1px solid var(--border); }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: var(--ink) !important;
    }
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: var(--ink) !important; }
    @media (max-width: 640px) {
        .block-container { padding: 1rem 0.8rem 2rem; }
        .hero { padding: 1.35rem 1.2rem; }
        [data-testid="stMetric"] { padding: 0.65rem 0.75rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.session_state.setdefault("notice_text", "")
st.session_state.setdefault("analysis_result", None)
st.session_state.setdefault("analysis_history", [])
st.session_state.setdefault("upload_generation", 0)


def load_sample() -> None:
    st.session_state["notice_text"] = SAMPLE_NOTICE
    st.session_state["input_mode"] = "Paste text"


def reset_current_notice() -> None:
    st.session_state["notice_text"] = ""
    st.session_state["analysis_result"] = None
    st.session_state["upload_generation"] += 1


def clear_history() -> None:
    st.session_state["analysis_history"] = []


def analyze_notice(notice_text: str) -> dict[str, object]:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "The classifier model is missing. Train it with 'python -m src.classifier'."
        )

    pipeline = joblib.load(MODEL_PATH)
    classifier = pipeline.named_steps["classifier"]
    probabilities = pipeline.predict_proba([notice_text])[0]
    predicted_index = int(probabilities.argmax())
    category = str(classifier.classes_[predicted_index])
    probability = float(probabilities[predicted_index])
    summary = summarize_text(notice_text)
    dates = extract_dates(notice_text)
    entities = extract_entities(notice_text)
    actions = extract_action_items(notice_text)
    report = generate_report(
        original_text=notice_text,
        category=category,
        estimated_probability=probability,
        summary=summary,
        dates=dates,
        entities=entities,
        action_items=actions,
    )

    return {
        "original_text": notice_text,
        "category": category,
        "estimated_probability": probability,
        "summary": summary,
        "dates": dates,
        "entities": entities,
        "action_items": actions,
        "report": report,
    }


with st.sidebar:
    st.header("Your session")
    st.divider()
    st.subheader("Recent analyses")
    history = st.session_state["analysis_history"]
    if history:
        st.button("Clear history", on_click=clear_history, use_container_width=True)
        for item in history:
            st.caption(f"{item['timestamp']} · {item['category']}")
            st.write(item["summary"])
    else:
        st.caption("Your analyzed notices will appear here until you close this session.")

st.markdown(
    """
    <div class="hero">
        <p class="eyebrow">College notice assistant</p>
        <h1>Smart Notice Analyzer</h1>
        <p>Turn long notices into clear summaries, important dates, and practical next steps.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.subheader("1. Add a notice")
st.caption("Paste the notice text or upload a PDF/TXT file to get started.")

uploaded_file = None
with st.container(border=True):
    input_mode = st.radio(
        "Choose an input method",
        options=("Paste text", "Upload PDF/TXT"),
        horizontal=True,
        key="input_mode",
    )
    sample_column, clear_column = st.columns([1, 1])
    sample_column.button(
        "Try a sample notice",
        on_click=load_sample,
        use_container_width=True,
    )
    clear_column.button(
        "Clear notice",
        on_click=reset_current_notice,
        use_container_width=True,
    )

    if input_mode == "Paste text":
        notice_text = st.text_area(
            "Notice text",
            key="notice_text",
            height=220,
            placeholder="Paste the full college notice here...",
            help="Include the complete notice for the most useful summary and extracted details.",
        )
    else:
        uploaded_file = st.file_uploader(
            "Choose a PDF or TXT notice",
            type=("pdf", "txt"),
            key=f"notice_upload_{st.session_state['upload_generation']}",
            help="Text-based PDFs are supported. Scanned image PDFs are not.",
        )
        notice_text = ""

    analyze_clicked = st.button(
        "Analyze notice",
        type="primary",
        use_container_width=True,
    )

if analyze_clicked:
    try:
        if input_mode == "Paste text":
            source_text = clean_text(notice_text)
        elif uploaded_file is not None:
            source_text = extract_notice_text(uploaded_file.name, uploaded_file.getvalue())
        else:
            source_text = ""

        if not source_text:
            st.error("Enter notice text or upload a readable PDF/TXT file first.")
        else:
            with st.spinner("Analyzing notice..."):
                result = analyze_notice(source_text)
            st.session_state["analysis_result"] = result
            st.session_state["analysis_history"].insert(
                0,
                {
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "category": result["category"],
                    "summary": result["summary"],
                },
            )
            st.session_state["analysis_history"] = st.session_state["analysis_history"][:10]
    except (FileNotFoundError, RuntimeError, ValueError, OSError) as error:
        st.error(str(error))

result = st.session_state["analysis_result"]
if result:
    st.divider()
    st.subheader("2. Your analysis")

    category_column, score_column, dates_count_column, actions_count_column = st.columns(4)
    category_column.metric("Predicted category", result["category"])
    score_column.metric(
        "Estimated class probability",
        f"{result['estimated_probability']:.1%}",
    )
    dates_count_column.metric("Detected dates", len(result["dates"]))
    actions_count_column.metric("Action items", len(result["action_items"]))
    st.caption(
        "This probability is a model estimate, not a guarantee. "
        "The classifier was trained on a small synthetic dataset."
    )

    st.markdown("### Summary")
    st.write(result["summary"] or "No summary could be created.")

    dates_column, entities_column = st.columns(2)
    with dates_column:
        st.markdown("### Dates and deadlines")
        if result["dates"]:
            date_rows = [
                {
                    "Date in notice": item["text"],
                    "Interpretation": (
                        "Ambiguous; not interpreted"
                        if item["is_ambiguous"]
                        else item["normalized_date"] or "Not interpreted"
                    ),
                    "Possible deadline": "Yes" if item["is_deadline"] else "No",
                }
                for item in result["dates"]
            ]
            st.dataframe(date_rows, hide_index=True, use_container_width=True)
        else:
            st.write("None detected.")

    with entities_column:
        st.markdown("### Named entities")
        if result["entities"]:
            entity_rows = [
                {"Entity": item["text"], "Type": item["label"]}
                for item in result["entities"]
            ]
            st.dataframe(entity_rows, hide_index=True, use_container_width=True)
        else:
            st.write("None detected.")

    st.markdown("### Action items")
    if result["action_items"]:
        for action in result["action_items"]:
            st.write(action)
    else:
        st.write("None detected.")

    with st.expander("Original notice"):
        st.text(result["original_text"])

    st.markdown("### Report")
    st.download_button(
        "Download Markdown report",
        data=result["report"],
        file_name="notice_analysis.md",
        mime="text/markdown",
    )
    st.code(result["report"], language="markdown")