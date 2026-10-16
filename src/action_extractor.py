import re

from src.preprocessing import clean_text


_ACTION_VERBS = re.compile(
    r"\b(?:submit|pay|register|attend|upload|bring|contact|collect|complete|"
    r"apply|report|email|download|verify|clear|participate|renew|update|"
    r"visit|meet|file)\b",
    re.IGNORECASE,
)


def extract_action_items(text: str) -> list[str]:
    """Return original notice sentences containing an action keyword."""
    cleaned = clean_text(text)
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    return [sentence.strip() for sentence in sentences if _ACTION_VERBS.search(sentence)]