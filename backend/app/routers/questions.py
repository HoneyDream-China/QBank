import json
import random

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.question_bank import QuestionBank
from app.models.question import Question
from app.models.user import User
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionResponse
from app.utils.deps import get_current_user, get_admin_user

router = APIRouter()


def _question_to_response(q: Question) -> dict:
    return {
        "id": q.id,
        "bank_id": q.bank_id,
        "question_text": q.question_text,
        "options": json.loads(q.options),
        "answer": json.loads(q.answer),
        "analysis": q.analysis or "",
        "sort_order": q.sort_order,
    }


@router.get("/{bank_id}/questions")
def list_questions(
    bank_id: int,
    mode: str = Query("seq", description="seq / random / wrong"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bank = db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="题库不存在")

    questions = db.query(Question).filter(Question.bank_id == bank_id).order_by(Question.sort_order, Question.id).all()

    if mode == "random":
        questions = random.sample(questions, min(20, len(questions)))
    elif mode == "wrong":
        from app.models.wrong_question import WrongQuestion
        wrong_records = db.query(WrongQuestion).filter(
            WrongQuestion.user_id == current_user.id,
            WrongQuestion.bank_id == bank_id,
            WrongQuestion.resolved == False,
        ).all()
        wrong_q_ids = {r.question_id for r in wrong_records}
        questions = [q for q in questions if q.id in wrong_q_ids]

    return [_question_to_response(q) for q in questions]


@router.get("/{bank_id}/questions/{question_id}")
def get_question(
    bank_id: int,
    question_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Question).filter(Question.id == question_id, Question.bank_id == bank_id).first()
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="题目不存在")
    return _question_to_response(q)


@router.post("/{bank_id}/questions")
def create_question(
    bank_id: int,
    req: QuestionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    bank = db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="题库不存在")

    max_order = db.query(Question).filter(Question.bank_id == bank_id).count()
    q = Question(
        bank_id=bank_id,
        question_text=req.question_text,
        options=json.dumps(req.options, ensure_ascii=False),
        answer=json.dumps(req.answer),
        analysis=req.analysis,
        sort_order=max_order,
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return _question_to_response(q)


@router.put("/{bank_id}/questions/{question_id}")
def update_question(
    bank_id: int,
    question_id: int,
    req: QuestionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    q = db.query(Question).filter(Question.id == question_id, Question.bank_id == bank_id).first()
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="题目不存在")

    if req.question_text is not None:
        q.question_text = req.question_text
    if req.options is not None:
        q.options = json.dumps(req.options, ensure_ascii=False)
    if req.answer is not None:
        q.answer = json.dumps(req.answer)
    if req.analysis is not None:
        q.analysis = req.analysis

    db.commit()
    db.refresh(q)
    return _question_to_response(q)


@router.delete("/{bank_id}/questions/{question_id}")
def delete_question(
    bank_id: int,
    question_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    q = db.query(Question).filter(Question.id == question_id, Question.bank_id == bank_id).first()
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="题目不存在")
    db.delete(q)
    db.commit()
    return {"message": "题目已删除"}
