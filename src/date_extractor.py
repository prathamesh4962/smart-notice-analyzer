import re

import dateparser

from src.preprocessing import clean_text


_MONTH = (
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
)
_DATE_PATTERN = re.compile(
    rf"\b(?:"
    rf"\d{{1,2}}(?:st|nd|rd|th)?\s+{_MONTH}\s+\d{{4}}|"
    rf"{_MONTH}\s+\d{{1,2}}(?:st|nd|rd|th)?,?\s+\d{{4}}|"
    rf"\d{{1,2}}[/-]\d{{1,2}}[/-]\d{{4}}"
    rf")\b",
    re.IGNORECASE,
)
_NUMERIC_DATE_PATTERN = re.compile(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{4})$")
_DEADLINE_HINT = re.compile(
    r"\b(?:deadline|due|by|before|last date|submit|pay|register|apply)\b",
    re.IGNORECASE,
)


def _date_context(text: str, date_text: str) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return next((sentence.strip() for sentence in sentences if date_text in sentence), date_text)


def extract_dates(text: str) -> list[dict[str, str | bool | None]]:
    """Extract explicit dates and flag ambiguous numeric dates without guessing."""
    cleaned = clean_text(text)
    results: list[dict[str, str | bool | None]] = []

    for match in _DATE_PATTERN.finditer(cleaned):
        date_text = match.group(0)
        context = _date_context(cleaned, date_text)
        numeric_match = _NUMERIC_DATE_PATTERN.fullmatch(date_text)
        is_ambiguous = False
        settings: dict[str, object] = {"STRICT_PARSING": True}

        if numeric_match:
            first, second = int(numeric_match.group(1)), int(numeric_match.group(2))
            is_ambiguous = first <= 12 and second <= 12 and first != second
            if first > 12:
                settings["DATE_ORDER"] = "DMY"
            elif second > 12:
                settings["DATE_ORDER"] = "MDY"

        parsed = None if is_ambiguous else dateparser.parse(date_text, settings=settings)
        results.append(
            {
                "text": date_text,
                "normalized_date": parsed.date().isoformat() if parsed else None,
                "is_ambiguous": is_ambiguous,
                "is_deadline": bool(_DEADLINE_HINT.search(context)),
                "context": context,
            }
        )

    return results