import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.question_bank import QuestionBank
from app.models.question import Question
from app.models.progress import Progress
from app.models.wrong_question import WrongQuestion
from app.models.user import User
from app.schemas.progress import SubmitAnswerRequest, SubmitExamRequest
from app.utils.deps import get_current_user

router = APIRouter()


def _check_answer(correct_answer, user_answer) -> bool:
    if isinstance(correct_answer, list):
        return sorted(correct_answer) == sorted(user_answer if isinstance(user_answer, list) else [user_answer])
    else:
        return user_answer == correct_answer


@router.get("/{bank_id}")
def get_progress(
    bank_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bank = db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="题库不存在")

    total = db.query(Question).filter(Question.bank_id == bank_id).count()
    answered = db.query(Progress).filter(
        Progress.user_id == current_user.id,
        Progress.bank_id == bank_id,
    ).all()

    answered_q_ids = set()
    correct_count = 0
    for p in answered:
        if p.question_id not in answered_q_ids:
            answered_q_ids.add(p.question_id)
            if p.is_correct:
                correct_count += 1

    wrong_count = db.query(WrongQuestion).filter(
        WrongQuestion.user_id == current_user.id,
        WrongQuestion.bank_id == bank_id,
        WrongQuestion.resolved == False,
    ).count()

    seq_records = db.query(Progress).filter(
        Progress.user_id == current_user.id,
        Progress.bank_id == bank_id,
        Progress.mode == "seq",
    ).count()

    return {
        "total_questions": total,
        "answered_count": len(answered_q_ids),
        "correct_count": correct_count,
        "accuracy": (correct_count / len(answered_q_ids) * 100) if answered_q_ids else 0,
        "wrong_count": wrong_count,
        "seq_index": seq_records,
    }


@router.post("/answer")
def submit_answer(
    req: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Question).filter(Question.id == req.question_id).first()
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="题目不存在")

    correct_answer = json.loads(q.answer)
    is_correct = _check_answer(correct_answer, req.user_answer)

    progress = Progress(
        user_id=current_user.id,
        question_id=req.question_id,
        bank_id=req.bank_id,
        mode=req.mode,
        user_answer=json.dumps(req.user_answer),
        is_correct=is_correct,
    )
    db.add(progress)

    if not is_correct:
        existing_wrong = db.query(WrongQuestion).filter(
            WrongQuestion.user_id == current_user.id,
            WrongQuestion.question_id == req.question_id,
        ).first()
        if not existing_wrong:
            wrong = WrongQuestion(
                user_id=current_user.id,
                question_id=req.question_id,
                bank_id=req.bank_id,
            )
            db.add(wrong)
    else:
        db.query(WrongQuestion).filter(
            WrongQuestion.user_id == current_user.id,
            WrongQuestion.question_id == req.question_id,
        ).update({"resolved": True})

    db.commit()

    return {
        "is_correct": is_correct,
        "correct_answer": correct_answer,
        "analysis": q.analysis or "",
    }


@router.post("/submit-exam")
def submit_exam(
    req: SubmitExamRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exam_record_id = int(datetime.now().timestamp())
    score = 0
    total = 0
    results = {}

    for q_id_str, user_ans in req.answers.items():
        q_id = int(q_id_str)
        q = db.query(Question).filter(Question.id == q_id).first()
        if not q:
            continue
        correct_answer = json.loads(q.answer)
        is_correct = _check_answer(correct_answer, user_ans)

        progress = Progress(
            user_id=current_user.id,
            question_id=q_id,
            bank_id=req.bank_id,
            mode="random",
            user_answer=json.dumps(user_ans),
            is_correct=is_correct,
            exam_record_id=exam_record_id,
        )
        db.add(progress)

        if is_correct:
            score += 5
        else:
            existing_wrong = db.query(WrongQuestion).filter(
                WrongQuestion.user_id == current_user.id,
                WrongQuestion.question_id == q_id,
            ).first()
            if not existing_wrong:
                wrong = WrongQuestion(
                    user_id=current_user.id,
                    question_id=q_id,
                    bank_id=req.bank_id,
                )
                db.add(wrong)

        total += 1
        results[q_id_str] = {"is_correct": is_correct, "correct_answer": correct_answer, "user_answer": user_ans}

    db.commit()

    return {
        "score": score,
        "total": total,
        "max_score": total * 5,
        "exam_record_id": exam_record_id,
        "results": results,
    }


@router.get("/{bank_id}/random-records")
def get_random_records(
    bank_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    records = db.query(Progress).filter(
        Progress.user_id == current_user.id,
        Progress.bank_id == bank_id,
        Progress.mode == "random",
    ).order_by(Progress.answered_at.desc()).all()

    exam_groups: dict[int, list] = {}
    for r in records:
        if r.exam_record_id:
            if r.exam_record_id not in exam_groups:
                exam_groups[r.exam_record_id] = []
            exam_groups[r.exam_record_id].append(r)

    result = []
    for exam_id, items in exam_groups.items():
        score = sum(5 for it in items if it.is_correct)
        result.append({
            "exam_record_id": exam_id,
            "time": items[0].answered_at.strftime("%Y-%m-%d %H:%M:%S") if items else "",
            "score": score,
        })

    result.sort(key=lambda x: x["time"], reverse=True)
    return result


@router.get("/{bank_id}/seq-index")
def get_seq_index(
    bank_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = db.query(Progress).filter(
        Progress.user_id == current_user.id,
        Progress.bank_id == bank_id,
        Progress.mode == "seq",
    ).count()
    return {"seq_index": count}
