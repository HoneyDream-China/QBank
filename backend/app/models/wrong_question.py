from datetime import datetime, timezone
from sqlalchemy import Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WrongQuestion(Base):
    __tablename__ = "wrong_questions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"), nullable=False)
    bank_id: Mapped[int] = mapped_column(Integer, ForeignKey("question_banks.id"), nullable=False)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("app.models.user.User", back_populates="wrong_questions")
    question = relationship("app.models.question.Question", back_populates="wrong_question_records")
    bank = relationship("app.models.question_bank.QuestionBank", back_populates="wrong_questions")
