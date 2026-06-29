from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    email: str
    username: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentCreate(BaseModel):
    title: str = "Untitled Document"


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class DocumentOut(BaseModel):
    id: str
    title: str
    content: str
    owner_id: str
    owner_email: Optional[str] = None
    owner_username: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FileUploadRequest(BaseModel):
    title: Optional[str] = None


class ShareRequest(BaseModel):
    email: EmailStr
    permission: str = "edit"


class ShareOut(BaseModel):
    id: str
    document_id: str
    shared_with_id: str
    shared_with_email: str
    shared_with_username: str
    permission: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
