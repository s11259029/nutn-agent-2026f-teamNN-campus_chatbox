"""Deterministic fixture-backed baseline for generating email drafts.

This module intentionally performs no network access and never sends email.
It exists so the Baseline Declaration acceptance cases can be executed before
an HTTP API or an LLM provider is introduced.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


MODEL_PROFILE = "deterministic-fixture-template-v0"

PURPOSE_LABELS = {
    "project_inquiry": "詢問專題名額",
    "research_inquiry": "詢問研究方向",
    "course_question": "詢問課程問題",
    "meeting_request": "預約討論時間",
    "course_add_request": "申請課程加簽",
    "late_submission_request": "申請補交作業",
    "answer_request": "詢問題目答案或解題說明",
    "grade_inquiry": "詢問成績",
    "other": "其他事項詢問",
}

# Synthetic data used only for reproducible tests. It is not real faculty data.
TEACHER_FIXTURE = {
    "王小明": {
        "name": "王小明",
        "title": "教授",
        "email": "wang@example.edu.tw",
        "research_areas": ["人工智慧", "自然語言處理"],
        "profile_url": "https://example.edu.tw/teachers/wang",
    }
}

REQUIRED_FIELDS = (
    "teacher_name",
    "purpose",
    "student_name",
    "request_details",
)


def _failure(
    status: int,
    *,
    reason: str,
    code: str,
    intent: str | None = None,
    missing_fields: list[str] | None = None,
) -> tuple[int, dict[str, Any]]:
    error: dict[str, Any] = {"code": code}
    if missing_fields:
        error["missing_fields"] = missing_fields

    return status, {
        "can_fulfill": False,
        "intent": intent,
        "teacher": None,
        "email_draft": None,
        "sources": [],
        "requires_confirmation": False,
        "send_status": "not_sent",
        "reason": reason,
        "error": error,
        "model_profile": MODEL_PROFILE,
    }


def _build_body(payload: Mapping[str, Any], teacher: Mapping[str, Any]) -> str:
    student_department = payload.get("student_department", "資訊工程學系")
    student_grade = payload.get("student_grade")
    identity_parts = [str(student_department)]
    if student_grade:
        identity_parts.append(str(student_grade))
    identity = "".join(identity_parts)

    background = str(payload.get("background") or "").strip()
    background_line = f"\n{background}" if background else ""

    return (
        f"{teacher['name'][0]}老師您好：\n\n"
        f"我是{identity}學生{payload['student_name']}。"
        f"{payload['request_details']}。{background_line}\n\n"
        "謝謝老師撥冗閱讀。\n\n"
        f"學生 {payload['student_name']} 敬上"
    )


def create_email_draft(
    payload: Mapping[str, Any],
    *,
    provider_mode: str = "normal",
) -> tuple[int, dict[str, Any]]:
    """Return an HTTP-like status and structured response.

    ``provider_mode`` is an internal test dependency. It is deliberately not a
    request field. ``ungrounded`` simulates a structurally valid but incorrect
    recipient produced by a provider.
    """

    normalized = {
        key: value.strip() if isinstance(value, str) else value
        for key, value in payload.items()
    }
    missing_fields = [
        field
        for field in REQUIRED_FIELDS
        if not isinstance(normalized.get(field), str) or not normalized[field]
    ]
    if missing_fields:
        return _failure(
            422,
            reason="缺少必要輸入欄位。",
            code="MISSING_REQUIRED_FIELD",
            missing_fields=missing_fields,
        )

    purpose = normalized["purpose"]
    if purpose not in PURPOSE_LABELS:
        return _failure(
            422,
            reason="寄信目的不在允許清單中。",
            code="INVALID_PURPOSE",
            intent=purpose,
        )

    if len(normalized["request_details"]) < 5:
        return _failure(
            422,
            reason="詢問內容至少需要 5 個字。",
            code="INVALID_REQUEST_DETAILS",
            intent=purpose,
        )

    teacher = TEACHER_FIXTURE.get(normalized["teacher_name"])
    if teacher is None:
        return _failure(
            404,
            reason="固定資料中找不到名稱完全相符的教師。",
            code="TEACHER_NOT_FOUND",
            intent=purpose,
        )

    if not teacher.get("email"):
        return _failure(
            409,
            reason="教師資料中沒有公開 Email。",
            code="EMAIL_NOT_AVAILABLE",
            intent=purpose,
        )

    recipient = (
        "fake@example.edu.tw"
        if provider_mode == "ungrounded"
        else teacher["email"]
    )
    draft = {
        "to": recipient,
        "subject": PURPOSE_LABELS[purpose],
        "body": _build_body(normalized, teacher),
    }

    if draft["to"] != teacher["email"]:
        return _failure(
            502,
            reason="郵件收件人無法通過固定資料驗證。",
            code="UNGROUNDED_EMAIL",
            intent=purpose,
        )

    teacher_response = deepcopy(teacher)
    return 200, {
        "can_fulfill": True,
        "intent": purpose,
        "teacher": teacher_response,
        "email_draft": draft,
        "sources": [
            {
                "type": "department_website",
                "url": teacher["profile_url"],
            }
        ],
        "requires_confirmation": True,
        "send_status": "not_sent",
        "reason": "已從固定教師資料中找到聯絡資訊並產生郵件草稿。",
        "error": None,
        "model_profile": MODEL_PROFILE,
    }

