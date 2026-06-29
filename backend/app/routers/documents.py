import json
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.deps import get_current_user
from app.models.models import Document, DocumentShare, DocumentVersion, User
from app.schemas.schemas import DocumentCreate, DocumentOut, DocumentUpdate
from app.services.file_service import file_to_tiptap

router = APIRouter()

ALLOWED_EXTENSIONS = {".txt", ".md", ".docx"}


def _doc_to_out(doc: Document) -> DocumentOut:
    return DocumentOut(
        id=doc.id,
        title=doc.title,
        content=doc.content,
        owner_id=doc.owner_id,
        owner_email=doc.owner.email if doc.owner else None,
        owner_username=doc.owner.username if doc.owner else None,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


async def _get_doc_or_403(doc_id: str, user: User, db: AsyncSession) -> Document:
    result = await db.execute(
        select(Document)
        .options(selectinload(Document.owner), selectinload(Document.shares))
        .where(Document.id == doc_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    is_owner = doc.owner_id == user.id
    is_shared = any(s.shared_with_id == user.id for s in doc.shares)
    if not is_owner and not is_shared:
        raise HTTPException(status_code=403, detail="Access denied")
    return doc


@router.get("", response_model=list[DocumentOut])
async def list_my_documents(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Document)
        .options(selectinload(Document.owner))
        .where(Document.owner_id == current_user.id)
        .order_by(Document.updated_at.desc())
    )
    return [_doc_to_out(d) for d in result.scalars().all()]


# must come before /{doc_id} or FastAPI treats the string "shared" as a UUID param
@router.get("/shared", response_model=list[DocumentOut])
async def list_shared_documents(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Document)
        .options(selectinload(Document.owner), selectinload(Document.shares))
        .join(DocumentShare, DocumentShare.document_id == Document.id)
        .where(DocumentShare.shared_with_id == current_user.id)
        .order_by(Document.updated_at.desc())
    )
    return [_doc_to_out(d) for d in result.scalars().all()]


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def create_document(body: DocumentCreate = DocumentCreate(), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)
    doc = Document(
        owner_id=current_user.id,
        title=body.title,
        content=json.dumps({"type": "doc", "content": [{"type": "paragraph"}]}),
        created_at=now,
        updated_at=now,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc, ["owner"])
    return _doc_to_out(doc)


@router.get("/{doc_id}", response_model=DocumentOut)
async def get_document(doc_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    doc = await _get_doc_or_403(doc_id, current_user, db)
    return _doc_to_out(doc)


@router.patch("/{doc_id}", response_model=DocumentOut)
async def update_document(doc_id: str, body: DocumentUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    doc = await _get_doc_or_403(doc_id, current_user, db)
    if body.title is not None:
        doc.title = body.title
    if body.content is not None:
        # snapshot before overwriting so history is queryable
        snapshot = DocumentVersion(
            document_id=doc.id,
            saved_by_id=current_user.id,
            title=doc.title,
            content=doc.content,
            created_at=datetime.now(timezone.utc),
        )
        db.add(snapshot)
        doc.content = body.content
    doc.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(doc)
    return _doc_to_out(doc)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(doc_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the owner can delete this document")
    await db.delete(doc)
    await db.commit()


@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Only {', '.join(ALLOWED_EXTENSIONS)} files are supported")

    raw = await file.read()
    tiptap_content = file_to_tiptap(file.filename, raw)
    title = os.path.splitext(file.filename)[0] if file.filename else "Uploaded Document"

    now = datetime.now(timezone.utc)
    doc = Document(owner_id=current_user.id, title=title, content=tiptap_content, created_at=now, updated_at=now)
    db.add(doc)
    await db.commit()
    await db.refresh(doc, ["owner"])
    return _doc_to_out(doc)
