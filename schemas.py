from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr

# User Schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True

# Comment Schemas
class CommentCreate(BaseModel):
    text: str

class CommentResponse(BaseModel):
    id: int
    text: str
    created_at: datetime
    user_id: int
    post_id: int
    author: UserResponse

    class Config:
        from_attributes = True

# Post Schemas
class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    user_id: int
    author: UserResponse
    comments: List[CommentResponse] = []

    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None