"""导入现有 JSON 数据到 SQLite 数据库"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, init_db
from app.models.user import User
from app.models.question_bank import QuestionBank
from app.models.question import Question
from app.utils.security import hash_password

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    init_db()
    db = SessionLocal()

    try:
        # 导入用户
        users_file = os.path.join(PROJECT_DIR, "users_db.json")
        if os.path.exists(users_file):
            with open(users_file, "r", encoding="utf-8") as f:
                users = json.load(f)
            for username, password in users.items():
                existing = db.query(User).filter(User.username == username).first()
                if not existing:
                    db.add(User(username=username, password_hash=hash_password(password)))
            print(f"Imported users: {list(users.keys())}")

        # 导入题库 (questions.json)
        questions_file = os.path.join(PROJECT_DIR, "questions.json")
        if os.path.exists(questions_file):
            with open(questions_file, "r", encoding="utf-8") as f:
                questions = json.load(f)

            bank_name = os.path.splitext(os.path.basename(questions_file))[0]
            bank = db.query(QuestionBank).filter(QuestionBank.name == bank_name).first()
            if not bank:
                bank = QuestionBank(name=bank_name, description="默认题库")
                db.add(bank)
                db.flush()

            for i, q_data in enumerate(questions):
                question = Question(
                    bank_id=bank.id,
                    question_text=q_data["question"],
                    options=json.dumps(q_data["options"], ensure_ascii=False),
                    answer=json.dumps(q_data["answer"]),
                    analysis=q_data.get("analysis", ""),
                    sort_order=i,
                )
                db.add(question)
            print(f"Imported {len(questions)} questions into bank '{bank_name}'")

        db.commit()
        print("Data migration completed!")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
