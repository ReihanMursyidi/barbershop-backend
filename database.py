import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Gunakan POSTGRES_URL sesuai dengan yang disediakan Vercel & Supabase
DATABASE_URL = os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")

# 2. Ubah awalan postgres:// menjadi postgresql:// agar diterima oleh SQLAlchemy
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if not DATABASE_URL:
    raise ValueError("POSTGRES_URL tidak ditemukan! Pastikan Environment Variables sudah terpasang di Vercel.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
