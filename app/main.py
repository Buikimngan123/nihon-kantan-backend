from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.routers import users, lessons, vocab, flashcards, progress
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Nihon Kantan API",
    description="Backend API cho ứng dụng học tiếng Nhật",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5500")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(users.router)
app.include_router(lessons.router)
app.include_router(vocab.router)
app.include_router(flashcards.router)
app.include_router(progress.router)

@app.get("/")
def root():
    return {"message": "Nihon Kantan API dang chay!"}