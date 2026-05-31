from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.wrong_question import WrongQuestion
from app.models.user import User
from app.utils.deps import get_current_user

router = APIRouter()


@router.get("/{bank_id}")
def list_wrong_questions(
    bank_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    records = db.query(WrongQuestion).filter(
        WrongQuestion.user_id == current_user.id,
        WrongQuestion.bank_id == bank_id,
        WrongQuestion.resolved == False,
    ).all()
    return [{"id": r.id, "question_id": r.question_id, "added_at": r.added_at.isoformat() if r.added_at else ""} for r in records]


@router.post("/{bank_id}/{question_id}/resolve")
def resolve_wrong(
    bank_id: int,
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = db.query(WrongQuestion).filter(
        WrongQuestion.user_id == current_user.id,
        WrongQuestion.question_id == question_id,
        WrongQuestion.bank_id == bank_id,
    ).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="错题记录不存在")
    record.resolved = True
    db.commit()
    return {"message": "错题已标记为已解决"}
