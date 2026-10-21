from pathlib import Path
import pandas as pd
import json

ALLOWED_CATEGORIES = {
    "quote_request",
    "shipment_status",
    "documentation_request",
    "other",
}


def classify_email(subject, body):
    """Classify an email using simple keyword rules."""

    text = f"{subject} {body}".lower()

    if any(word in text for word in [
        "quotation",
        "quote",
        "freight charges",
        "pricing",
    ]):
        return "quote_request"

    if any(word in text for word in [
        "bill of lading",
        "commercial invoice",
        "customs clearance",
        "documents",
        "document request",
    ]):
        return "documentation_request"


    if any(word in text for word in [
        "shipment_status",
        "shipment update",
        "tracking",
        "dispatched",
        "arrived",
        "shipment shp"
    ]):
        return "shipment_status"



    return "other"


def main():
    project_root = Path(__file__).resolve().parent.parent
    input_path = project_root/"sample_emails.csv"
    output_path = project_root/"output"/"classified_emails.csv"

    df = pd.read_csv(input_path)

    df['category'] = df.apply(lambda row: classify_email(row["subject"], row["body"]),axis = 1)
    df['needs_human_review'] = True

    invalid_categories = set(df["category"]) - ALLOWED_CATEGORIES
    if invalid_categories:
        raise ValueError(f"Invalid categories found: {invalid_categories}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    results = df.to_dict(orient="records")
    print(json.dumps(results))

    print(f"Classified emails saved to: {output_path}", file=__import__("sys").stderr)

if __name__ == "__main__":
    main()