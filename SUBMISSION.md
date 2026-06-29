# Submission

**Candidate:** Hamza Fayyaz (hamza.fayyaz.devx@gmail.com)  
**Assignment:** AI-Native Full Stack Developer — Ajaia LLC

---

## What Is Included

| Item | Status | Location |
|---|---|---|
| Source code | ✅ Complete | `backend/` + `frontend/` |
| README with setup instructions | ✅ Complete | `README.md` |
| Architecture note | ✅ Complete | `ARCHITECTURE.md` |
| AI workflow note | ✅ Complete | `AI_WORKFLOW.md` |
| Automated tests | ✅ Complete | `backend/app/tests/test_documents.py` |
| Docker Compose setup | ✅ Complete | `docker-compose.yml` |
| Live deployment | ⏳ Deploy in progress | See below |
| Walkthrough video | ⏳ Record after deployment | See below |

---

## Live URL

_[Add deployment URL here]_

## Video Walkthrough

_[Add Loom/YouTube URL here]_

---

## Test Accounts

Register two accounts via the UI to test sharing:

| Email | Password |
|---|---|
| alice@test.com | pass1234 |
| bob@test.com | pass1234 |

---

## What Is Working

- User registration and login (JWT auth, bcrypt passwords)
- Document creation, renaming, editing with full rich text (Bold, Italic, Underline, H1/H2/H3, Bullet List, Ordered List)
- Auto-save on 1.5s debounce — content and formatting persist across refresh
- File upload (.txt, .md, .docx) — converts to editable rich-text document
- Document sharing by email with view or edit permission
- View-only enforcement — shared users with "view" permission get a read-only editor
- Dashboard: "My Documents" and "Shared with me" sections clearly separated
- Real-time presence — avatars appear when another user opens the same document
- Live content sync — edits broadcast to other connected sessions via WebSocket
- Version history — every save creates a snapshot; reviewable and restorable from the editor
- Full Docker Compose setup — `docker compose up --build` starts everything

## Intentional Scope Cuts

- No CRDT-based conflict resolution — simultaneous edits from two users may overwrite each other (last write wins). Full CRDT requires Yjs + a dedicated sync server, which is a multi-day effort.
- Version history preview shows raw JSON, not rendered output — rendering TipTap outside an editor instance requires additional setup.

## What I Would Add Next

- CRDT merge via Yjs + Hocuspocus for true concurrent editing without conflicts
- Rendered diff view in version history (highlight what changed between versions)
- Export to PDF or Markdown from the editor
- Role escalation UI — owner can change a share from view to edit after the fact
