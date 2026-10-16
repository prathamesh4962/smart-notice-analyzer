import html
import re
import unicodedata


_CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_WHITESPACE = re.compile(r"\s+")
_TOKEN_PATTERN = re.compile(
    r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"
    r"|\d{1,2}:\d{2}(?:\s?[ap]m)?"
    r"|\d+(?:\.\d+)?"
    r"|[^\W\d_]+(?:['’][^\W\d_]+)*",
    re.IGNORECASE,
)


def clean_text(text: str) -> str:
    """Normalize Unicode and whitespace without removing notice details."""
    if not isinstance(text, str):
        raise TypeError("Notice text must be a string.")

    normalized = unicodedata.normalize("NFKC", html.unescape(text))
    normalized = _CONTROL_CHARACTERS.sub(" ", normalized)
    return _WHITESPACE.sub(" ", normalized).strip()


def normalize_text(text: str) -> str:
    """Return cleaned, case-insensitive text for classification features."""
    return clean_text(text).casefold()


def tokenize_text(text: str) -> list[str]:
    """Split text into word, number, date, and time tokens."""
    return _TOKEN_PATTERN.findall(clean_text(text))