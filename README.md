
# AI Freight Operations Assistant

An end-to-end prototype that automates freight email processing using n8n, Python, FastAPI, PostgreSQL, and Streamlit. The system monitors incoming emails, classifies them into operational categories, stores structured records, and provides a dashboard for human review.

## Project Links

- **Live Dashboard:** [Open the Streamlit Dashboard](https://ai-freight-email-assistant-vpjyzfp7ddslduuwcoe6tv.streamlit.app/)
- **API Documentation:** https://ai-freight-email-assistant.onrender.com/docs
- **Backend API:** https://ai-freight-email-assistant.onrender.com

## Project Overview

Freight operations teams receive emails about quotations, shipment tracking, documentation, and general enquiries. Manually sorting these emails can be repetitive and time-consuming.

This project automates the initial email-processing workflow and provides a structured interface for employees to review incoming requests. It combines workflow automation, rule-based classification, API integration, persistent data storage, and a dashboard into a single prototype.

## Key Features

- **Email Monitoring:** Uses an n8n Gmail Trigger to detect incoming emails.
- **Email Normalization:** Extracts email IDs, thread IDs, sender, subject, and body.
- **Rule-Based Classification:** Categorizes emails into quotation requests, shipment status enquiries, documentation requests, and other enquiries.
- **API Integration:** Uses FastAPI and Pydantic for request validation and email record processing.
- **Persistent Storage:** Stores email records in PostgreSQL in the deployed environment, with SQLite support for local development.
- **Duplicate Prevention:** Checks email IDs to prevent duplicate records from being inserted.
- **Human-in-the-Loop Review:** Marks incoming emails as pending review rather than treating automated classifications as final decisions.
- **Interactive Dashboard:** Provides a Streamlit interface for viewing email records, searching and filtering data, and reviewing operational categories and statuses.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Workflow Automation | n8n |
| Email Integration | Gmail |
| Backend API | FastAPI |
| Request Validation | Pydantic |
| Database | PostgreSQL, SQLite for local development |
| Dashboard | Streamlit |
| Data Processing | Pandas |
| Deployment | Render, Streamlit Community Cloud |

## Email Categories

| Category | Purpose |
|---|---|
| `quote_request` | Freight quotations, rates, and shipping cost enquiries |
| `shipment_status` | Shipment tracking and delivery status enquiries |
| `documentation_request` | Invoices, bills of lading, and shipping documents |
| `other` | Emails that do not match the configured classification rules |

The current classifier uses phrase-matching rules implemented in JavaScript workflow nodes. It is not an ML- or LLM-based classifier, and unfamiliar or multi-topic emails may be categorized incorrectly.

## Workflow Architecture

1. An email arrives in the connected Gmail account.
2. The n8n Gmail Trigger detects the incoming message.
3. JavaScript workflow nodes normalize the email fields and apply classification rules.
4. n8n sends the structured email record to the FastAPI backend through an HTTP POST request.
5. FastAPI validates the request, checks for duplicate email IDs, and stores the record in the database.
6. The Streamlit dashboard retrieves records from the backend API.
7. An employee reviews the email and inspects its category and review status through the dashboard.

## Architecture Diagram

```text
Incoming Gmail
      |
      v
n8n Gmail Trigger
      |
      v
Email Normalization
      |
      v
Rule-Based Classification
      |
      v
HTTP Request
      |
      v
FastAPI Backend
      |
      v
PostgreSQL Database
      |
      v
Streamlit Dashboard
      |
      v
Human Review
```

## Project Structure

```text
Prologis_Frieght/
├── README.md
├── requirements.txt
├── python/
│   ├── validate_email.py
│   ├── classify_email.py
│   ├── classify_single_email.py
│   ├── append_email.py
│   ├── append_api.py
│   └── update_review_workbook.py
├── n8n/
└── output/
```

Generated files, local database files, credentials, and environment-specific configuration may be excluded from version control.

## Setup and Local Execution

### 1. Clone the Repository

```powershell
git clone https://github.com/ashmisharma93/AI-Freight-Email-Assistant.git
cd AI-Freight-Email-Assistant
```

### 2. Activate the Python Environment

If using Conda:

```powershell
conda activate p_env
```

Alternatively, create and activate a virtual environment appropriate for your Python installation.

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Configure the required database connection and other environment-specific settings for your local setup. Do not commit credentials, API keys, or `.env` files to GitHub.

### 5. Start the FastAPI Service

From the project root, run:

```powershell
python -m uvicorn python.append_api:app --host 127.0.0.1 --port 8000
```

Open the local API documentation at:

http://127.0.0.1:8000/docs

Keep the terminal running while using the local API.

### 6. Configure n8n

- Connect the Gmail account using the appropriate OAuth credentials.
- Configure the Gmail Trigger to detect incoming messages.
- Set up the JavaScript nodes for email normalization and classification.
- Configure the HTTP Request node to send JSON records to the FastAPI endpoint.
- Publish the workflow after testing it.

For local execution, the HTTP Request node should use:

```text
http://127.0.0.1:8000/append-email
```

For the deployed workflow configuration, use:

```text
https://ai-freight-email-assistant.onrender.com/append-email
```

**Note:** The current n8n workflow runs locally. Automatic email processing requires the n8n instance to be running and the published workflow to be configured correctly.

### 7. Open the Dashboard

Access the deployed Streamlit dashboard through the link in the Project Links section. The dashboard retrieves email records from the deployed FastAPI backend.

## Review Statuses

- `Pending Review`
- `Reviewed`
- `Needs Follow-up`

Automated classification is intended to assist employees, not replace human review or operational decision-making.

## Current Limitations

- Classification is rule-based and depends on configured phrases.
- Classification accuracy has not been established through a formal evaluation.
- Multi-topic, ambiguous, or unfamiliar emails may be categorized incorrectly.
- Automatic email processing depends on the n8n workflow running and being properly configured.
- The deployed backend and dashboard depend on network connectivity and service availability.
- The prototype has not been validated for production-scale freight operations.
- Authentication, access controls, and security hardening require further work before processing real customer or commercially sensitive email data.

## Future Improvements

- Introduce an ML- or LLM-assisted classifier with confidence scores.
- Improve multi-topic classification and add a fallback mechanism for uncertain predictions.
- Evaluate classification quality using a labeled dataset and appropriate metrics.
- Add structured logging, monitoring, retries, and stronger error handling.
- Implement API authentication and role-based access controls.
- Improve review-status management and auditability.
- Add automated testing and production deployment safeguards.

## Project Goal

Demonstrate how workflow automation, API development, data validation, persistent storage, and human-in-the-loop review can be combined to streamline the initial handling of freight operations emails.
