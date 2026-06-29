# DocEditor

A lightweight collaborative document editor inspired by Google Docs.

**Live Demo:** _[Add URL after deployment]_  
**Test accounts:** Register via the UI. For sharing flows, create `alice@test.com` and `bob@test.com` (password: `pass1234`).

---

## Features

- Rich text editing — Bold, Italic, Underline, H1/H2/H3, Bullet List, Ordered List
- File upload — `.txt`, `.md`, and `.docx` files convert to editable documents
- Document sharing — share by email, with view-only or edit permission enforced
- Real-time presence — see who else has the document open; edits sync live via WebSocket
- Version history — every save creates a snapshot; browse and restore from the editor
- Full auth — register, login, JWT sessions

---

## Quick Start (Docker)

```bash
git clone <repo-url> && cd doceditor
cp .env.example .env
# Edit .env and set a strong SECRET_KEY
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8000/docs

The backend runs Alembic migrations on startup automatically.

---

## Local Development (without Docker)

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export DATABASE_URL=postgresql+asyncpg://docuser:docpass@localhost:5432/doceditor
export SYNC_DATABASE_URL=postgresql+psycopg2://docuser:docpass@localhost:5432/doceditor
export SECRET_KEY=dev-secret-key

alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev    # starts at http://localhost:5173
```

Vite proxies `/api` and `/ws` to `http://localhost:8000` automatically.

---

## Running Tests

```bash
cd backend
pytest
```

Tests use in-memory SQLite — no Postgres needed.

---

## File Upload

Supported formats: **`.txt`**, **`.md`**, **`.docx`**. The file is parsed and converted to a rich-text document. `.pdf` is not supported.

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | JWT signing secret — **change this in production** | `dev-secret-key` |
| `DATABASE_URL` | Async PostgreSQL URL | see docker-compose |
| `SYNC_DATABASE_URL` | Sync PostgreSQL URL (Alembic only) | see docker-compose |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `10080` (7 days) |
