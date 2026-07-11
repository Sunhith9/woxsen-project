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
        keywords=["lost id", "missing id", "id card lost", "id lost", "misplaced id"],
        steps=[
            Step("Bridge Helpdesk", "Submit your request for a replacement ID card", "Office Hours"),
            Step("Required Documents", "Provide your Student ID Number, Identity Proof, and a Passport Photo (if requested)", None),
            Step("Processing Time", "Approximately 2–7 working days", None)
        ],
        contact="📧 bridge@woxsen.edu.in"
    ),

    DirectAnswer(
        id="fee_issue",
        title="Fee Payment Not Updated / Reflecting",
        keywords=["fee payment", "fee not updated", "payment screenshot", "transaction id", "fee status", "fee problem"],
        steps=[
            Step("Accounts Office", "Provide details of your payment for verification", "Office Hours"),
            Step("Required Information", "Submit your Transaction ID, Payment Screenshot, Date of Payment, and Amount Paid", None),
            Step("Resolution Timeline", "Typical resolution takes 1–3 working days", None)
        ],
        contact="📧 accounts@woxsen.edu.in"
    ),

    DirectAnswer(
        id="attendance_shortage",
        title="Attendance Shortage Policy",
        keywords=["attendance shortage", "attendance low", "shortage of attendance", "attendance issue", "below 75"],
        steps=[
            Step("Course Faculty", "Contact your course faculty to discuss your attendance status", None),
            Step("Program Manager", "If unresolved, escalate the concern to your Program Manager", None),
            Step("Supporting Documents", "Submit medical certificates or relevant approval letters if applicable", None)
        ],
        contact="📧 bridge@woxsen.edu.in"
    ),

    DirectAnswer(
        id="exam_revaluation",
        title="Exam Revaluation Process",
        keywords=["revaluation", "exam reval", "re-evaluation", "marks reval", "revalue"],
        steps=[
            Step("Controller of Examinations", "Apply for paper revaluation", "Office Hours"),
            Step("Required Documents", "Submit your Revaluation Application and Payment Receipt", None),
            Step("Processing Time", "Typical processing takes 2–4 weeks", None)
        ],
        contact="📧 coe@woxsen.edu.in"
    ),

    DirectAnswer(
        id="bonafide_cert",
        title="Apply for Bonafide Certificate",
        keywords=["bonafide", "bonafide certificate", "get bonafide"],
        steps=[
            Step("Bridge Support Desk", "Request a Bonafide Certificate", "Office Hours"),
            Step("Required Details", "Provide your Student ID", None),
            Step("Processing Time", "Ready within 1–3 working days", None)
        ],
        contact="📧 bridge@woxsen.edu.in"
    ),

    DirectAnswer(
        id="transcript",
        title="Apply for Transcripts",
        keywords=["transcript", "transcripts", "official transcript"],
        steps=[
            Step("Bridge Support Desk", "Submit a request for your transcripts", "Office Hours"),
            Step("Required Items", "Submit Application and complete any fee payment (if applicable)", None),
            Step("Processing Time", "Typically ready in 5–10 working days", None)
        ],
        contact="📧 bridge@woxsen.edu.in"
    ),

    DirectAnswer(
        id="transfer_cert",
        title="Apply for Transfer Certificate",
        keywords=["transfer certificate", "migration certificate", "tc and migration", "transfer cert"],
        steps=[
            Step("Registrar Office", "Request a Transfer or Migration Certificate", "Office Hours"),
            Step("Required Documents", "Submit Department Clearance and a No Due Certificate", None),
            Step("Processing Time", "Issued in 5–10 working days", None)
        ],
        contact="📧 registrar@woxsen.edu.in"
    ),

    DirectAnswer(
        id="hostel_room_change",
        title="Hostel Room Change Request",
        keywords=["room change", "change hostel room", "room transfer", "hostel change"],
        steps=[
            Step("Gateway (Hostel Support)", "Submit a room change request", "Office Hours"),
            Step("Requirements", "Submit a Written Request explaining your reason", None),
            Step("Approval", "Approvals depend strictly on room availability", None)
        ],
        contact="📧 thegateway@woxsen.edu.in"
    ),

    DirectAnswer(
        id="wifi_problem",
        title="Hostel Wi-Fi Issues",
        keywords=["hostel wifi", "wi-fi", "wifi issue", "internet not working", "no wifi"],
        steps=[
            Step("IT Help Desk", "Report the Wi-Fi connectivity issue", "Office Hours"),
            Step("Required Information", "Provide your Hostel Room, Student ID, and Device Information", None)
        ],
        contact="📧 techsupport@woxsen.edu.in"
    ),

    DirectAnswer(
        id="erp_login_issue",
        title="ERP Login / Password Reset",
        keywords=["erp login", "erp issue", "erp password", "reset erp"],
        steps=[
            Step("IT Help Desk", "Report access or login issues", "Office Hours"),
            Step("Required Information", "Provide your Roll Number, Registered Email, and a Screenshot of the Error", None)
        ],
        contact="📧 techsupport@woxsen.edu.in"
    ),

    DirectAnswer(
        id="library_book_missing",
        title="Library Book Missing / Unavailable",
        keywords=["book missing", "book not found", "library book missing", "missing book"],
        steps=[
            Step("Library Staff", "Report the missing book at the counter", "Library Hours"),
            Step("Possible Solutions", "Library staff will assist with reservations, alternative copies, or digital access", None)
        ],
        contact="📧 library@woxsen.edu.in"
    ),

    DirectAnswer(
        id="library_book_damaged",
        title="Damaged Library Book Policy",
        keywords=["damaged book", "damaged library book", "book damaged", "ruined book"],
        steps=[
            Step("Library Staff", "Report any damage to the book immediately", "Library Hours"),
            Step("Fine Policy", "Fines or replacement charges will depend on library policy", None)
        ],
        contact="📧 library@woxsen.edu.in"
    ),

    DirectAnswer(
        id="transport_issue",
        title="Bus Route or Transport Issue",
        keywords=["bus route", "transport issue", "bus timing", "university bus", "bus pass"],
        steps=[
            Step("Transport Office", "Submit transportation inquiries or complaints", "Office Hours"),
            Step("Required Information", "Provide your Bus Route and Student ID", None)
        ],
        contact="📧 transport@woxsen.edu.in"
    ),

    DirectAnswer(
        id="medical_leave",
        title="Medical Leave Application",
        keywords=["medical leave", "sick leave", "apply for medical leave", "medical certificate"],
        steps=[
            Step("Course Faculty", "Inform your course faculty about your illness", None),
            Step("Program Manager", "Submit leave request to your Program Manager", None),
            Step("Supporting Documents", "Submit a valid Medical Certificate", None)
        ],
        contact="📧 bridge@woxsen.edu.in"
    ),

    DirectAnswer(
        id="ragging_complaint",
        title="Anti-Ragging Complaint (High Priority)",
        keywords=["ragging", "bully", "harassment", "anti ragging", "anti-ragging"],
        steps=[
            Step("Anti-Ragging Cell", "Contact immediately to report any ragging or harassment", "24/7 Support"),
            Step("Emergency Hotline", "Call the 24/7 emergency numbers: 7416664429 or 9709704747", None)
        ],
        contact="📧 antiragging.cell@woxsen.edu.in",
        note="All ragging complaints are treated with the highest urgency and confidentiality."
    ),

    DirectAnswer(
        id="scholarship_query",
        title="Scholarship Inquiry",
        keywords=["scholarship", "scholarships", "fee deduction"],
        steps=[
            Step("Accounts Office", "Submit scholarship inquiries", "Office Hours"),
            Step("Required Documents", "Bring Scholarship Documents and Income Certificate (if required)", None)
        ],
        contact="📧 accounts@woxsen.edu.in"
    ),

    DirectAnswer(
        id="placement_internship",
        title="Career Placements & Internships",
        keywords=["placement", "internship", "placements", "jobs", "career connect"],
        steps=[
            Step("Career Connect Office", "Inquire about placement drives, resumes, and internship registrations", "Office Hours")
        ],
        contact="📧 careerconnect@woxsen.edu.in"
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
