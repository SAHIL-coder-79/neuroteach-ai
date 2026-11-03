# NEUROTEACH AI — Setup & Execution Guide

NEUROTEACH AI is an adaptive pedagogical learning platform pairing fine-tuned misconception diagnosis models with deterministic visual and mathematical verification.

---

## 🏗️ Project Architecture

- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, TanStack Query, Recharts, JSXGraph, React Flow.
- **Backend**: Python 3.10+, FastAPI (modular monolith), Pydantic v2, SQLAlchemy 2.0 (async), Alembic, SymPy.
- **Database**: PostgreSQL (production/staging) / SQLite with aiosqlite (zero-setup local fallback).
- **AI Integration**: Adaption AutoScientist-trained pedagogical model accessed through a secure, server-side `llm_client`.

---

## 🔒 Security Best Practices

1. **No Frontend Leaks**: AutoScientist API keys and backend secrets are loaded strictly on the backend and never exposed to React or the client bundle.
2. **Secret Management**: Passwords are never stored in plain text (Argon2 hashing).
3. **Environment Isolation**: `.env` is ignored by git; use `.env.example` as a template.
4. **Input Sanitization**: Math expressions are validated via SymPy AST symbol whitelists without dynamic `eval()`.

---

## 🚀 Getting Started

### 1. Environment Configuration

Copy the sample environment file:
```bash
cp .env.example .env
```
*(Default settings automatically enable SQLite local mode if PostgreSQL credentials are not yet configured).*

### 2. Backend Setup & Run

From the root directory:
```bash
# Navigate to backend
cd backend

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run automated tests
pytest tests -v

# Start development server
uvicorn app.main:app --reload --port 8000
```
- API Documentation (Swagger UI): `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/v1/health`

### 3. Frontend Setup & Run

In a separate terminal:
```bash
# Navigate to frontend
cd frontend

# Install dependencies (if not already installed)
npm install

# Run TypeScript build check
npm run build

# Start Vite dev server
npm run dev
```
- Frontend Web App: `http://localhost:5173`

---

## 🧪 Automated Testing

To run the backend test suite:
```bash
cd backend
.\venv\Scripts\python -m pytest tests -v
```

To run the frontend build and type-checking:
```bash
cd frontend
npm run build
```
