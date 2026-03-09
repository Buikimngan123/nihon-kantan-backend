from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from typing import Optional
from PIL import Image
import uuid, os, io
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/vocab", tags=["Vocabulary"])
UPLOAD_DIR = "uploads/vocab"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/")
def get_vocab(lesson_id: Optional[int]=Query(None), level: Optional[str]=Query(None),
              page: int=Query(1,ge=1), limit: int=Query(20,le=100),
              db: Session=Depends(get_db), _=Depends(get_current_user)):
    q = db.query(models.Vocabulary)
    if lesson_id: q = q.filter(models.Vocabulary.lesson_id == lesson_id)
    if level:     q = q.filter(models.Vocabulary.level == level)
    return {"total": q.count(), "page": page, "data": q.offset((page-1)*limit).limit(limit).all()}

@router.post("/")
def create_vocab(data: schemas.VocabCreate, db: Session=Depends(get_db), _=Depends(require_admin)):
    vocab = models.Vocabulary(**data.model_dump())
    db.add(vocab); db.commit(); db.refresh(vocab); return vocab

@router.put("/{vocab_id}")
def update_vocab(vocab_id: int, data: schemas.VocabCreate,
                 db: Session=Depends(get_db), _=Depends(require_admin)):
    vocab = db.query(models.Vocabulary).filter(models.Vocabulary.id == vocab_id).first()
    if not vocab: raise HTTPException(404, "Không tìm thấy từ vựng")
    for k, v in data.model_dump().items(): setattr(vocab, k, v)
    db.commit(); return vocab

@router.delete("/{vocab_id}")
def delete_vocab(vocab_id: int, db: Session=Depends(get_db), _=Depends(require_admin)):
    vocab = db.query(models.Vocabulary).filter(models.Vocabulary.id == vocab_id).first()
    if not vocab: raise HTTPException(404, "Không tìm thấy từ vựng")
    db.delete(vocab); db.commit()
    return {"message": f"Đã xóa từ vựng #{vocab_id}"}

@router.post("/{vocab_id}/image")
async def upload_image(vocab_id: int, file: UploadFile=File(...),
                       db: Session=Depends(get_db), _=Depends(require_admin)):
    if file.content_type not in ["image/jpeg","image/png","image/webp"]:
        raise HTTPException(400, "Chỉ chấp nhận JPEG, PNG hoặc WebP")
    contents = await file.read()
    if len(contents) > 2*1024*1024: raise HTTPException(400, "Ảnh không được vượt quá 2MB")
    img = Image.open(io.BytesIO(contents))
    img.thumbnail((800, 800))
    filename = f"{uuid.uuid4().hex}.webp"
    img.save(os.path.join(UPLOAD_DIR, filename), "WEBP", quality=85)
    vocab = db.query(models.Vocabulary).filter(models.Vocabulary.id == vocab_id).first()
    if not vocab: raise HTTPException(404, "Không tìm thấy từ vựng")
    vocab.image_url = f"/uploads/vocab/{filename}"
    db.commit()
    return {"image_url": vocab.image_url}
