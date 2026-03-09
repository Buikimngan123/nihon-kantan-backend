from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import hash_password, verify_password, create_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.TokenResponse)
def register(data: schemas.UserRegister, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == data.email).first():
        raise HTTPException(400, "Email này đã được đăng ký")
    if db.query(models.User).filter(models.User.username == data.username).first():
        raise HTTPException(400, "Username này đã được sử dụng")
    user = models.User(email=data.email, username=data.username,
                       full_name=data.full_name, hashed_pw=hash_password(data.password))
    db.add(user); db.commit(); db.refresh(user)
    return {"access_token": create_token({"sub": str(user.id)}), "token_type": "bearer", "user": user}

@router.post("/login", response_model=schemas.TokenResponse)
def login(data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_pw):
        raise HTTPException(401, "Email hoặc mật khẩu không đúng")
    if user.status == "banned":
        raise HTTPException(403, "Tài khoản đã bị khóa")
    return {"access_token": create_token({"sub": str(user.id)}), "token_type": "bearer", "user": user}

@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user=Depends(get_current_user)):
    return current_user

@router.put("/change-password")
def change_password(old_pw: str, new_pw: str,
                    current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(old_pw, current_user.hashed_pw):
        raise HTTPException(400, "Mật khẩu cũ không đúng")
    current_user.hashed_pw = hash_password(new_pw)
    db.commit()
    return {"message": "Đổi mật khẩu thành công"}