"""
knowledge_base.py
=================
Layer 1: Direct, rule-based answers for common student issues.
These are returned INSTANTLY without any vector search or LLM call.
Add more entries as you discover recurring queries.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Step:
    place: str
    detail: str
    timing: Optional[str] = None


@dataclass
class DirectAnswer:
    id: str
    title: str
    keywords: list[str]
    steps: list[Step]
    contact: str
    fee: Optional[str] = None
    note: Optional[str] = None


# ─────────────────────────────────────────────
# KNOWLEDGE BASE — Add/edit entries here
# ─────────────────────────────────────────────
KNOWLEDGE_BASE: list[DirectAnswer] = [

    DirectAnswer(
        id="id_lost",
        title="Lost / Missing ID Card",
        keywords=[
            "id card missing", "lost id card", "id missing", "lost my id",
            "id card lost", "misplaced id", "id card chori", "id card kho gaya",
            "id card nahi mila", "missing identity card"
        ],
        steps=[
            Step("Security Office – Block A, Ground Floor",
                 "Report the loss and collect a Loss Complaint Slip",
                 "Mon–Sat, 8AM–8PM"),
            Step("Fee Counter – Accounts Dept, Admin Block Room 201",
                 "Pay ₹200 re-issue fee. Keep the payment receipt.",
                 "Mon–Sat, 9AM–5PM"),
            Step("Admin Office – Room 102",
                 "Collect the ID re-issue form. Attach: complaint slip + fee receipt.",
                 "Mon–Sat, 9AM–5PM"),
            Step("Submit & Collect",
                 "Submit the filled form at Admin Room 102. New ID card ready in 2 working days.",
                 None),
        ],
        contact="📧 admin@woxsen.edu.in | ☎ 040-6810-0100 ext 102",
        fee="₹200",
        note="Bring any other photo ID (Aadhaar/Passport) when visiting the Security Office."
    ),

    DirectAnswer(
        id="id_new",
        title="Apply for a New ID Card (Fresh Student)",
        keywords=[
            "new id card", "get id card", "apply id card", "id card kaise milega",
            "how to get id card", "fresh id", "id card banwana", "id card apply"
        ],
        steps=[
            Step("Admin Office – Room 102",
                 "Collect the ID card application form",
                 "Mon–Sat, 9AM–5PM"),
            Step("Fee Counter – Accounts Dept, Room 201",
                 "Pay ₹150 (first-time) at the fee counter. Keep receipt.",
                 "Mon–Sat, 9AM–5PM"),
            Step("Photo & Documents",
                 "Submit: 2 passport-size photos + fee receipt + admission letter at Admin Room 102",
                 None),
            Step("Collection",
                 "Collect your ID card after 2–3 working days from Admin Room 102",
                 None),
        ],
        contact="📧 admin@woxsen.edu.in | ☎ 040-6810-0100 ext 102",
        fee="₹150 (first-time)"
    ),

    DirectAnswer(
        id="id_damaged",
        title="Damaged / Expired ID Card Replacement",
        keywords=[
            "id card damaged", "broken id card", "id card expired", "id card not working",
            "id card replacement", "id card faded", "replace id card"
        ],
        steps=[
            Step("Admin Office – Room 102",
                 "Bring the damaged/expired card. Collect replacement form.",
                 "Mon–Sat, 9AM–5PM"),
            Step("Fee Counter – Room 201",
                 "Pay ₹100 replacement fee. Keep receipt.",
                 None),
            Step("Submit",
                 "Submit: old card + fee receipt + 1 passport-size photo at Admin Room 102",
                 None),
            Step("Collection",
                 "New card ready in 1–2 working days",
                 None),
        ],
        contact="📧 admin@woxsen.edu.in | ☎ 040-6810-0100 ext 102",
        fee="₹100"
    ),

    DirectAnswer(
        id="fee_issue",
        title="Fee Payment Not Reflecting in Portal",
        keywords=[
            "fee not showing", "payment not reflected", "fee issue", "paid fees not updated",
            "fee payment problem", "portal not showing payment", "challan not updated"
        ],
        steps=[
            Step("Accounts Department – Admin Block Room 201",
                 "Visit with your payment receipt / bank screenshot / UTR number",
                 "Mon–Sat, 9AM–5PM"),
            Step("Bank Verification",
                 "Accounts team verifies the transaction with the bank",
                 None),
            Step("Portal Update",
                 "Fee status updated in the portal within 24–48 hours",
                 None),
        ],
        contact="📧 accounts@woxsen.edu.in | ☎ 040-6810-0100 ext 201"
    ),

    DirectAnswer(
        id="hostel",
        title="Hostel Complaint / Issue",
        keywords=[
            "hostel complaint", "hostel issue", "hostel room problem", "hostel maintenance",
            "dorm issue", "hostel wifi", "hostel water", "hostel food complaint"
        ],
        steps=[
            Step("Hostel Warden Office – Block H",
                 "Visit and submit a written complaint with your room number & issue",
                 "Mon–Sat, 8AM–8PM"),
            Step("Resolution Timeline",
                 "Maintenance issues: 24–48 hrs. Other issues: 3–5 working days.",
                 None),
            Step("Escalation",
                 "If unresolved, escalate to Dean of Student Affairs – Admin Block Room 301",
                 None),
        ],
        contact="📧 hostel@woxsen.edu.in | ☎ 040-6810-0100 ext 305"
    ),

    DirectAnswer(
        id="library",
        title="Library Book / Fine Issue",
        keywords=[
            "library fine", "library book", "overdue book", "library card", "book not available",
            "library issue", "library complaint", "return book", "library membership"
        ],
        steps=[
            Step("Library – Counter 3 (Ground Floor)",
                 "Visit with your ID card and student enrollment number",
                 "Mon–Sat, 8AM–9PM | Sun, 10AM–5PM"),
            Step("Fine Payment",
                 "Fines: ₹2/day per book. Pay at Library Counter 1.",
                 None),
            Step("Book Request",
                 "For books not in stock, submit a request form at Counter 3. Available in 7–10 days.",
                 None),
        ],
        contact="📧 library@woxsen.edu.in | ☎ 040-6810-0100 ext 400"
    ),

    DirectAnswer(
        id="exam",
        title="Exam Hall Ticket / Results Issue",
        keywords=[
            "hall ticket", "admit card", "exam schedule", "exam results", "result not showing",
            "grade issue", "marks problem", "exam issue", "revaluation", "supplementary exam"
        ],
        steps=[
            Step("Student Portal – portal.woxsen.edu.in",
                 "Login → Examinations → Download Hall Ticket / View Results",
                 None),
            Step("Exam Cell – Admin Block Room 105",
                 "For portal issues or discrepancies, visit with your enrollment number",
                 "Mon–Fri, 9AM–5PM"),
            Step("Revaluation Request",
                 "Submit revaluation form within 7 days of result declaration. Fee: ₹500/subject.",
                 None),
        ],
        contact="📧 examcell@woxsen.edu.in | ☎ 040-6810-0100 ext 105"
    ),

]


# ─────────────────────────────────────────────
# Lookup function
# ─────────────────────────────────────────────
def find_direct_answer(query: str) -> DirectAnswer | None:
    """
    Returns a DirectAnswer if query matches known issue keywords.
    Uses simple keyword matching — fast, zero cost.
    """
    q = query.lower().strip()
    for item in KNOWLEDGE_BASE:
        if any(kw in q for kw in item.keywords):
            return item
    return None


def direct_answer_to_dict(answer: DirectAnswer) -> dict:
    """Serialize a DirectAnswer for JSON API response."""
    # Build a readable HTML answer string for the frontend chatbot
    parts = [f"<strong>{answer.title}</strong><br><br>"]
    if answer.steps:
        parts.append("<strong>Steps:</strong><ul>")
        for s in answer.steps:
            timing_str = f" (<em>{s.timing}</em>)" if s.timing else ""
            parts.append(f"<li><strong>{s.place}</strong>: {s.detail}{timing_str}</li>")
        parts.append("</ul>")
    if answer.fee:
        parts.append(f"<em>Fee Required:</em> {answer.fee}<br>")
    if answer.note:
        parts.append(f"<em>Note:</em> {answer.note}<br>")
    if answer.contact:
        parts.append(f"<br><strong>Contact:</strong> {answer.contact}")
    readable_answer = "".join(parts)

    return {
        "type": "direct",
        "id": answer.id,
        "title": answer.title,
        "answer": readable_answer,
        "fee": answer.fee,
        "note": answer.note,
        "contact": answer.contact,
        "steps": [
            {"place": s.place, "detail": s.detail, "timing": s.timing}
            for s in answer.steps
        ]
    }
