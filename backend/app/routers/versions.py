from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.deps import get_current_user
from app.models.models import Document, DocumentShare, DocumentVersion, User

router = APIRouter()


class VersionOut(BaseModel):
    id: str
    document_id: str
    title: str
    content: str
    saved_by_id: str | None
    saved_by_username: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


async def _check_access(doc_id: str, user: User, db: AsyncSession) -> Document:
    result = await db.execute(
        select(Document)
        .options(selectinload(Document.shares))
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


@router.get("/{doc_id}/versions", response_model=list[VersionOut])
async def list_versions(doc_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await _check_access(doc_id, current_user, db)
    result = await db.execute(
        select(DocumentVersion)
        .options(selectinload(DocumentVersion.saved_by))
        .where(DocumentVersion.document_id == doc_id)
        .order_by(DocumentVersion.created_at.desc())
        .limit(50)
    )
    versions = result.scalars().all()
    return [
        VersionOut(
            id=v.id,
            document_id=v.document_id,
            title=v.title,
            content=v.content,
            saved_by_id=v.saved_by_id,
            saved_by_username=v.saved_by.username if v.saved_by else None,
            created_at=v.created_at,
        )
        for v in versions
    ]


@router.get("/{doc_id}/versions/{version_id}", response_model=VersionOut)
async def get_version(doc_id: str, version_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await _check_access(doc_id, current_user, db)
    result = await db.execute(
        select(DocumentVersion)
        .options(selectinload(DocumentVersion.saved_by))
        .where(DocumentVersion.id == version_id, DocumentVersion.document_id == doc_id)
    )
    v = result.scalar_one_or_none()
    if not v:
        raise HTTPException(status_code=404, detail="Version not found")
    return VersionOut(
        id=v.id,
        document_id=v.document_id,
        title=v.title,
        content=v.content,
        saved_by_id=v.saved_by_id,
        saved_by_username=v.saved_by.username if v.saved_by else None,
        created_at=v.created_at,
    )
