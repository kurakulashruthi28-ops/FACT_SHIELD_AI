from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'fact_shield.db'}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, index=True)
    analysis_type = Column(String(50), nullable=False)
    input_text = Column(Text, nullable=False)
    filename = Column(String(255), nullable=True)
    assessment = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    explanation = Column(Text, nullable=False)
    indicators = Column(Text, nullable=True)
    sources = Column(Text, nullable=True)
    claims = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

Base.metadata.create_all(bind=engine)

def save_analysis(text, analysis_type, result):
    db = SessionLocal()
    try:
        record = AnalysisHistory(
            analysis_type=analysis_type,
            input_text=text,
            filename=result.get("filename"),
            assessment=result.get("assessment", ""),
            confidence=result.get("confidence", 0),
            risk_score=result.get("risk_score", 0),
            explanation=result.get("explanation", ""),
            indicators=json.dumps(result.get("indicators", []), ensure_ascii=False),
            sources=json.dumps(result.get("sources", []), ensure_ascii=False),
            claims=json.dumps(result.get("claims", []), ensure_ascii=False),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record.id
    finally:
        db.close()

def get_history(limit=50):
    db = SessionLocal()
    try:
        records = db.query(AnalysisHistory).order_by(AnalysisHistory.created_at.desc()).limit(limit).all()
        return records
    finally:
        db.close()

def get_analysis(analysis_id):
    db = SessionLocal()
    try:
        return db.query(AnalysisHistory).filter(AnalysisHistory.id == analysis_id).first()
    finally:
        db.close()
