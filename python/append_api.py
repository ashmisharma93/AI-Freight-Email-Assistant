
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import csv
import os
from pathlib import Path
import pandas as pd

app = FastAPI()

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_DIR / "output" / "gmail_test.csv"

FIELDNAMES = [
    "email_id",
    "thread_id",
    "sender",
    "subject",
    "body",
    "category",
    "needs_human_review",
    "review_status",
]


class EmailRecord(BaseModel):
    email_id: str = ""
    thread_id: str = ""
    sender: str = ""
    subject: str = ""
    body: str = ""
    category: str = "other"
    needs_human_review: bool = True
    review_status: str = "Pending Review"


@app.post("/append-email")
def append_email(email: EmailRecord):
    record = email.model_dump()
    if not record["email_id"].strip():
        raise HTTPException(
            status_code=400,
            detail = "email_id is required"
        )
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    try:
        file_exists = (
            os.path.exists(OUTPUT_FILE)
            and os.path.getsize(OUTPUT_FILE) > 0
        )

        # Avoid adding the same email twice.
        if file_exists:
            with open(
                OUTPUT_FILE, "r", newline="", encoding="utf-8-sig"
            ) as file:
                reader = csv.DictReader(file)
                existing_ids = {
                    row.get("email_id", "") for row in reader
                }

            if record["email_id"] and record["email_id"] in existing_ids:
                return {
                    "success": True,
                    "duplicate": True,
                    "message": "Email already exists; no row added.",
                }

        # Add a newline if the existing file lacks one.
        if file_exists:
            with open(OUTPUT_FILE, "rb") as check:
                check.seek(-1, os.SEEK_END)
                last_byte = check.read(1)

            if last_byte not in (b"\n", b"\r"):
                with open(OUTPUT_FILE, "a", encoding="utf-8") as file:
                    file.write("\n")

        # Append a correctly quoted CSV record.
        with open(
            OUTPUT_FILE, "a", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)

            if not file_exists:
                writer.writeheader()

            writer.writerow(record)

        return {
            "success": True,
            "duplicate": False,
            "email_id": record["email_id"],
            "category": record["category"],
        }

    except (OSError, csv.Error) as error:
        raise HTTPException(status_code=500, detail=str(error))

@app.get("/emails")
def get_emails():
    try:
        if not OUTPUT_FILE.exists():
            return []

        df = pd.read_csv(OUTPUT_FILE, dtype=str).fillna("")
        return df.to_dict(orient="records")

    except pd.errors.EmptyDataError:
        return []

    except (OSError, pd.errors.ParserError) as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to read email data: {error}",
        )