# AI Property Sales & Lead Automation Platform

A full-stack property sales application that helps manage property enquiries, assist customers with property searches, qualify leads, and escalate enquiries that require human attention.

## Features

* Property listing and search
* Natural-language property search
* Retrieval-Augmented Generation (RAG)
* AI-assisted property enquiries
* Conversation history
* Lead capture and qualification
* Lead scoring
* Human escalation
* Response validation
* REST API
* Responsive web interface

## Tech Stack

**Backend**

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* SQLite
* Chroma

**AI**

* RAG
* Embeddings
* LLM integration
* Conversation memory
* Lead scoring
* Response validation

**Frontend**

* Next.js
* TypeScript
* React
* Tailwind CSS
* Lucide
* Framer Motion

**Testing**

* Pytest
* ESLint
* TypeScript

## Architecture

```text
User
 |
 v
Next.js Frontend
 |
 v
FastAPI API
 |
 +-------------------+
 |                   |
 v                   v
Property Search    Sales Agent
                       |
                       v
                  RAG Retrieval
                       |
                       v
                 Response Validation
                       |
              +--------+--------+
              |                 |
              v                 v
        Lead Qualification   Escalation
```

## Project Structure

```text
ai-property-sales-automation/
│
├── app/
│   ├── api/
│   ├── models/
│   ├── schemas/
│   └── services/
│
├── frontend/
│   └── Next.js application
│
├── docs/
│   └── project documentation
│
├── scripts/
│   └── database and RAG utilities
│
├── tests/
│   └── automated tests
│
├── pyproject.toml
├── README.md
└── .gitignore
```

## Running the Backend

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -e ".[dev]"
```

Create the environment file:

```powershell
copy .env.example .env
```

Seed the database:

```powershell
python scripts/seed_database.py
```

Start the API:

```powershell
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

## Running the Frontend

Open another terminal:

```powershell
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

Frontend:

```text
http://localhost:3000
```

## API Endpoints

### Properties

```text
GET  /properties
GET  /properties/{property_id}
POST /properties/search
POST /properties/search/natural
```

### Knowledge Base

```text
POST /knowledge/reindex
POST /knowledge/search
```

### Chat

```text
POST /chat
GET  /conversations/{conversation_id}/messages
```

### Leads

```text
POST /leads
GET  /leads
GET  /leads/{id}
```

### Escalations

```text
POST /escalations
GET  /escalations
GET  /escalations/{id}
```

## AI Configuration

The application supports different LLM modes:

```text
LLM_MODE=mock
LLM_MODE=openai
LLM_MODE=anthropic
```

Mock mode can be used for local development and testing without a paid API.

API keys and other secrets are stored through environment variables and are not committed to the repository.

## Testing

Run the backend tests with:

```powershell
pytest
```

The project includes tests for:

* Property search
* Natural-language search
* Chat
* Conversation memory
* Lead qualification
* Lead scoring
* Human escalation
* Response validation
* LLM provider configuration

Frontend checks:

```powershell
cd frontend
npm run lint
npx tsc --noEmit
npm run build
```

## Development Notes

Chroma uses native dependencies on Windows and may require Microsoft C++ Build Tools during installation.

For setup and development details, see:

```text
docs/DEVELOPMENT.md
```

Additional technical documentation is available in the `docs/` directory.

## Project Status

The current version includes the backend, AI services, RAG workflow, lead management, escalation workflow, frontend interface, testing, and project documentation.

## Future Improvements

* CRM integration
* n8n workflow automation
* Email and SMS notifications
* WhatsApp integration
* Real property listing APIs
* Analytics and reporting
* Authentication and role-based access control
* Cloud deployment

## Author

Prabin Rai

BSc (Hons) Computer Science

Interests: AI Engineering, Generative AI, Machine Learning, AI Automation, and AI Infrastructure.
