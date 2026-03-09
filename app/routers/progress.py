from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app import models
from app.auth import get_current_user

router = APIRouter(prefix="/api/progress", tags=["Progress"])

@router.get("/me")
def get_my_progress(current_user=Depends(get_current_user), db: Session=Depends(get_db)):
    progress = db.query(models.UserProgress).filter(
        models.UserProgress.user_id == current_user.id).all()
    return {"user": {"name": current_user.full_name, "level": current_user.level,
                     "streak": current_user.streak, "xp": current_user.xp}, "progress": progress}

@router.post("/{lesson_id}/complete")
def mark_completed(lesson_id: int, current_user=Depends(get_current_user), db: Session=Depends(get_db)):
    if not db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first():
        raise HTTPException(404, "Không tìm thấy bài học")
    prog = db.query(models.UserProgress).filter(
        models.UserProgress.user_id == current_user.id,
        models.UserProgress.lesson_id == lesson_id).first()
    if not prog:
        prog = models.UserProgress(user_id=current_user.id, lesson_id=lesson_id)
        db.add(prog)
    prog.completed = True
    prog.mastery_pct = min(prog.mastery_pct + 20, 100)
    prog.review_count += 1
    prog.last_review = datetime.utcnow()
    prog.due_date = datetime.utcnow() + timedelta(days=prog.review_count * 2)
    current_user.xp += 50
    db.commit()
    return {"message": "Hoàn thành bài học!", "xp_earned": 50}
