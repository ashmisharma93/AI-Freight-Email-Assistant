
# AI Freight Operations Assistant

A prototype automation system that collects freight-related emails, classifies them into operational categories, stores them in a CSV file, and supports human review through an Excel workbook.

## Project Overview

Freight operations teams receive emails about quotations, shipment tracking, documentation, and general enquiries. Manually sorting these emails can be repetitive and time-consuming.

This project automates the initial email-processing workflow and provides a structured review process for employees.

## Key Features

- **Email monitoring:** Uses an n8n Gmail Trigger to detect incoming emails.
- **Email normalization:** Extracts email IDs, sender, subject, body, and thread information.
- **Rule-based classification:** Categorizes emails into quotation requests, shipment status enquiries, documentation requests, and other enquiries.
- **API integration:** Uses FastAPI to validate and store email records.
- **CSV storage:** Appends incoming emails to a structured CSV file.
- **Duplicate prevention:** Checks email IDs to avoid inserting duplicate records.
- **Human review:** Marks emails as pending review instead of treating automated classifications as final decisions.
- **Excel review workbook:** Supports filtering, reviewing, and updating email statuses while preserving existing review decisions when new records are imported.

## Technology Stack

- **Language:** Python
- **Workflow automation:** n8n
- **Email integration:** Gmail API
- **Backend API:** FastAPI
- **Data validation:** Pydantic
- **Data storage:** CSV
- **Review interface:** Microsoft Excel
- **Excel workbook automation:** openpyxl

## Email Categories

| Category | Purpose |
|---|---|
| `quote_request` | Freight quotations, rates, and shipping cost enquiries |
| `shipment_status` | Shipment tracking and delivery status enquiries |
| `documentation_request` | Invoices, bills of lading, and shipping documents |
| `other` | Emails that do not match the configured classification rules |

The classifier uses phrase-matching rules. It is not currently an ML- or LLM-based classifier, and unfamiliar or multi-topic emails may be categorized incorrectly.

## Workflow Architecture

1. An email arrives in the connected Gmail account.
2. The n8n Gmail Trigger detects the new message.
3. JavaScript workflow nodes normalize the email fields and apply classification rules.
4. n8n sends the structured record to the FastAPI endpoint.
5. FastAPI validates the request, checks for duplicate email IDs, and appends valid records to the CSV file.
6. The Python workbook update script imports new records into Excel without replacing existing review statuses.
7. An employee reviews the email and updates its review status.

## Project Structure

```text
Prologis_Frieght/
├── README.md
├── requirements.txt
├── sample_emails.csv
├── python/
│   ├── validate_email.py
│   ├── classify_email.py
│   ├── classify_single_email.py
│   ├── append_email.py
│   ├── append_api.py
│   └── update_review_workbook.py
├── n8n/
└── output/
    ├── gmail_test.csv
    └── Freight_Email_Review.xlsx
```

## Setup and Execution

### 1. Activate the Python environment

Activate your configured Conda environment:

```powershell
conda activate p_env
```

### 2. Install dependencies

From the project root:

```powershell
pip install -r requirements.txt
```

### 3. Start the FastAPI service

Run this command from the project root:

```powershell
python -m uvicorn append_api:app --app-dir python --host 127.0.0.1 --port 8000
```

The API documentation is available at:

http://127.0.0.1:8000/docs

Keep the terminal running while the workflow uses the API.

### 4. Configure n8n

- Connect the Gmail account and configure the Gmail Trigger.
- Configure the JavaScript nodes for email normalization and classification.
- Configure the HTTP Request node to send records to `http://127.0.0.1:8000/append-email`.
- Publish the workflow after testing it.

The Gmail workflow requires the FastAPI service to be running and accessible.

### 5. Update the Excel review workbook

Close the Excel workbook before running the update script. From the project root, execute:

```powershell
python .\python\update_review_workbook.py
```

The script reads the CSV, appends new email IDs, preserves existing review statuses, and expands the Excel table.

Open `output/Freight_Email_Review.xlsx` to review the records.

## Review Statuses

- `Pending Review`
- `Reviewed`
- `Needs Follow-up`

Automated classification is intended to assist employees, not replace human review.

## Current Limitations

- Classification is rule-based and depends on configured phrases.
- Classification accuracy has not been established through a formal evaluation.
- The Excel workbook is a separate review copy and does not update automatically when the CSV changes.
- The workbook update script must be run manually after new emails arrive.
- The FastAPI service must remain running for the n8n workflow to append records.
- The prototype has not been validated for production-scale freight operations.

## Future Improvements

- Replace phrase matching with an LLM-assisted classifier or a trained ML model.
- Add confidence scores and more robust multi-topic classification.
- Introduce persistent database storage.
- Automate the review-workbook refresh process.
- Add structured logging, monitoring, and retry handling.
- Evaluate classification quality on a labeled dataset.
- Add role-based access controls and secure deployment configuration.

## Project Goal

Demonstrate how workflow automation, API development, data validation, and human-in-the-loop review can be combined to streamline the initial handling of freight operations emails.
