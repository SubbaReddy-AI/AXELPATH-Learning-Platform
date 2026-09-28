"""Google Sheets integration for student details.

The service-account JSON is read from a local/container-only path configured by
GOOGLE_SERVICE_ACCOUNT_FILE. Passwords and other authentication secrets are
never written to the Sheet.
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import gspread
from google.oauth2.service_account import Credentials

from app.config import settings

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]
HEADERS = [
    "Student ID", "Full Name", "Email", "Phone", "Qualification", "Preferred Domain", "Status",
    "Registered At", "Approved At", "Last Login",
    "Recordings Total", "Recordings Completed", "Recordings Pending", "Recording %",
    "Quizzes Total", "Quizzes Completed", "Quizzes Pending", "Quiz %", "Quiz Marks",
    "Assignments Total", "Assignments Completed", "Assignments Pending", "Assignment %", "Assignment Marks",
    "Projects Total", "Projects Completed", "Projects Pending", "Project %", "Project Marks",
    "Total Items", "Completed Items", "Pending Items", "Overall %", "Total Marks", "Marks Obtained", "Marks %",
    "Last Activity", "Last Updated",
]


def _client() -> gspread.Client:
    credentials_path = Path(settings.GOOGLE_SERVICE_ACCOUNT_FILE)
    if not credentials_path.exists():
        raise FileNotFoundError(
            f"Google service-account JSON not found: {credentials_path}"
        )
    credentials = Credentials.from_service_account_file(
        str(credentials_path), scopes=SCOPES
    )
    return gspread.authorize(credentials)


def _worksheet():
    if not settings.GOOGLE_SPREADSHEET_ID:
        raise ValueError("GOOGLE_SPREADSHEET_ID is not configured")
    client = _client()
    spreadsheet = client.open_by_key(settings.GOOGLE_SPREADSHEET_ID)
    try:
        worksheet = spreadsheet.worksheet(settings.GOOGLE_SHEET_WORKSHEET)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=settings.GOOGLE_SHEET_WORKSHEET, rows=1000, cols=len(HEADERS)
        )
    values = worksheet.get_all_values()
    if not values:
        worksheet.append_row(HEADERS, value_input_option="USER_ENTERED")
    elif values[0][:len(HEADERS)] != HEADERS:
        # Only create the expected header row when the sheet is genuinely empty.
        # Existing user data is never overwritten automatically.
        logger.warning(
            "Google Sheet '%s' has an existing header layout; using it as-is.",
            settings.GOOGLE_SHEET_WORKSHEET,
        )
    return worksheet


def _value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return str(value)


def _student_row(student, db) -> list[str]:
    from app.services.progress_service import calculate_student_progress, summary_to_dict
    progress = summary_to_dict(calculate_student_progress(db, student.id))
    r, q, a, p, m = progress["recordings"], progress["quizzes"], progress["assignments"], progress["projects"], progress["marks"]
    profile = student.profile
    return [
        _value(student.id), _value(profile.full_name if profile else ""), _value(student.email), _value(student.phone),
        _value(profile.qualification if profile else ""), _value(profile.preferred_domain if profile else ""),
        _value(getattr(student.status, "value", student.status)), _value(student.created_at), _value(profile.approved_at if profile else None), _value(student.last_login_at),
        _value(r["total"]), _value(r["completed"]), _value(r["pending"]), _value(r["percentage"]),
        _value(q["total"]), _value(q["completed"]), _value(q["pending"]), _value(q["percentage"]), _value(q["marks_obtained"]),
        _value(a["total"]), _value(a["completed"]), _value(a["pending"]), _value(a["percentage"]), _value(a["marks_obtained"]),
        _value(p["total"]), _value(p["completed"]), _value(p["pending"]), _value(p["percentage"]), _value(p["marks_obtained"]),
        _value(progress["total_items"]), _value(progress["completed_items"]), _value(progress["pending_items"]), _value(progress["overall_percentage"]),
        _value(m["total"]), _value(m["obtained"]), _value(m["percentage"]), _value(progress["last_activity_at"]), _value(datetime.utcnow()),
    ]


def sync_student_to_google_sheet(student, db) -> bool:
    worksheet = _worksheet()
    row = _student_row(student, db)
    values = worksheet.get_all_values()
    existing_row = next((index for index, existing in enumerate(values[1:], start=2) if existing and existing[0].strip() == row[0]), None)
    end_col = _column_letter(len(row))
    if existing_row:
        worksheet.update(f"A{existing_row}:{end_col}{existing_row}", [row], value_input_option="USER_ENTERED")
    else:
        worksheet.append_row(row, value_input_option="USER_ENTERED")
    return True


def _column_letter(number: int) -> str:
    result = ""
    while number:
        number, rem = divmod(number - 1, 26)
        result = chr(65 + rem) + result
    return result


def sync_students_to_google_sheet(students, db) -> dict:
    synced, failed, errors = 0, 0, []
    for student in students:
        try:
            sync_student_to_google_sheet(student, db)
            synced += 1
        except Exception as exc:
            failed += 1
            errors.append(f"student {getattr(student, 'id', '?')}: {exc}")
            logger.exception("Google Sheets sync failed")
    return {"synced": synced, "failed": failed, "errors": errors}
