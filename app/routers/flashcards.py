from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/flashcards", tags=["Flashcards"])

@router.get("/decks")
def get_decks(level: Optional[str]=Query(None), page: int=Query(1,ge=1), limit: int=Query(20,le=100),
              db: Session=Depends(get_db), _=Depends(get_current_user)):
    q = db.query(models.FlashcardDeck)
    if level: q = q.filter(models.FlashcardDeck.level == level)
    return {"total": q.count(), "page": page, "data": q.offset((page-1)*limit).limit(limit).all()}

@router.get("/decks/{deck_id}/cards")
def get_cards(deck_id: int, db: Session=Depends(get_db), _=Depends(get_current_user)):
    deck = db.query(models.FlashcardDeck).filter(models.FlashcardDeck.id == deck_id).first()
    if not deck: raise HTTPException(404, "Không tìm thấy bộ flashcard")
    return {"deck": deck, "cards": deck.cards}

@router.post("/decks")
def create_deck(data: schemas.FlashcardDeckCreate, db: Session=Depends(get_db), _=Depends(require_admin)):
    deck = models.FlashcardDeck(**data.model_dump())
    db.add(deck); db.commit(); db.refresh(deck); return deck

@router.post("/cards")
def create_card(data: schemas.FlashcardCreate, db: Session=Depends(get_db), _=Depends(require_admin)):
    card = models.Flashcard(**data.model_dump())
    db.add(card)
    deck = db.query(models.FlashcardDeck).filter(models.FlashcardDeck.id == data.deck_id).first()
    if deck: deck.card_count += 1
    db.commit(); db.refresh(card); return card

@router.delete("/cards/{card_id}")
def delete_card(card_id: int, db: Session=Depends(get_db), _=Depends(require_admin)):
    card = db.query(models.Flashcard).filter(models.Flashcard.id == card_id).first()
    if not card: raise HTTPException(404, "Không tìm thấy thẻ")
    deck = db.query(models.FlashcardDeck).filter(models.FlashcardDeck.id == card.deck_id).first()
    if deck and deck.card_count > 0: deck.card_count -= 1
    db.delete(card); db.commit()
    return {"message": f"Đã xóa thẻ #{card_id}"}
