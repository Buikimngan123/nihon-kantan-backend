from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/lessons", tags=["Lessons"])

@router.get("/")
def get_lessons(level: Optional[str]=Query(None), category: Optional[str]=Query(None),
                page: int=Query(1,ge=1), limit: int=Query(20,le=100),
                db: Session=Depends(get_db), _=Depends(get_current_user)):
    q = db.query(models.Lesson).filter(models.Lesson.is_published == True)
    if level:    q = q.filter(models.Lesson.level == level)
    if category: q = q.filter(models.Lesson.category == category)
    return {"total": q.count(), "page": page,
            "data": q.order_by(models.Lesson.order_num).offset((page-1)*limit).limit(limit).all()}

@router.get("/{lesson_id}")
def get_lesson(lesson_id: int, db: Session=Depends(get_db), _=Depends(get_current_user)):
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson: raise HTTPException(404, "Không tìm thấy bài học")
    return lesson

@router.post("/")
def create_lesson(data: schemas.LessonCreate, db: Session=Depends(get_db), _=Depends(require_admin)):
    lesson = models.Lesson(**data.model_dump())
    db.add(lesson); db.commit(); db.refresh(lesson)
    return lesson

@router.put("/{lesson_id}")
def update_lesson(lesson_id: int, data: schemas.LessonCreate,
                  db: Session=Depends(get_db), _=Depends(require_admin)):
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson: raise HTTPException(404, "Không tìm thấy bài học")
    for k, v in data.model_dump().items(): setattr(lesson, k, v)
    db.commit(); return lesson

@router.delete("/{lesson_id}")
def delete_lesson(lesson_id: int, db: Session=Depends(get_db), _=Depends(require_admin)):
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson: raise HTTPException(404, "Không tìm thấy bài học")
    db.delete(lesson); db.commit()
    return {"message": f"Đã xóa bài học #{lesson_id}"}