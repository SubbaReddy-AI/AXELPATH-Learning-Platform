from sqlalchemy import Column, DateTime, ForeignKey, Integer, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class StudentProgressSummary(Base):
    __tablename__ = "student_progress_summary"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    recordings_total = Column(Integer, default=0, nullable=False)
    recordings_completed = Column(Integer, default=0, nullable=False)
    recordings_percentage = Column(DECIMAL(6, 2), default=0, nullable=False)
    quizzes_total = Column(Integer, default=0, nullable=False)
    quizzes_completed = Column(Integer, default=0, nullable=False)
    quizzes_percentage = Column(DECIMAL(6, 2), default=0, nullable=False)
    quizzes_marks_obtained = Column(DECIMAL(10, 2), default=0, nullable=False)
    quizzes_marks_total = Column(DECIMAL(10, 2), default=0, nullable=False)
    assignments_total = Column(Integer, default=0, nullable=False)
    assignments_completed = Column(Integer, default=0, nullable=False)
    assignments_percentage = Column(DECIMAL(6, 2), default=0, nullable=False)
    assignments_marks_obtained = Column(DECIMAL(10, 2), default=0, nullable=False)
    assignments_marks_total = Column(DECIMAL(10, 2), default=0, nullable=False)
    projects_total = Column(Integer, default=0, nullable=False)
    projects_completed = Column(Integer, default=0, nullable=False)
    projects_percentage = Column(DECIMAL(6, 2), default=0, nullable=False)
    projects_marks_obtained = Column(DECIMAL(10, 2), default=0, nullable=False)
    projects_marks_total = Column(DECIMAL(10, 2), default=0, nullable=False)
    total_items = Column(Integer, default=0, nullable=False)
    completed_items = Column(Integer, default=0, nullable=False)
    pending_items = Column(Integer, default=0, nullable=False)
    overall_percentage = Column(DECIMAL(6, 2), default=0, nullable=False)
    total_marks = Column(DECIMAL(10, 2), default=0, nullable=False)
    marks_obtained = Column(DECIMAL(10, 2), default=0, nullable=False)
    marks_percentage = Column(DECIMAL(6, 2), default=0, nullable=False)
    last_activity_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    student = relationship("User", backref="progress_summary")
