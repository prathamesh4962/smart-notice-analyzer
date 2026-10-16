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

st.set_page_config(page_title="Smart Notice Analyzer", layout="wide")
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] { background: #f4f7f5; }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] { background: #edf2ef; }
    .block-container { max-width: 1280px; padding-top: 1.7rem; padding-bottom: 3rem; }
    h1, h2, h3 { color: #183b36; }
    [data-testid="stMetric"] {
        background: #ffffff;
        border-top: 3px solid #237666;
        padding: 0.8rem 1rem;
    }
    @media (max-width: 640px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; }
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
    st.header("Notice workspace")
    input_mode = st.radio(
        "Input method",
        options=("Paste text", "Upload PDF/TXT"),
        horizontal=True,
        key="input_mode",
    )
    st.button("Load sample notice", on_click=load_sample, use_container_width=True)
    st.button("Clear current notice", on_click=reset_current_notice, use_container_width=True)

    st.divider()
    st.subheader("Session history")
    history = st.session_state["analysis_history"]
    if history:
        st.button("Clear history", on_click=clear_history, use_container_width=True)
        for item in history:
            st.caption(f"{item['timestamp']} · {item['category']}")
            st.write(item["summary"])
    else:
        st.caption("Analyzed notices will appear here during this session.")

st.title("Smart Notice Analyzer")
st.caption("Extract useful details from college notices.")

uploaded_file = None
if input_mode == "Paste text":
    notice_text = st.text_area(
        "Notice text",
        key="notice_text",
        height=220,
        placeholder="Paste a college notice here...",
    )
else:
    uploaded_file = st.file_uploader(
        "Upload a PDF or TXT notice",
        type=("pdf", "txt"),
        key=f"notice_upload_{st.session_state['upload_generation']}",
    )
    notice_text = ""

analyze_clicked = st.button("Analyze notice", type="primary", use_container_width=True)
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
    st.subheader("Analysis")

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