# seed.py – Chạy một lần để thêm dữ liệu mẫu
from app.database import SessionLocal, engine, Base
from app.models import User, Lesson, Vocabulary, FlashcardDeck, Flashcard
from app.auth import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

print("□ Đang seed dữ liệu...")

# — Tạo tài khoản admin ——————
admin = User(
    email       = "admin@nihonkantan.com",
    username    = "admin",
    full_name   = "Administrator",
    hashed_pw   = hash_password("Admin@123"),
    is_admin    = True,
    level       = "N1"
)
db.add(admin)

# — Tạo tài khoản học viên mẫu ——————
student = User(
    email       = "student@example.com",
    username    = "sato_yuki",
    full_name   = "Sato Yuki",
    hashed_pw   = hash_password("Student@123"),
    level       = "N4",
    streak      = 14,
    xp          = 1240
)
db.add(student)

# — Tạo bài học mẫu ——————
lessons_data = [
    {"title":"Bảng chữ Hiragana", "category":"vocab",  "level":"N5", "kanji_icon":"あ", "is_published":True},
    {"title":"Động từ nhóm 1",    "category":"grammar", "level":"N5", "kanji_icon":"動", "is_published":True},
    {"title":"Chia động từ て",   "category":"grammar", "level":"N4", "kanji_icon":"て", "is_published":True},
    {"title":"Từ vựng: Ẩm thực",  "category":"vocab",   "level":"N4", "kanji_icon":"食", "is_published":True},
    {"title":"Kanji: Cảm xúc",    "category":"kanji",   "level":"N3", "kanji_icon":"感", "is_published":True},
]

lesson_objs = []
for i, data in enumerate(lessons_data):
    lesson = Lesson(**data, order_num=i+1)
    db.add(lesson)
    lesson_objs.append(lesson)

db.commit()

# — Tạo từ vựng cho bài học đầu ——————
vocab_data = [
    {"word":"桜", "hiragana":"さくら", "romaji":"sakura", "meaning_en":"Cherry Blossom", "meaning_vi":"Hoa anh đào", "level":"N4"},
    {"word":"山", "hiragana":"やま",   "romaji":"yama",   "meaning_en":"Mountain",       "meaning_vi":"Núi",         "level":"N5"},
    {"word":"海", "hiragana":"うみ",   "romaji":"umi",    "meaning_en":"Sea",            "meaning_vi":"Biển",        "level":"N5"},
]
for v_data in vocab_data:
    vocab = Vocabulary(**v_data, lesson_id=lesson_objs[0].id)
    db.add(vocab)

db.commit()
db.close()
print("□ Seed xong! Admin: admin@nihonkantan.com / Admin@123")