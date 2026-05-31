from datetime import datetime, timezone
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Progress(Base):
    __tablename__ = "progress"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"), nullable=False)
    bank_id: Mapped[int] = mapped_column(Integer, ForeignKey("question_banks.id"), nullable=False)
    mode: Mapped[str] = mapped_column(String(20), default="seq")
    user_answer: Mapped[str] = mapped_column(String(200), default="")
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    exam_record_id: Mapped[int] = mapped_column(Integer, nullable=True)
    answered_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("app.models.user.User", back_populates="progress_records")
    question = relationship("app.models.question.Question", back_populates="progress_records")
