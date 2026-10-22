import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Boolean, Integer, String, Text, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


app = FastAPI()

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    engine = create_engine(
    DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
    if DATABASE_URL.startswith("postgresql://")
    else DATABASE_URL,
    pool_pre_ping=True,
)

else:
    local_db = PROJECT_DIR / "output"/ "freight_emails.db"
    local_db.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{local_db.as_posix()}", connect_args={"check_same_thread": False}, )


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass

class EmailEntry(Base):
    __tablename__ = "emails"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True)
    thread_id: Mapped[str] = mapped_column(String(255), default="")
    sender: Mapped[str] = mapped_column(String(500), default="")
    subject: Mapped[str] = mapped_column(String(1000), default="")
    body: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(100), default="other")
    needs_human_review: Mapped[bool] = mapped_column(
        Boolean, default=True
    )
    review_status: Mapped[str] = mapped_column(
        String(100), default="Pending Review"
    )


class EmailRecord(BaseModel):
    email_id: str = ""
    thread_id: str = ""
    sender: str = ""
    subject: str = ""
    body: str = ""
    category: str = "other"
    needs_human_review: bool = True
    review_status: str = "Pending Review"


@app.on_event("startup")
def create_database_tables():
    Base.metadata.create_all(bind=engine)


@app.post("/append-email")
def append_email(email: EmailRecord):
    record = email.model_dump()

    if not record["email_id"].strip():
        raise HTTPException(
            status_code=400,
            detail="email_id is required",
        )

    try:
        with SessionLocal() as db:
            existing = (
                db.query(EmailEntry)
                .filter(EmailEntry.email_id == record["email_id"])
                .first()
            )

            if existing:
                return {
                    "success": True,
                    "duplicate": True,
                    "message": "Email already exists; no row added.",
                }

            new_email = EmailEntry(**record)
            db.add(new_email)
            db.commit()

            return {
                "success": True,
                "duplicate": False,
                "email_id": record["email_id"],
                "category": record["category"],
            }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Unable to save email to the database.",
        )


@app.get("/emails")
def get_emails():
    try:
        with SessionLocal() as db:
            emails = (
                db.query(EmailEntry)
                .order_by(EmailEntry.id)
                .all()
            )

            # Keep the response compatible with the existing dashboard.
            return [
                {
                    "email_id": email.email_id,
                    "thread_id": email.thread_id,
                    "sender": email.sender,
                    "subject": email.subject,
                    "body": email.body,
                    "category": email.category,
                    "needs_human_review": str(
                        email.needs_human_review
                    ),
                    "review_status": email.review_status,
                }
                for email in emails
            ]

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Unable to read emails from the database.",
        )
