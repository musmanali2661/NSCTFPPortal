"""
AI Service – stubs with clear function signatures.
Replace body implementations with real LLM calls when an OPENAI_API_KEY is available.
"""
from __future__ import annotations

from typing import Optional

from fuzzywuzzy import fuzz


# ---------------------------------------------------------------------------
# Entity matching
# ---------------------------------------------------------------------------

def fuzzy_name_match(name_a: str, name_b: str, threshold: int = 80) -> bool:
    """Return True if two name strings are similar enough (fuzzy match)."""
    ratio = fuzz.token_sort_ratio(name_a.lower(), name_b.lower())
    return ratio >= threshold


def find_best_match(query: str, candidates: list[str], threshold: int = 70) -> Optional[str]:
    """Return the best matching candidate for *query* or None if below threshold."""
    best_score = 0
    best_match: Optional[str] = None
    for candidate in candidates:
        score = fuzz.token_sort_ratio(query.lower(), candidate.lower())
        if score > best_score:
            best_score = score
            best_match = candidate
    return best_match if best_score >= threshold else None


# ---------------------------------------------------------------------------
# Intent recognition
# ---------------------------------------------------------------------------

INTENT_KEYWORDS: dict[str, list[str]] = {
    "transport": ["bus", "transport", "route", "pickup", "drop"],
    "login": ["login", "password", "access", "account", "credential", "sign in"],
    "data_correction": ["wrong", "incorrect", "error", "update", "change", "fix", "name", "cnic", "dob"],
    "general_info": ["when", "what", "how", "where", "fee", "date", "schedule", "exam"],
}


def recognize_intent(text: str) -> str:
    """
    Classify a support query into one of the ticket categories.
    Returns one of: 'Transport', 'Login', 'Data_Correction', 'General_Info'.
    """
    lower = text.lower()
    scores: dict[str, int] = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        scores[intent] = sum(kw in lower for kw in keywords)

    best = max(scores, key=lambda k: scores[k])
    if scores[best] == 0:
        return "General_Info"

    mapping = {
        "transport": "Transport",
        "login": "Login",
        "data_correction": "Data_Correction",
        "general_info": "General_Info",
    }
    return mapping[best]


# ---------------------------------------------------------------------------
# Auto-summary / reply generation
# ---------------------------------------------------------------------------

_REPLY_TEMPLATES: dict[str, str] = {
    "Transport": (
        "Thank you for contacting NSCT support regarding transport services. "
        "Please note that transport routes and schedules are managed by the transport office. "
        "You may visit the transport office or call the dedicated helpline for real-time updates. "
        "If you need to register for transport, please submit a formal request through the portal."
    ),
    "Login": (
        "Thank you for reaching out. For login issues, please try resetting your password using the "
        "'Forgot Password' option on the login page. If the issue persists, contact the IT helpdesk "
        "with your registration number so they can verify your account details."
    ),
    "Data_Correction": (
        "Thank you for reporting a data discrepancy. Please provide the correct information along "
        "with supporting documents (e.g., CNIC copy, birth certificate) to your department's focal "
        "person. Corrections will be reviewed and applied within 2–3 working days."
    ),
    "General_Info": (
        "Thank you for contacting NSCT support. We have received your query and a coordinator will "
        "respond within one working day. For urgent matters, please visit the administrative office "
        "during business hours (Mon–Fri, 9am–5pm)."
    ),
}


def generate_auto_reply(query: str, category: str) -> str:
    """
    Generate a canned / template-based auto reply for a support ticket.
    When OPENAI_API_KEY is configured this can be swapped for an LLM call.
    """
    return _REPLY_TEMPLATES.get(category, _REPLY_TEMPLATES["General_Info"])


def summarize_student_record(student_data: dict) -> str:
    """
    Produce a brief natural-language summary of a student record.
    Stub – returns a formatted string; replace with LLM summarisation as needed.
    """
    return (
        f"Student {student_data.get('full_name', 'N/A')} "
        f"(Reg: {student_data.get('reg_no', 'N/A')}) is enrolled in "
        f"{student_data.get('department', 'N/A')} — "
        f"{student_data.get('batch_type', 'N/A')} batch, "
        f"Semester {student_data.get('semester_no', 'N/A')}. "
        f"Current status: {student_data.get('status', 'N/A')}."
    )
