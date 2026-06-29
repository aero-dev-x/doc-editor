# AI Workflow Note

## Tools Used

- **Claude Code (claude-sonnet-4-6)** — primary coding assistant throughout this project

## Where AI Materially Sped Up My Work

**Boilerplate acceleration:**
- FastAPI router scaffolding with async SQLAlchemy patterns
- Alembic `env.py` configuration, particularly the sync/async URL split
- TipTap editor setup with extension wiring and the `useEditor` hook
- Docker Compose service definitions with health checks and startup ordering
- WebSocket connection manager pattern (broadcast-to-room structure)

**Problem prevention:**
AI flagged the FastAPI route ordering issue upfront — `/documents/shared` must be registered before `/{doc_id}` or FastAPI interprets the string "shared" as a UUID parameter. This saved real debugging time.

**Parser generation:**
The `.md` and `.docx` to TipTap JSON converters were co-generated and then manually verified against TipTap's expected node structure by round-tripping content through the editor.

## What I Changed or Rejected

**Rejected:** AI initially suggested storing TipTap content as PostgreSQL JSONB. Switched to TEXT — the content is always read/written as a blob, JSONB operators add no value, and TEXT is more portable.

**Rejected:** AI proposed the `@tiptap/extension-collaboration` package for real-time. It had peer dependency conflicts with the installed TipTap version. Switched to native FastAPI WebSockets with a broadcast manager — simpler, no Yjs dependency, covers the core presence and live-sync use case.

**Changed:** Auto-save hook initially called `updateDocument` on every editor `onUpdate` event. Refactored to a proper `useRef`-based debounce after recognizing it would fire 10+ requests per keystroke.

**Changed:** `ProtectedRoute` initially used `useEffect` to check auth, causing a layout flash. Fixed by reading `isLoading` from `AuthContext` directly and rendering a neutral loading state.

## How I Verified Correctness

- Ran `pytest` suite (2 tests, all passing) covering the full lifecycle: register → create → share → access control → file upload
- TypeScript compiler (`tsc --noEmit`) run with zero errors after all changes
- Manually round-tripped TipTap content through save → reload → re-render to confirm formatting persistence
- Tested view-only enforcement by logging in as a shared user and confirming the toolbar is disabled
- Tested WebSocket presence by opening the same document in two browser tabs simultaneously
- Confirmed Docker Compose builds cleanly from scratch with `docker compose up --build`

## Reflection

AI accelerated the mechanical work — boilerplate, config, Dockerfile patterns, parser logic — enough that I could spend proportionally more time on product decisions: what to cut, how to structure the sharing UX, how to handle permission enforcement, and whether to use CRDT or a simpler broadcast model. Those judgment calls were mine; AI executed against them.
