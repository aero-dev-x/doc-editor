# Architecture Note

## What I Built and Why

### Stack

| Layer | Choice | Reason |
|---|---|---|
| Backend | FastAPI (Python) | Async-native, excellent type safety via Pydantic, auto-generated OpenAPI docs |
| ORM | SQLAlchemy 2.0 async | Non-blocking I/O matches uvicorn's event loop; clean declarative models |
| Migrations | Alembic | First-class SQLAlchemy integration, deterministic upgrade path |
| Auth | bcrypt + python-jose (JWT) | Industry-standard password hashing; stateless JWT avoids session storage complexity |
| Database | PostgreSQL 16 | ACID compliance, strong tooling ecosystem |
| Frontend | React 18 + Vite + TypeScript | Fast DX, strong typing catches errors at build time |
| Rich Text | TipTap v2 | ProseMirror-based, headless, clean extension model; best React integration |
| Real-time | FastAPI WebSockets + native browser WS | Avoids Yjs/CRDT complexity while still delivering presence and live content sync |
| Containerization | Docker Compose | Self-contained local setup; easy to port to any container-aware host |

### Key Design Decisions

**TipTap content stored as JSON in a TEXT column.**
TipTap's `editor.getJSON()` produces a clean document tree. Storing it as a TEXT column (JSON string) avoids JSONB-specific migration concerns and is sufficient since content is always read/written as a whole blob, never queried by field.

**Two SQLAlchemy URLs (sync + async).**
FastAPI uses `asyncpg` for non-blocking request handling. Alembic needs a synchronous engine. Rather than hacking Alembic's env.py with `run_sync` wrappers, I maintain two connection URLs — cleaner and more explicit.

**`/documents/shared` registered before `/{doc_id}`.**
FastAPI resolves routes top-to-bottom. Registering the static `/shared` path first prevents FastAPI from trying to validate the string `"shared"` as a UUID parameter.

**WebSocket without CRDT.**
Each document gets a WebSocket room in `ConnectionManager`. Edits are broadcast to all connected clients for that document. This gives real presence and live sync for turn-based collaboration. True concurrent editing without conflicts requires a CRDT library (Yjs + Hocuspocus) which is a multi-day integration — documented as the natural next step.

**Version snapshots on every content save.**
Each `PATCH /documents/{id}` call with new content saves the previous state as a `DocumentVersion` row before overwriting. This is append-only, cheap to query, and supports restore without a separate background job. The most recent 50 versions are surfaced in the history panel.

**JWT in localStorage.**
Simpler than httpOnly cookies for this scope (no same-site CORS configuration required). Acceptable for a demo; noted here as the trade-off for a production hardening pass.

### What I Prioritized

1. **End-to-end flow.** Every stated feature works completely — auth, edit, upload, share, persist, real-time, history. Nothing is mocked.
2. **Editor quality.** TipTap's toolbar is responsive and accurate. Auto-save with debounce means no manual "Save" prompts.
3. **Permission model.** View-only is enforced in the editor (TipTap `editable: false`). Owners see the Share button; viewers see a "View only" badge.

### Scope Cuts

| Feature | Reason |
|---|---|
| CRDT conflict resolution | Yjs + Hocuspocus is a multi-day integration; last-write-wins covers most real use |
| Rendered version diff | Rendering TipTap JSON outside an editor instance requires additional setup |
| Email verification | Out of scope for timebox; accounts work immediately |

### What I Would Build Next

- **True CRDT** via Yjs + Hocuspocus for conflict-free concurrent edits
- **Rendered diff view** in version history — show what changed between snapshots
- **Export to Markdown / PDF** — serialize TipTap JSON back to Markdown or print via headless Chrome
- **Role escalation** — let owner change a share from view to edit after the fact
