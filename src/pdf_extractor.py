from pathlib import Path

import fitz

from src.preprocessing import clean_text


def extract_notice_text(filename: str, file_bytes: bytes) -> str:
    """Extract selectable text from a PDF or decode a UTF-8 text file."""
    suffix = Path(filename).suffix.lower()
    if not file_bytes:
        raise ValueError("The uploaded file is empty.")

    if suffix == ".txt":
        extracted = file_bytes.decode("utf-8-sig", errors="replace")
    elif suffix == ".pdf":
        try:
            with fitz.open(stream=file_bytes, filetype="pdf") as document:
                extracted = "\n".join(page.get_text("text") for page in document)
        except fitz.FileDataError as error:
            raise ValueError("The uploaded PDF is invalid or cannot be read.") from error
        if not extracted.strip():
            raise ValueError(
                "No selectable text was found. The PDF may be scanned; OCR is not supported."
            )
    else:
        raise ValueError("Unsupported file type. Upload a PDF or TXT file.")

    cleaned = clean_text(extracted)
    if not cleaned:
        raise ValueError("The uploaded file does not contain readable text.")
    return cleaned