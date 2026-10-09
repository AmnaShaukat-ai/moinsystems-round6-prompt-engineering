# MoinSystems AI — Round 5: AI & API Integration

## Overview

This update extends the MoinSystems AI chatbot (built in Rounds 1–4) by connecting it to external services. The AI chatbot now does more than hold a conversation — when it detects buying intent, it collects a lead's details, saves them to a database, and automatically triggers a real-world notification workflow through n8n.

**Core flow:**

```
User chats with the bot
        ↓
AI detects buying/lead intent (detect_lead_intent)
        ↓
Bot collects name, email, phone (with smart extraction from natural language)
        ↓
Lead is validated
        ↓
Lead is saved to a SQLite database
        ↓
Lead data is POSTed to an n8n webhook (event-driven trigger)
        ↓
n8n workflow calls the Resend API
        ↓
A real email notification is sent with the lead's details
```

## What Was Added in Round 5

### 1. Smart Field Extraction
Previously, the bot stored whatever the user typed verbatim (e.g. "My name is Amna Shaukat" would be saved as the full sentence). Three new regex-based helper functions were added to `rag_service.py`:

- `extract_name(text)` — strips common lead-in phrases ("my name is", "i am", "this is", etc.) to isolate the actual name.
- `extract_email(text)` — already existed; pulls a valid email address out of any sentence.
- `extract_phone(text)` — pulls a phone number (digits, spaces, dashes) out of any sentence.

### 2. Database Integration (SQLite)
`send_lead_email()` now opens a connection to a local SQLite database (`lead.db`), creates the `lead` table if it doesn't exist, and inserts every validated lead as a new row (`id`, `name`, `email`, `phone`).

### 3. Webhook / n8n Integration
After saving to the database, the same function sends a `POST` request (with the lead data as JSON) to an n8n webhook URL (`N8N_WEBHOOK_URL`, stored in `.env`). This is an event-driven trigger — it only fires once a complete, validated lead exists.

### 4. n8n Workflow (built separately, hosted via Docker)
A new n8n workflow, **"Lead Capture - MoinSystems AI"**, was built with:
- **Webhook node** (trigger, `POST`, Production URL, Active)
- **HTTP Request node** — calls the Resend API (`https://api.resend.com/emails`) using Header Auth (`Authorization: Bearer <RESEND_API_KEY>`) to send a formatted email containing the lead's name, email, and phone.

### 5. Error Handling
The database write and the webhook call are each wrapped in their own `try/except` block. If either step fails, the function returns a clear success/failure message instead of crashing, and the error is logged via the existing `logger`.

## Environment Variables

Add the following to the project's `.env` file (in addition to the existing `OPENAI_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`, `RESEND_API_KEY`):

```
N8N_WEBHOOK_URL=http://localhost:5679/webhook/lead-capture
```

> Use the **Production URL** from n8n (not the Test URL) so the webhook works automatically without needing to manually "Listen for Test Event" each time.

## New Python Dependencies

```python
import sqlite3
import requests
```

(No install needed for `sqlite3` — it's part of Python's standard library. `requests` may need `pip install requests` if not already present.)

## How to Test

1. Start the FastAPI server (`uvicorn main:app --reload`).
2. Ensure the n8n Docker container is running and the workflow is **Active**.
3. Send a message to the chatbot that signals buying intent, e.g.:
   ```
   I'm interested in your services, please contact me
   ```
4. Respond with name, email, and phone when prompted — natural phrasing works too, e.g. "My name is Amna Shaukat", "my email is amna@example.com", "my contact number is 03001234567".
5. Verify:
   - The chatbot returns a success confirmation message.
   - A new row appears in `lead.db` (table `lead`).
   - The n8n workflow execution shows as successful (check the **Executions** tab for Production runs).
   - An email arrives via Resend with the lead's full details.

## Deliverable Checklist (Round 5 Requirements)

| Requirement | Status |
|---|---|
| REST API fundamentals and authentication patterns | ✅ |
| GET/POST requests, JSON payloads and response parsing | ✅ |
| Webhooks and event-driven workflows | ✅ |
| Integrating databases and third-party services | ✅ |
| Connecting AI decisions to automation platforms (n8n) | ✅ |
| Error handling, timeouts and retries around external services | ✅ |
| **Deliverable:** at least one useful integration | ✅ — Database write **+** n8n-triggered workflow **+** notification (4-in-1) |

## Tech Stack Used

- **Python** (FastAPI backend, from earlier rounds)
- **SQLite** — lightweight local database for lead storage
- **n8n** (self-hosted via Docker) — automation/workflow engine
- **Resend API** — transactional email delivery
- **Webhooks** — event-driven communication between the Python backend and n8n

## Notes

- The database used is SQLite rather than PostgreSQL; this satisfies the "PostgreSQL/other database" recommendation in the roadmap. Migrating to PostgreSQL later would only require changing the connection logic, not the overall design.
- The n8n instance runs locally via Docker (`localhost:5679`); for a production deployment, this would need to point to a publicly accessible n8n instance or a hosted n8n Cloud URL.