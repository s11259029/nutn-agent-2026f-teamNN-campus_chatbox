"""Executable acceptance tests for the email-draft baseline.

Run from the repository root with:

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from email_draft_baseline import create_email_draft  # noqa: E402


VALID_REQUEST = {
    "teacher_name": "王小明",
    "purpose": "course_add_request",
    "student_name": "李安以",
    "request_details": "想詢問老師是否可以加簽人工智慧課程",
}


class EmailDraftBaselineAcceptanceTests(unittest.TestCase):
    def test_ac01_normal_request_returns_grounded_draft(self) -> None:
        status, response = create_email_draft(VALID_REQUEST)

        self.assertEqual(status, 200)
        self.assertTrue(response["can_fulfill"])
        self.assertEqual(response["teacher"]["name"], "王小明")
        self.assertEqual(response["email_draft"]["to"], "wang@example.edu.tw")
        self.assertIn("加簽", response["email_draft"]["subject"])
        self.assertIn("李安以", response["email_draft"]["body"])
        self.assertTrue(response["requires_confirmation"])
        self.assertEqual(response["send_status"], "not_sent")
        self.assertEqual(
            response["sources"][0]["url"],
            response["teacher"]["profile_url"],
        )

    def test_ac02_missing_teacher_name_stops_at_request_validation(self) -> None:
        request = {**VALID_REQUEST, "teacher_name": ""}

        status, response = create_email_draft(request)

        self.assertEqual(status, 422)
        self.assertFalse(response["can_fulfill"])
        self.assertEqual(response["error"]["code"], "MISSING_REQUIRED_FIELD")
        self.assertIn("teacher_name", response["error"]["missing_fields"])
        self.assertIsNone(response["teacher"])
        self.assertIsNone(response["email_draft"])
        self.assertEqual(response["send_status"], "not_sent")

    def test_ac03_ungrounded_recipient_is_rejected(self) -> None:
        status, response = create_email_draft(
            VALID_REQUEST,
            provider_mode="ungrounded",
        )

        self.assertEqual(status, 502)
        self.assertFalse(response["can_fulfill"])
        self.assertEqual(response["error"]["code"], "UNGROUNDED_EMAIL")
        self.assertIsNone(response["email_draft"])
        self.assertEqual(response["send_status"], "not_sent")

    def test_known_failure_partial_teacher_name_returns_404(self) -> None:
        request = {**VALID_REQUEST, "teacher_name": "王老師"}

        status, response = create_email_draft(request)

        self.assertEqual(status, 404)
        self.assertFalse(response["can_fulfill"])
        self.assertEqual(response["error"]["code"], "TEACHER_NOT_FOUND")
        self.assertIsNone(response["email_draft"])
        self.assertEqual(response["send_status"], "not_sent")


if __name__ == "__main__":
    unittest.main(verbosity=2)
