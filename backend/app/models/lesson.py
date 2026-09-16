import enum
from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, Text, Enum, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.section import Section
    from app.models.progress import LessonProgress
    from app.models.quiz import Quiz
    from app.models.assignment import Assignment


class LessonType(str, enum.Enum):
    VIDEO = "video"
    ARTICLE = "article"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    lesson_type: Mapped[LessonType] = mapped_column(
        Enum(LessonType, values_callable=lambda obj: [e.value for e in obj]),
        default=LessonType.VIDEO,
        nullable=False,
    )
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    video_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    pdf_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_preview: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    section: Mapped["Section"] = relationship("Section", back_populates="lessons")
    progresses: Mapped[List["LessonProgress"]] = relationship("LessonProgress", back_populates="lesson", cascade="all, delete-orphan")
    quiz: Mapped[Optional["Quiz"]] = relationship("Quiz", back_populates="lesson", uselist=False, cascade="all, delete-orphan")
    assignment: Mapped[Optional["Assignment"]] = relationship("Assignment", back_populates="lesson", uselist=False, cascade="all, delete-orphan")
