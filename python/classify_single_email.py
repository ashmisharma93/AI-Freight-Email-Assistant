import json
import sys

ALLOWED_CATEGORIES = {
    "quote_request",
    "shipment_status",
    "documentation_request",
    "other",
}

def classify_email(subject, body):
    text = f"{subject}{body}".lower()

    if any(word in text for word in ["quotation", "quote", "freight charges", "pricing"]):
        return "quote_request"


    if any(word in text for word in ["bill of lading", "commercial invoice", "customs clearance", "documents", "document request"]):
        return "documentation_request"

    if any(word in text for word in ["shipment_status", "shipment update", "tracking", "dispatched", "arrived", "shipment shp"]):
        return "shipment_status"

    return "other"

def main():
    try:
        email = json.load(sys.stdin)
        email_id = email.get("email_id", "")
        subject = email.get("subject", "")
        body = email.get("body", "")

        if not isinstance(subject,str) or not isinstance(body,str):
            raise ValueError("Subject and body must be strings.")

        if not subject.strip() and not body.strip():
            raise ValueError("Email subject and body cannot both be empty.")

        category = classify_email(subject, body)

        if category not in ALLOWED_CATEGORIES:
            raise ValueError(f"Invalid category: {category}")


        result = {
            "email_id": email_id,
            "subject": subject,
            "category": category,
            "needs_human_review": True,
        }

        print(json.dumps(result))

    except (json.JSONDecodeError, ValueError) as error:
        print(json.dumps({"error": str(error)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
