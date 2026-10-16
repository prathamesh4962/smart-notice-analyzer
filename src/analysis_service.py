from functools import lru_cache

import joblib
from sklearn.pipeline import Pipeline

from src.action_extractor import extract_action_items
from src.classifier import MODEL_PATH
from src.date_extractor import extract_dates
from src.entity_extractor import extract_entities
from src.preprocessing import clean_text
from src.report_generator import generate_report
from src.summarizer import summarize_text


@lru_cache(maxsize=1)
def load_classifier() -> Pipeline:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "The classifier model is missing. Train it with 'python -m src.classifier'."
        )
    return joblib.load(MODEL_PATH)


def analyze_notice(notice_text: str) -> dict[str, object]:
    """Analyze a cleaned notice and return serializable results."""
    cleaned_text = clean_text(notice_text)
    if not cleaned_text:
        raise ValueError("Notice text cannot be empty.")

    pipeline = load_classifier()
    classifier = pipeline.named_steps["classifier"]
    probabilities = pipeline.predict_proba([cleaned_text])[0]
    predicted_index = int(probabilities.argmax())
    category = str(classifier.classes_[predicted_index])
    probability = float(probabilities[predicted_index])
    summary = summarize_text(cleaned_text)
    dates = extract_dates(cleaned_text)
    entities = extract_entities(cleaned_text)
    actions = extract_action_items(cleaned_text)
    report = generate_report(
        original_text=cleaned_text,
        category=category,
        estimated_probability=probability,
        summary=summary,
        dates=dates,
        entities=entities,
        action_items=actions,
    )

    return {
        "original_text": cleaned_text,
        "category": category,
        "estimated_probability": probability,
        "summary": summary,
        "dates": dates,
        "entities": entities,
        "action_items": actions,
        "report": report,
    }
