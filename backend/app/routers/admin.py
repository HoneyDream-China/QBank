"""管理员专用 API：PDF 上传提取题目 + 题库题目批量管理"""
import json
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.user import User
from app.models.question_bank import QuestionBank
from app.models.question import Question
from app.models.progress import Progress
from app.models.wrong_question import WrongQuestion
from app.utils.deps import get_admin_user
from app.services.pdf_extractor import extract_questions_from_pdf

router = APIRouter(prefix="/admin", tags=["管理员"])


# ===================== 统计 =====================

@router.get("/stats")
def get_stats(db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    user_count = db.query(func.count(User.id)).scalar()
    bank_count = db.query(func.count(QuestionBank.id)).scalar()
    question_count = db.query(func.count(Question.id)).scalar()
    return {
        "user_count": user_count,
        "bank_count": bank_count,
        "question_count": question_count,
    }


# ===================== PDF 上传与提取 =====================

@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    target_bank_id: Optional[int] = Form(None),
    bank_name: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="请上传 PDF 文件")

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="PDF 文件为空")

    try:
        extracted = extract_questions_from_pdf(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 解析失败: {str(e)}")

    return {
        "filename": file.filename,
        "choice_questions": extracted["choice_questions"],
        "true_false_questions": extracted["true_false_questions"],
        "fill_blank_questions": extracted["fill_blank_questions"],
        "total": extracted["total"],
        "raw_text_preview": extracted["raw_text_preview"],
    }


class BatchImportRequest:
    pass


@router.post("/import-questions")
async def import_questions(
    target_bank_id: int = Form(...),
    questions_json: str = Form(...),
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    """将提取的题目批量导入到指定题库"""
    bank = db.query(QuestionBank).filter(QuestionBank.id == target_bank_id).first()
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")

    try:
        questions = json.loads(questions_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="题目数据格式错误")

    if not isinstance(questions, list) or len(questions) == 0:
        raise HTTPException(status_code=400, detail="题目列表为空")

    max_order = db.query(func.max(Question.sort_order)).filter(Question.bank_id == target_bank_id).scalar() or 0
    imported = 0

    for q_data in questions:
        options = q_data.get("options", [])
        answer = q_data.get("answer", 0)

        # 填空题特殊处理：无选项，答案存入 analysis 字段辅助展示
        if not options:
            options = ["________"]

        question = Question(
            bank_id=target_bank_id,
            question_text=q_data.get("question_text", ""),
            options=json.dumps(options, ensure_ascii=False),
            answer=json.dumps(answer),
            analysis=q_data.get("analysis", ""),
            sort_order=max_order + imported,
        )
        db.add(question)
        imported += 1

    db.commit()
    return {"imported": imported, "bank_id": target_bank_id, "bank_name": bank.name}


@router.post("/create-bank-with-questions")
async def create_bank_with_questions(
    bank_name: str = Form(...),
    bank_description: str = Form(""),
    questions_json: str = Form(...),
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    """创建新题库并批量导入题目"""
    existing = db.query(QuestionBank).filter(QuestionBank.name == bank_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="题库名称已存在")

    try:
        questions = json.loads(questions_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="题目数据格式错误")

    if not isinstance(questions, list) or len(questions) == 0:
        raise HTTPException(status_code=400, detail="题目列表为空")

    bank = QuestionBank(name=bank_name, description=bank_description)
    db.add(bank)
    db.flush()

    for i, q_data in enumerate(questions):
        options = q_data.get("options", [])
        if not options:
            options = ["________"]
        answer = q_data.get("answer", 0)

        question = Question(
            bank_id=bank.id,
            question_text=q_data.get("question_text", ""),
            options=json.dumps(options, ensure_ascii=False),
            answer=json.dumps(answer),
            analysis=q_data.get("analysis", ""),
            sort_order=i,
        )
        db.add(question)

    db.commit()
    db.refresh(bank)
    return {"bank_id": bank.id, "bank_name": bank.name, "imported": len(questions)}


# ===================== 题库管理增强 =====================

@router.get("/banks")
def admin_list_banks(db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    banks = db.query(QuestionBank).all()
    result = []
    for b in banks:
        q_count = db.query(func.count(Question.id)).filter(Question.bank_id == b.id).scalar()
        result.append({
            "id": b.id, "name": b.name, "description": b.description or "",
            "question_count": q_count, "created_at": b.created_at.isoformat() if b.created_at else "",
        })
    return result


@router.put("/banks/{bank_id}")
def admin_update_bank(bank_id: int, name: str = Form(...), description: str = Form(""),
                      db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    bank = db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    if name != bank.name:
        dup = db.query(QuestionBank).filter(QuestionBank.name == name, QuestionBank.id != bank_id).first()
        if dup:
            raise HTTPException(status_code=400, detail="题库名称已存在")
    bank.name = name
    bank.description = description
    db.commit()
    return {"id": bank.id, "name": bank.name, "description": bank.description}


@router.delete("/banks/{bank_id}")
def admin_delete_bank(bank_id: int, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    bank = db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    db.delete(bank)
    db.commit()
    return {"message": f"题库「{bank.name}」已删除"}


@router.get("/banks/{bank_id}/questions")
def admin_list_questions(bank_id: int, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    bank = db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    questions = db.query(Question).filter(Question.bank_id == bank_id).order_by(Question.sort_order, Question.id).all()
    return [{
        "id": q.id, "bank_id": q.bank_id, "question_text": q.question_text,
        "options": json.loads(q.options), "answer": json.loads(q.answer),
        "analysis": q.analysis or "", "sort_order": q.sort_order,
    } for q in questions]


@router.post("/banks/{bank_id}/questions")
def admin_create_question(bank_id: int,
                          question_text: str = Form(...),
                          options: str = Form("[]"),
                          answer: str = Form("0"),
                          analysis: str = Form(""),
                          db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    bank = db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    try:
        opts = json.loads(options)
        ans = json.loads(answer)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="选项或答案格式错误")
    max_order = db.query(func.max(Question.sort_order)).filter(Question.bank_id == bank_id).scalar() or 0
    q = Question(bank_id=bank_id, question_text=question_text, options=json.dumps(opts, ensure_ascii=False),
                 answer=json.dumps(ans), analysis=analysis, sort_order=max_order + 1)
    db.add(q)
    db.commit()
    db.refresh(q)
    return {"id": q.id, "question_text": q.question_text}


@router.put("/banks/{bank_id}/questions/{question_id}")
def admin_update_question(bank_id: int, question_id: int,
                          question_text: str = Form(...),
                          options: str = Form("[]"),
                          answer: str = Form("0"),
                          analysis: str = Form(""),
                          db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    q = db.query(Question).filter(Question.id == question_id, Question.bank_id == bank_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="题目不存在")
    try:
        opts = json.loads(options)
        ans = json.loads(answer)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="选项或答案格式错误")
    q.question_text = question_text
    q.options = json.dumps(opts, ensure_ascii=False)
    q.answer = json.dumps(ans)
    q.analysis = analysis
    db.commit()
    db.refresh(q)
    return {"message": "题目已更新", "id": q.id}


@router.delete("/banks/{bank_id}/questions/{question_id}")
def admin_delete_question(bank_id: int, question_id: int, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    q = db.query(Question).filter(Question.id == question_id, Question.bank_id == bank_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="题库不存在")
    db.delete(q)
    db.commit()
    return {"message": "题目已删除"}


# ===================== 用户管理 =====================

@router.get("/users")
def admin_list_users(db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "is_admin": u.is_admin,
             "created_at": u.created_at.isoformat() if u.created_at else ""} for u in users]
