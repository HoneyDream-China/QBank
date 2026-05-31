from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    bank_id: Mapped[int] = mapped_column(Integer, ForeignKey("question_banks.id"), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(String(50), nullable=False)
    analysis: Mapped[str] = mapped_column(Text, default="")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    bank = relationship("app.models.question_bank.QuestionBank", back_populates="questions")
    progress_records = relationship("app.models.progress.Progress", back_populates="question", cascade="all, delete-orphan")
    wrong_question_records = relationship("app.models.wrong_question.WrongQuestion", back_populates="question", cascade="all, delete-orphan")
