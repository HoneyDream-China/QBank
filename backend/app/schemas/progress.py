from typing import Union, List

from pydantic import BaseModel


class SubmitAnswerRequest(BaseModel):
    question_id: int
    bank_id: int
    user_answer: int | list[int]
    mode: str = "seq"


class SubmitExamRequest(BaseModel):
    bank_id: int
    answers: dict[str, list[int] | int]


class ProgressSummary(BaseModel):
    total_questions: int
    answered_count: int
    correct_count: int
    accuracy: float
    wrong_count: int
    seq_index: int
