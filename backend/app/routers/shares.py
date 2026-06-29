from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.deps import get_current_user
from app.models.models import Document, DocumentShare, User
from app.schemas.schemas import ShareOut, ShareRequest

router = APIRouter()


def _share_to_out(share: DocumentShare) -> ShareOut:
    return ShareOut(
        id=share.id,
        document_id=share.document_id,
        shared_with_id=share.shared_with_id,
        shared_with_email=share.shared_with.email,
        shared_with_username=share.shared_with.username,
        permission=share.permission,
        created_at=share.created_at,
    )


async def _require_owner(doc_id: str, user: User, db: AsyncSession) -> Document:
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only the owner can manage shares")
    return doc


@router.get("/{doc_id}/shares", response_model=list[ShareOut])
async def list_shares(doc_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await _require_owner(doc_id, current_user, db)
    result = await db.execute(
        select(DocumentShare)
        .options(selectinload(DocumentShare.shared_with))
        .where(DocumentShare.document_id == doc_id)
    )
    return [_share_to_out(s) for s in result.scalars().all()]


@router.post("/{doc_id}/shares", response_model=ShareOut, status_code=status.HTTP_201_CREATED)
async def share_document(doc_id: str, body: ShareRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await _require_owner(doc_id, current_user, db)

    target = await db.execute(select(User).where(User.email == body.email))
    target_user = target.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=404, detail="User with that email not found")
    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot share a document with yourself")

    existing = await db.execute(
        select(DocumentShare).where(DocumentShare.document_id == doc_id, DocumentShare.shared_with_id == target_user.id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Document already shared with this user")

    share = DocumentShare(document_id=doc_id, shared_with_id=target_user.id, permission=body.permission)
    db.add(share)
    await db.commit()
    await db.refresh(share, ["shared_with"])
    return _share_to_out(share)


@router.get("/{doc_id}/my-permission")
async def my_permission(doc_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Returns the current user's permission on a document they don't own."""
    result = await db.execute(
        select(DocumentShare).where(DocumentShare.document_id == doc_id, DocumentShare.shared_with_id == current_user.id)
    )
    share = result.scalar_one_or_none()
    if not share:
        return {"permission": None}
    return {"permission": share.permission}


@router.delete("/{doc_id}/shares/{share_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_share(doc_id: str, share_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await _require_owner(doc_id, current_user, db)
    result = await db.execute(select(DocumentShare).where(DocumentShare.id == share_id, DocumentShare.document_id == doc_id))
    share = result.scalar_one_or_none()
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
    await db.delete(share)
    await db.commit()
