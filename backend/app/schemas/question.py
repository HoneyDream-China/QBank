import json

from pydantic import BaseModel, field_validator
from typing import Union, List


class QuestionBankCreate(BaseModel):
    name: str
    description: str = ""


class QuestionBankUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class QuestionBankResponse(BaseModel):
    id: int
    name: str
    description: str
    question_count: int = 0

    class Config:
        from_attributes = True


class QuestionCreate(BaseModel):
    question_text: str
    options: list[str]
    answer: int | list[int]
    analysis: str = ""

    @field_validator("answer")
    @classmethod
    def validate_answer(cls, v):
        if isinstance(v, int) and v < 0:
            raise ValueError("答案索引不能为负数")
        if isinstance(v, list) and not v:
            raise ValueError("多选题答案列表不能为空")
        return v


class QuestionUpdate(BaseModel):
    question_text: str | None = None
    options: list[str] | None = None
    answer: int | list[int] | None = None
    analysis: str | None = None


class QuestionResponse(BaseModel):
    id: int
    bank_id: int
    question_text: str
    options: list[str]
    answer: int | list[int]
    analysis: str
    sort_order: int

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_json(cls, obj):
        return cls(
            id=obj.id,
            bank_id=obj.bank_id,
            question_text=obj.question_text,
            options=json.loads(obj.options),
            answer=json.loads(obj.answer),
            analysis=obj.analysis,
            sort_order=obj.sort_order,
        )
