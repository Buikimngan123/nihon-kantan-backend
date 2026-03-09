from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    full_name : str      = Field(..., min_length=2, max_length=100)
    email     : EmailStr
    username  : str      = Field(..., min_length=3, max_length=50)
    password  : str      = Field(..., min_length=8)

class UserLogin(BaseModel):
    email    : EmailStr
    password : str

class UserResponse(BaseModel):
    id: int; email: str; username: str; full_name: str
    level: str; streak: int; xp: int
    avatar_url: Optional[str]; is_admin: bool; created_at: datetime
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token : str
    token_type   : str = "bearer"
    user         : UserResponse

class LessonCreate(BaseModel):
    title: str; description: Optional[str] = None; category: str; level: str
    kanji_icon: Optional[str] = None; content: Optional[str] = None; is_published: bool = False

class VocabCreate(BaseModel):
    lesson_id: int; word: str; hiragana: str; romaji: Optional[str] = None
    meaning_en: str; meaning_vi: Optional[str] = None
    example_jp: Optional[str] = None; example_en: Optional[str] = None
    level: Optional[str] = None; pos: Optional[str] = None

class FlashcardDeckCreate(BaseModel):
    title: str; description: Optional[str] = None; level: Optional[str] = None

class FlashcardCreate(BaseModel):
    deck_id: int; front: str; back: str
    image_url: Optional[str] = None; order_num: int = 0