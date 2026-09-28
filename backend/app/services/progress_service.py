from datetime import datetime
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.domain import StudentDomain, DomainAccessStatus
from app.models.recording import Recording, VideoProgress
from app.models.quiz import Quiz, QuizAttempt
from app.models.assignment import Assignment, AssignmentSubmission
from app.models.project import Project, ProjectSubmission
from app.models.student_progress import StudentProgressSummary


def _pct(done, total):
    return round((float(done) / float(total) * 100.0) if total else 0.0, 2)

def _latest_by(items, key):
    result = {}
    for item in items:
        k = key(item)
        if k not in result or (item.submitted_at or item.created_at or datetime.min) > (result[k].submitted_at or result[k].created_at or datetime.min):
            result[k] = item
    return result

def calculate_student_progress(db: Session, student_id: int) -> StudentProgressSummary:
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise ValueError("Student not found")
    domain_ids = [x.domain_id for x in db.query(StudentDomain).filter(StudentDomain.student_id == student_id, StudentDomain.status == DomainAccessStatus.active).all()]

    recordings = db.query(Recording).filter(Recording.domain_id.in_(domain_ids), Recording.is_published == True).all() if domain_ids else []
    rec_ids = [x.id for x in recordings]
    video_rows = db.query(VideoProgress).filter(VideoProgress.student_id == student_id, VideoProgress.recording_id.in_(rec_ids)).all() if rec_ids else []
    completed_rec_ids = {x.recording_id for x in video_rows if x.is_completed}

    quizzes = db.query(Quiz).filter(Quiz.domain_id.in_(domain_ids), Quiz.is_published == True).all() if domain_ids else []
    quiz_ids = [x.id for x in quizzes]
    attempts = db.query(QuizAttempt).filter(QuizAttempt.student_id == student_id, QuizAttempt.quiz_id.in_(quiz_ids)).all() if quiz_ids else []
    submitted_attempts = [x for x in attempts if str(getattr(x.status, 'value', x.status)) == 'submitted' or x.submitted_at is not None]
    latest_attempts = _latest_by(submitted_attempts, lambda x: x.quiz_id)
    quiz_completed = len(latest_attempts)
    quiz_marks_obtained = sum(float(x.score or 0) for x in latest_attempts.values())
    quiz_marks_total = sum(float(q.total_marks or 0) for q in quizzes)

    assignments = db.query(Assignment).filter(Assignment.domain_id.in_(domain_ids), Assignment.is_published == True).all() if domain_ids else []
    assignment_ids = [x.id for x in assignments]
    assignment_subs = db.query(AssignmentSubmission).filter(AssignmentSubmission.student_id == student_id, AssignmentSubmission.assignment_id.in_(assignment_ids)).all() if assignment_ids else []
    latest_assignment_subs = _latest_by(assignment_subs, lambda x: x.assignment_id)
    assignment_completed = len(latest_assignment_subs)
    assignment_marks_obtained = sum(float(x.marks_obtained or 0) for x in latest_assignment_subs.values())
    assignment_marks_total = sum(float(x.max_marks or 0) for x in assignments)

    projects = db.query(Project).filter(Project.domain_id.in_(domain_ids), Project.is_published == True).all() if domain_ids else []
    project_ids = [x.id for x in projects]
    project_subs = db.query(ProjectSubmission).filter(ProjectSubmission.student_id == student_id, ProjectSubmission.project_id.in_(project_ids)).all() if project_ids else []
    latest_project_subs = _latest_by(project_subs, lambda x: x.project_id)
    project_completed = len(latest_project_subs)
    project_marks_obtained = sum(float(x.marks_obtained or 0) for x in latest_project_subs.values())
    project_marks_total = sum(float(x.max_marks or 0) for x in projects)

    rec_total, rec_completed = len(recordings), len(completed_rec_ids)
    quiz_total = len(quizzes)
    assignment_total = len(assignments)
    project_total = len(projects)
    total_items = rec_total + quiz_total + assignment_total + project_total
    completed_items = rec_completed + quiz_completed + assignment_completed + project_completed

    total_marks = quiz_marks_total + assignment_marks_total + project_marks_total
    marks_obtained = quiz_marks_obtained + assignment_marks_obtained + project_marks_obtained

    activities = []
    activities += [x.last_watched_at for x in video_rows if x.last_watched_at]
    activities += [x.submitted_at for x in submitted_attempts if x.submitted_at]
    activities += [x.submitted_at for x in assignment_subs if x.submitted_at]
    activities += [x.submitted_at for x in project_subs if x.submitted_at]
    last_activity = max(activities) if activities else None

    summary = db.query(StudentProgressSummary).filter(StudentProgressSummary.student_id == student_id).first()
    if not summary:
        summary = StudentProgressSummary(student_id=student_id)
        db.add(summary)

    summary.recordings_total = rec_total
    summary.recordings_completed = rec_completed
    summary.recordings_percentage = _pct(rec_completed, rec_total)
    summary.quizzes_total = quiz_total
    summary.quizzes_completed = quiz_completed
    summary.quizzes_percentage = _pct(quiz_completed, quiz_total)
    summary.quizzes_marks_obtained = quiz_marks_obtained
    summary.quizzes_marks_total = quiz_marks_total
    summary.assignments_total = assignment_total
    summary.assignments_completed = assignment_completed
    summary.assignments_percentage = _pct(assignment_completed, assignment_total)
    summary.assignments_marks_obtained = assignment_marks_obtained
    summary.assignments_marks_total = assignment_marks_total
    summary.projects_total = project_total
    summary.projects_completed = project_completed
    summary.projects_percentage = _pct(project_completed, project_total)
    summary.projects_marks_obtained = project_marks_obtained
    summary.projects_marks_total = project_marks_total
    summary.total_items = total_items
    summary.completed_items = completed_items
    summary.pending_items = max(total_items - completed_items, 0)
    summary.overall_percentage = _pct(completed_items, total_items)
    summary.total_marks = total_marks
    summary.marks_obtained = marks_obtained
    summary.marks_percentage = _pct(marks_obtained, total_marks)
    summary.last_activity_at = last_activity
    db.flush()
    return summary

def summary_to_dict(summary: StudentProgressSummary) -> dict:
    return {
        "recordings": {"total": summary.recordings_total, "completed": summary.recordings_completed, "pending": max(summary.recordings_total-summary.recordings_completed,0), "percentage": float(summary.recordings_percentage or 0)},
        "quizzes": {"total": summary.quizzes_total, "completed": summary.quizzes_completed, "pending": max(summary.quizzes_total-summary.quizzes_completed,0), "percentage": float(summary.quizzes_percentage or 0), "marks_obtained": float(summary.quizzes_marks_obtained or 0), "marks_total": float(summary.quizzes_marks_total or 0)},
        "assignments": {"total": summary.assignments_total, "completed": summary.assignments_completed, "pending": max(summary.assignments_total-summary.assignments_completed,0), "percentage": float(summary.assignments_percentage or 0), "marks_obtained": float(summary.assignments_marks_obtained or 0), "marks_total": float(summary.assignments_marks_total or 0)},
        "projects": {"total": summary.projects_total, "completed": summary.projects_completed, "pending": max(summary.projects_total-summary.projects_completed,0), "percentage": float(summary.projects_percentage or 0), "marks_obtained": float(summary.projects_marks_obtained or 0), "marks_total": float(summary.projects_marks_total or 0)},
        "total_items": summary.total_items, "completed_items": summary.completed_items, "pending_items": summary.pending_items, "overall_percentage": float(summary.overall_percentage or 0),
        "marks": {"total": float(summary.total_marks or 0), "obtained": float(summary.marks_obtained or 0), "percentage": float(summary.marks_percentage or 0)},
        "last_activity_at": summary.last_activity_at,
    }
