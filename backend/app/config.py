import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'quiz.db')}")

SECRET_KEY = os.getenv("SECRET_KEY", "quiz-system-secret-key-change-in-production")
if SECRET_KEY == "quiz-system-secret-key-change-in-production":
    print("[WARN] SECRET_KEY is using the default value. Set the SECRET_KEY env var for production.", file=sys.stderr)

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
