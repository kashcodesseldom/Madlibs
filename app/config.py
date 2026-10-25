import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{(BASE_DIR / 'data' / 'madlib.db').as_posix()}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_ANSWER_LENGTH = 40
    MAX_TEMPLATE_LENGTH = 4000
    MAX_BLANKS = 40


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
