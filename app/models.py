from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id         = Column(Integer, primary_key=True, index=True)
    email      = Column(String(255), unique=True, nullable=False, index=True)
    username   = Column(String(100), unique=True, nullable=False, index=True)
    full_name  = Column(String(255), nullable=False)
    hashed_pw  = Column(String(255), nullable=False)
    level      = Column(Enum("N5","N4","N3","N2","N1"), default="N5")
    avatar_url = Column(String(500), nullable=True)
    streak     = Column(Integer, default=0)
    xp         = Column(Integer, default=0)
    status     = Column(Enum("active","banned","pending"), default="active")
    is_admin   = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    progress   = relationship("UserProgress", back_populates="user")

class Lesson(Base):
    __tablename__ = "lessons"
    id           = Column(Integer, primary_key=True, index=True)
    title        = Column(String(255), nullable=False)
    description  = Column(Text)
    category     = Column(Enum("grammar","vocab","kanji","listening","reading"))
    level        = Column(Enum("N5","N4","N3","N2","N1"), nullable=False)
    kanji_icon   = Column(String(10))
    content      = Column(Text)
    order_num    = Column(Integer, default=0)
    is_published = Column(Boolean, default=False)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    vocabulary   = relationship("Vocabulary", back_populates="lesson")
    progress     = relationship("UserProgress", back_populates="lesson")

class Vocabulary(Base):
    __tablename__ = "vocabulary"
    id         = Column(Integer, primary_key=True, index=True)
    lesson_id  = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    word       = Column(String(50), nullable=False)
    hiragana   = Column(String(100), nullable=False)
    romaji     = Column(String(100))
    meaning_en = Column(String(500), nullable=False)
    meaning_vi = Column(String(500))
    example_jp = Column(Text)
    example_en = Column(Text)
    image_url  = Column(String(500))
    level      = Column(Enum("N5","N4","N3","N2","N1"))
    pos        = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    lesson     = relationship("Lesson", back_populates="vocabulary")

class FlashcardDeck(Base):
    __tablename__ = "flashcard_decks"
    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(255), nullable=False)
    description = Column(Text)
    level       = Column(Enum("N5","N4","N3","N2","N1"))
    card_count  = Column(Integer, default=0)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    cards       = relationship("Flashcard", back_populates="deck")

class Flashcard(Base):
    __tablename__ = "flashcards"
    id        = Column(Integer, primary_key=True, index=True)
    deck_id   = Column(Integer, ForeignKey("flashcard_decks.id"), nullable=False)
    front     = Column(Text, nullable=False)
    back      = Column(Text, nullable=False)
    image_url = Column(String(500))
    order_num = Column(Integer, default=0)
    deck      = relationship("FlashcardDeck", back_populates="cards")

class UserProgress(Base):
    __tablename__ = "user_progress"
    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id    = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    completed    = Column(Boolean, default=False)
    mastery_pct  = Column(Float, default=0.0)
    due_date     = Column(DateTime(timezone=True), nullable=True)
    last_review  = Column(DateTime(timezone=True), nullable=True)
    review_count = Column(Integer, default=0)
    updated_at   = Column(DateTime(timezone=True), onupdate=func.now())
    user         = relationship("User", back_populates="progress")
    lesson       = relationship("Lesson", back_populates="progress")