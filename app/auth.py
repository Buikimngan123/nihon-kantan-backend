from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
import os

SECRET_KEY    = os.getenv("SECRET_KEY", "change-this-secret")
ALGORITHM     = os.getenv("ALGORITHM", "HS256")
EXPIRE_MIN    = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 10080))
pwd_context   = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(data: dict) -> str:
    payload = data.copy()
    payload.update({"exp": datetime.utcnow() + timedelta(minutes=EXPIRE_MIN)})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    err = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token không hợp lệ hoặc đã hết hạn",
                        headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise err
    except JWTError:
        raise err
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user or user.status == "banned":
        raise err
    return user

def require_admin(current_user=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Không có quyền admin")
    return current_user