import unittest
from unittest.mock import patch

import fitz
import spacy

from src.action_extractor import extract_action_items
from src.date_extractor import extract_dates
from src.entity_extractor import extract_entities
from src.pdf_extractor import extract_notice_text
from src.report_generator import generate_report
from src.summarizer import summarize_text


class ExtractorTests(unittest.TestCase):
    def test_extract_txt(self):
        result = extract_notice_text("notice.txt", b"Submit the form by 12 November 2026.")

        self.assertIn("12 November 2026", result)

    def test_extract_pdf(self):
        document = fitz.open()
        document.new_page().insert_text((72, 72), "Exam notice for 12 November 2026")
        pdf_bytes = document.tobytes()
        document.close()

        result = extract_notice_text("notice.pdf", pdf_bytes)

        self.assertIn("Exam notice", result)

    def test_invalid_and_scanned_pdfs_have_helpful_errors(self):
        with self.assertRaisesRegex(ValueError, "invalid"):
            extract_notice_text("notice.pdf", b"not a PDF")

        empty_pdf = fitz.open()
        empty_pdf.new_page()
        pdf_bytes = empty_pdf.tobytes()
        empty_pdf.close()
        with self.assertRaisesRegex(ValueError, "scanned"):
            extract_notice_text("scan.pdf", pdf_bytes)

    def test_unsupported_file_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported file type"):
            extract_notice_text("notice.docx", b"content")

    def test_extract_dates_and_deadlines(self):
        dates = extract_dates("Submit the application by 12 November 2026.")

        self.assertEqual(dates[0]["normalized_date"], "2026-11-12")
        self.assertTrue(dates[0]["is_deadline"])
        self.assertFalse(dates[0]["is_ambiguous"])

    def test_ambiguous_numeric_date_is_not_interpreted(self):
        dates = extract_dates("The event is on 03/04/2026.")

        self.assertTrue(dates[0]["is_ambiguous"])
        self.assertIsNone(dates[0]["normalized_date"])

    def test_missing_dates_return_empty_list(self):
        self.assertEqual(extract_dates("Students should contact the office."), [])

    def test_extract_action_sentences(self):
        actions = extract_action_items(
            "Submit the form by 12 November 2026. The office opens at 9 AM."
        )

        self.assertEqual(len(actions), 1)
        self.assertIn("Submit the form", actions[0])

    def test_short_summary_is_original_text(self):
        notice = "The examination is on 12 November 2026."

        self.assertEqual(summarize_text(notice), notice)

    def test_long_summary_uses_only_original_sentences(self):
        notice = (
            "The college announces a placement drive. Register by 12 November 2026. "
            "Bring an updated resume to the interview. Contact the placement office for details."
        )
        summary_sentences = summarize_text(notice, max_sentences=2).split(". ")

        self.assertEqual(len(summary_sentences), 2)
        for sentence in summary_sentences:
            self.assertIn(sentence, notice)

    def test_entity_extractor_returns_spacy_entities(self):
        nlp = spacy.blank("en")
        ruler = nlp.add_pipe("entity_ruler")
        ruler.add_patterns([{"label": "GPE", "pattern": "Pune"}])

        with patch("src.entity_extractor._load_nlp", return_value=nlp):
            entities = extract_entities("The seminar will be held in Pune.")

        self.assertEqual(entities, [{"text": "Pune", "label": "GPE"}])

    def test_missing_spacy_model_has_install_instruction(self):
        with patch("src.entity_extractor.spacy.load", side_effect=OSError("missing")):
            with self.assertRaisesRegex(RuntimeError, "spacy download en_core_web_sm"):
                extract_entities("Notice text")

    def test_report_marks_missing_information(self):
        report = generate_report(original_text="A notice with no extracted details.")

        self.assertIn("None detected.", report)
        self.assertIn("A notice with no extracted details.", report)


if __name__ == "__main__":
    unittest.main()