import spacy

from src.preprocessing import clean_text


MODEL_NAME = "en_core_web_sm"


def _load_nlp():
    try:
        return spacy.load(MODEL_NAME)
    except OSError as error:
        raise RuntimeError(
            "The spaCy English model is missing. Install it with "
            "'python -m spacy download en_core_web_sm'."
        ) from error


def extract_entities(text: str) -> list[dict[str, str]]:
    """Return spaCy named entities, such as people, organizations, and places."""
    cleaned = clean_text(text)
    if not cleaned:
        return []

    document = _load_nlp()(cleaned)
    return [{"text": entity.text, "label": entity.label_} for entity in document.ents]