import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.question_bank import QuestionBank
from app.models.question import Question
from app.models.user import User
from app.schemas.question import QuestionBankCreate, QuestionBankUpdate, QuestionBankResponse
from app.utils.deps import get_current_user, get_admin_user

router = APIRouter()


@router.get("/", response_model=list[QuestionBankResponse])
def list_banks(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    banks = db.query(QuestionBank).all()
    result = []
    for b in banks:
        count = db.query(func.count(Question.id)).filter(Question.bank_id == b.id).scalar()
        result.append(QuestionBankResponse(
            id=b.id, name=b.name, description=b.description or "", question_count=count
        ))
    return result


@router.post("/", response_model=QuestionBankResponse)
def create_bank(req: QuestionBankCreate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    existing = db.query(QuestionBank).filter(QuestionBank.name == req.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="题库名称已存在")
    bank = QuestionBank(name=req.name, description=req.description)
    db.add(bank)
    db.commit()
    db.refresh(bank)
    return QuestionBankResponse(id=bank.id, name=bank.name, description=bank.description or "", question_count=0)


@router.put("/{bank_id}", response_model=QuestionBankResponse)
def update_bank(bank_id: int, req: QuestionBankUpdate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    bank = db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="题库不存在")
    if req.name is not None:
        existing = db.query(QuestionBank).filter(QuestionBank.name == req.name, QuestionBank.id != bank_id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="题库名称已存在")
        bank.name = req.name
    if req.description is not None:
        bank.description = req.description
    db.commit()
    db.refresh(bank)
    count = db.query(func.count(Question.id)).filter(Question.bank_id == bank.id).scalar()
    return QuestionBankResponse(id=bank.id, name=bank.name, description=bank.description or "", question_count=count)


@router.delete("/{bank_id}")
def delete_bank(bank_id: int, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    bank = db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="题库不存在")
    db.delete(bank)
    db.commit()
    return {"message": "题库已删除"}
