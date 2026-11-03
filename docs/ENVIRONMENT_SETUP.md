# Environment Setup & Compatibility Report — NEUROTEACH AI

## 1. Environment Inspection Summary

| Component | Detected Specification | Status | Compatibility Notes |
|---|---|---|---|
| **Operating System** | Windows 11 Enterprise (NT 10.0.26300.0) | ✅ Ready | Full Windows PowerShell environment. |
| **Node.js** | `v24.7.0` | ✅ Ready | Node 20+ compatible with Vite 5/6, React 18, and modern ESM tooling. |
| **npm** | `11.5.1` | ✅ Ready | Modern package manager. |
| **Python** | `Python 3.10.0` | ✅ Ready | Fully compatible with FastAPI, Pydantic v2, SQLAlchemy 2, asyncpg, SymPy, NumPy, and Pytest. |
| **Git** | `git version 2.51.0.windows.1` | ✅ Ready | Version control available. |
| **PostgreSQL** | PostgreSQL Server 18 (`psql.exe` at `C:\Program Files\PostgreSQL\18\bin\psql.exe`) | ✅ Running | Service `postgresql-x64-18` is running and accessible locally on default port `5432`. |
| **Workspace** | `D:\oracathon` | ✅ Scaffolding Prepared | Directory tree structured for docs, backend, frontend, ml, and artifacts. |

---

## 2. Python 3.10 Compatibility Analysis
Python **3.10.0** is an official Python LTS release with full support across all selected packages:
- **FastAPI (0.111.0+) & Pydantic v2 (2.7.4+)**: Both provide pre-built C-extension wheels (`pydantic-core`) for Windows x86_64 on Python 3.10.
- **SQLAlchemy 2.0.31+ & asyncpg 0.29.0**: Fully compatible with Python 3.10 asyncio event loops.
- **SymPy 1.12.1+ & NumPy 1.26.4**: Stable binaries available without requiring local compilation.
- **Passlib & Argon2-cffi**: Native Windows binaries available.

---

## 3. Recommended Frontend & Backend Dependency Versions

### Frontend Stack (`frontend/package.json`)
- **Core Framework**: React `^18.3.1` & React DOM `^18.3.1`
- **Build Tool**: Vite `^5.4.0` with `@vitejs/plugin-react` `^4.3.1`
- **Language**: TypeScript `^5.5.4`
- **Styling**: Tailwind CSS `^3.4.10`, PostCSS `^8.4.41`, Autoprefixer `^10.4.20`, Tailwind Typography `^0.5.15`
- **Routing & State**: React Router DOM `^6.26.1`, `@tanstack/react-query` `^5.52.1`, Zustand `^4.5.5`
- **Icons & Micro-animations**: Lucide React `^0.435.0`, Framer Motion `^11.3.28`
- **Charts (Data & Metrics)**: Recharts `^2.12.7`
- **Interactive Mathematics Graphing Library**: JSXGraph `^1.10.1` (or Mafs `^0.13.1` as a React-first SVG alternative)
- **Diagram & Concept Map Visualization**: `@xyflow/react` (React Flow v12) `^12.0.4`
- **Math Formatting (LaTeX)**: KaTeX `^0.16.11` & `react-katex` `^3.0.1`

### Backend Stack (`backend/requirements.txt`)
```text
# Web Framework & Server
fastapi==0.111.0
uvicorn[standard]==0.30.1
pydantic==2.7.4
pydantic-settings==2.3.4

# Database & ORM
sqlalchemy==2.0.31
asyncpg==0.29.0
alembic==1.13.2

# Security & Authentication
passlib[argon2]==1.7.4
argon2-cffi==23.1.0
python-jose[cryptography]==3.3.0
python-multipart==0.0.9

# Mathematical & Scientific Engine
sympy==1.12.1
numpy==1.26.4
scipy==1.13.1

# HTTP & AI Integration Client
httpx==0.27.0

# Testing & Quality
pytest==8.2.2
pytest-asyncio==0.23.7
pytest-cov==5.0.0
```

---

## 4. Proposed Setup Commands (Pending User Approval)

### Step 1: Backend Virtual Environment Setup
*Note: Run from the workspace root or `backend` folder.*
```powershell
# 1. Create a dedicated Python 3.10 virtual environment
python -m venv backend/venv

# 2. Activate virtual environment
.\backend\venv\Scripts\Activate.ps1

# 3. Upgrade pip, setuptools and wheel
python -m pip install --upgrade pip setuptools wheel

# 4. Install backend dependencies
pip install -r backend/requirements.txt
```

### Step 2: Database Initialization (PostgreSQL)
*Create the database using PostgreSQL CLI:*
```powershell
# Create database 'neuroteach_db' with default postgres user
# (You will be prompted for your local PostgreSQL password)
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -c "CREATE DATABASE neuroteach_db;"
```

### Step 3: Frontend Project Initialization
*Initialize frontend using non-interactive Vite template:*
```powershell
cd frontend
# Install package dependencies
npm install
cd ..
```

---

## 5. Security & Configuration Best Practices
- Keep `.env` out of version control (already configured in `.gitignore`).
- Store database credentials and API endpoints in `.env` exclusively.
- All model inference calls will use the mock-safe `llm_client` wrapper allowing complete offline development and testing prior to external model endpoint connectivity.
