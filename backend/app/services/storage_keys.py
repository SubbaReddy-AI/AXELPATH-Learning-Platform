def media_key(category: str, filename: str) -> str:
    category = category.strip("/ ").replace("\\\\", "/")
    return f"axelpath/media/{category}/{filename}"


def course_key(domain_id: int, filename: str = "course.json") -> str:
    return f"axelpath/courses/{domain_id}/{filename}"


def recording_key(domain_id: int, recording_id: int, filename: str = "video") -> str:
    return f"axelpath/recordings/{domain_id}/{recording_id}/{filename}"


def recording_metadata_key(domain_id: int, recording_id: int) -> str:
    return f"axelpath/recordings/{domain_id}/{recording_id}/metadata.json"


def quiz_key(domain_id: int, quiz_id: int) -> str:
    return f"axelpath/quizzes/{domain_id}/{quiz_id}/quiz.json"


def quiz_attempt_key(student_id: int, quiz_id: int, attempt_id: int) -> str:
    return f"axelpath/quiz-attempts/{student_id}/{quiz_id}/{attempt_id}.json"


def assignment_key(domain_id: int, assignment_id: int, filename: str = "assignment.json") -> str:
    return f"axelpath/assignments/{domain_id}/{assignment_id}/{filename}"


def assignment_submission_key(student_id: int, assignment_id: int, submission_id: int, filename: str) -> str:
    return f"axelpath/assignment-submissions/{student_id}/{assignment_id}/{submission_id}/{filename}"


def project_key(domain_id: int, project_id: int, filename: str = "project.json") -> str:
    return f"axelpath/projects/{domain_id}/{project_id}/{filename}"


def project_submission_key(student_id: int, project_id: int, submission_id: int, filename: str) -> str:
    return f"axelpath/project-submissions/{student_id}/{project_id}/{submission_id}/{filename}"
