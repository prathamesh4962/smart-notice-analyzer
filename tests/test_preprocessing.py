import unittest

from src.preprocessing import clean_text, normalize_text, tokenize_text


class PreprocessingTests(unittest.TestCase):
    def test_clean_text_normalizes_spacing_and_html_entities(self):
        self.assertEqual(clean_text("  Submit&nbsp;the form.\n"), "Submit the form.")

    def test_normalize_text_preserves_dates_and_action_words(self):
        normalized = normalize_text("Submit the form by 12 November 2026.")

        self.assertIn("12 november 2026", normalized)
        self.assertIn("submit", normalized)
        self.assertIn("form", normalized)

    def test_tokenize_text_preserves_numeric_dates_and_times(self):
        tokens = tokenize_text("Exam on 12/11/2026 at 9:00 AM; submit the form.")

        self.assertIn("12/11/2026", tokens)
        self.assertIn("9:00 AM", tokens)
        self.assertIn("submit", tokens)
        self.assertIn("form", tokens)

    def test_empty_text_returns_empty_values(self):
        self.assertEqual(clean_text("  \n"), "")
        self.assertEqual(normalize_text(""), "")
        self.assertEqual(tokenize_text(""), [])

    def test_non_string_input_is_rejected(self):
        with self.assertRaises(TypeError):
            clean_text(None)


if __name__ == "__main__":
    unittest.main()