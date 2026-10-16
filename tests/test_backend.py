import unittest
from unittest.mock import patch

import requests
from fastapi import HTTPException

from backend.main import NoticeRequest, analyze_notice_endpoint, health_check
from src.api_client import BackendAPIError, analyze_notice_via_api


class BackendTests(unittest.TestCase):
    def test_health_check(self):
        self.assertEqual(health_check(), {"status": "ok"})

    @patch("backend.main.analyze_notice")
    def test_analysis_endpoint_returns_analysis(self, analyze_notice):
        expected = {
            "original_text": "Pay fees by 12 November 2026.",
            "category": "Fees",
            "estimated_probability": 0.8,
            "summary": "Pay fees by 12 November 2026.",
            "dates": [
                {
                    "text": "12 November 2026",
                    "normalized_date": "2026-11-12",
                    "is_ambiguous": False,
                    "is_deadline": True,
                    "context": "Pay fees by 12 November 2026.",
                }
            ],
            "entities": [],
            "action_items": ["Pay fees by 12 November 2026."],
            "report": "# Notice Analysis Report",
        }
        analyze_notice.return_value = expected

        result = analyze_notice_endpoint(NoticeRequest(text=expected["original_text"]))

        self.assertEqual(result.model_dump(), expected)
        analyze_notice.assert_called_once_with(expected["original_text"])

    def test_analysis_endpoint_returns_bad_request_for_empty_text(self):
        with patch(
            "backend.main.analyze_notice",
            side_effect=ValueError("Notice text cannot be empty."),
        ):
            with self.assertRaises(HTTPException) as error:
                analyze_notice_endpoint(NoticeRequest(text=" "))

        self.assertEqual(error.exception.status_code, 422)
        self.assertEqual(error.exception.detail, "Notice text cannot be empty.")

    @patch("src.api_client.requests.post")
    def test_api_client_posts_notice_and_returns_json(self, post):
        expected = {"category": "Fees"}
        post.return_value.ok = True
        post.return_value.json.return_value = {
            "original_text": "Pay fees by 12 November 2026.",
            "category": "Fees",
            "estimated_probability": 0.8,
            "summary": "Pay fees by 12 November 2026.",
            "dates": [],
            "entities": [],
            "action_items": [],
            "report": "# Notice Analysis Report",
        }

        result = analyze_notice_via_api("Notice text", "https://api.example.com/")

        self.assertEqual(result["category"], expected["category"])
        post.assert_called_once_with(
            "https://api.example.com/api/analyze",
            json={"text": "Notice text"},
            timeout=120,
        )

    @patch("src.api_client.requests.post")
    def test_api_client_surfaces_connection_errors(self, post):
        post.side_effect = requests.ConnectionError("offline")

        with self.assertRaisesRegex(BackendAPIError, "Could not connect"):
            analyze_notice_via_api("Notice text", "http://127.0.0.1:8000")


if __name__ == "__main__":
    unittest.main()
