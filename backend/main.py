# main.py

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os


# ============================================================
# 1. FASTAPI APP
# ============================================================

app = FastAPI(
    title="FACT SHIELD AI",
    description="AI-Powered Information & Internship Offer Verification",
    version="1.0.0"
)


# ============================================================
# 2. CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 3. DATABASE CONFIGURATION
# ============================================================

# SQLite database file
DATABASE_URL = "sqlite:///./factshield.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# ============================================================
# 4. DATABASE TABLE
# ============================================================

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)

    analysis_type = Column(String(50), nullable=False)

    input_text = Column(Text, nullable=True)

    file_name = Column(String(255), nullable=True)

    assessment = Column(String(100), nullable=False)

    confidence = Column(Integer, nullable=False)

    explanation = Column(Text, nullable=True)

    warning_indicators = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# Create database and table automatically
Base.metadata.create_all(bind=engine)


# ============================================================
# 5. REQUEST MODEL
# ============================================================

class AnalysisRequest(BaseModel):
    text: str
    analysis_type: str = "news"


# ============================================================
# 6. AI / ANALYSIS FUNCTION
# ============================================================

def analyze_content(text: str, analysis_type: str):
    """
    Basic FACT SHIELD analysis.

    You can later connect Gemini/OpenAI/API/RAG
    inside this function.
    """

    text_lower = text.lower()

    warning_words = [
        "urgent",
        "limited time",
        "click here",
        "send money",
        "pay now",
        "registration fee",
        "processing fee",
        "guaranteed job",
        "guaranteed internship",
        "otp",
        "password",
        "bank details",
        "account details",
        "crypto",
        "investment",
        "winner",
        "congratulations",
        "claim now"
    ]

    found_warnings = []

    for word in warning_words:
        if word in text_lower:
            found_warnings.append(word)

    # --------------------------------------------------------
    # INTERNSHIP ANALYSIS
    # --------------------------------------------------------

    if analysis_type.lower() == "internship":

        if len(found_warnings) >= 4:

            assessment = "HIGH CAUTION"
            confidence = 90

            explanation = (
                "Several warning indicators were detected in the "
                "submitted internship offer. These indicators do not "
                "independently prove fraud, but the offer should be "
                "independently verified before sharing personal "
                "information or making payments."
            )

        elif len(found_warnings) >= 2:

            assessment = "CAUTION"
            confidence = 75

            explanation = (
                "Some warning indicators were detected in the "
                "internship offer. Verify the company, recruiter, "
                "official website and contact details before proceeding."
            )

        else:

            assessment = "LOW WARNING SIGNS"
            confidence = 55

            explanation = (
                "No major warning indicators were detected from the "
                "submitted content. This does not prove that the offer "
                "is legitimate. Verify the organization independently."
            )

    # --------------------------------------------------------
    # NEWS ANALYSIS
    # --------------------------------------------------------

    else:

        if len(found_warnings) >= 4:

            assessment = "HIGH CAUTION"
            confidence = 85

            explanation = (
                "The submitted information contains several indicators "
                "that require additional verification. Check reliable "
                "sources before treating the claim as factual."
            )

        elif len(found_warnings) >= 2:

            assessment = "UNCERTAIN"
            confidence = 65

            explanation = (
                "Some warning indicators were detected. Additional "
                "verification from reliable sources is recommended."
            )

        else:

            assessment = "UNCERTAIN"
            confidence = 35

            explanation = (
                "No major warning indicators were detected from the "
                "submitted content. This does not prove that the "
                "information is true. Additional verification is "
                "recommended."
            )

    if found_warnings:
        warning_indicators = ", ".join(found_warnings)
    else:
        warning_indicators = "No obvious warning indicators"

    return {
        "assessment": assessment,
        "confidence": confidence,
        "explanation": explanation,
        "warning_indicators": warning_indicators
    }


# ============================================================
# 7. SAVE RESULT TO DATABASE
# ============================================================

def save_analysis(
    analysis_type,
    input_text,
    file_name,
    result
):

    db = SessionLocal()

    try:

        new_analysis = Analysis(
            analysis_type=analysis_type,
            input_text=input_text,
            file_name=file_name,
            assessment=result["assessment"],
            confidence=result["confidence"],
            explanation=result["explanation"],
            warning_indicators=result["warning_indicators"]
        )

        db.add(new_analysis)

        db.commit()

        db.refresh(new_analysis)

        return new_analysis.id

    finally:

        db.close()


# ============================================================
# 8. HOME API
# ============================================================

@app.get("/")
def home():

    return {
        "message": "FACT SHIELD AI Backend is running",
        "status": "online",
        "database": "connected",
        "version": "1.0.0"
    }


# ============================================================
# 9. ANALYZE TEXT
# ============================================================

@app.post("/analyze")
def analyze(request: AnalysisRequest):

    result = analyze_content(
        request.text,
        request.analysis_type
    )

    analysis_id = save_analysis(
        analysis_type=request.analysis_type,
        input_text=request.text,
        file_name=None,
        result=result
    )

    return {
        "success": True,
        "analysis_id": analysis_id,
        "analysis_type": request.analysis_type,
        "result": result
    }


# ============================================================
# 10. ANALYZE FILE
# ============================================================

@app.post("/analyze-file")
async def analyze_file(
    file: UploadFile = File(...),
    analysis_type: str = Form("document")
):

    try:

        content = await file.read()

        # Try to decode text files
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = (
                f"File uploaded: {file.filename}. "
                "The file content could not be read as plain text."
            )

        result = analyze_content(
            text,
            analysis_type
        )

        analysis_id = save_analysis(
            analysis_type=analysis_type,
            input_text=text,
            file_name=file.filename,
            result=result
        )

        return {
            "success": True,
            "analysis_id": analysis_id,
            "file_name": file.filename,
            "analysis_type": analysis_type,
            "result": result
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# 11. GET ALL ANALYSIS HISTORY
# ============================================================

@app.get("/history")
def get_history():

    db = SessionLocal()

    try:

        records = (
            db.query(Analysis)
            .order_by(Analysis.id.desc())
            .all()
        )

        result = []

        for record in records:

            result.append({
                "id": record.id,
                "analysis_type": record.analysis_type,
                "input_text": record.input_text,
                "file_name": record.file_name,
                "assessment": record.assessment,
                "confidence": record.confidence,
                "explanation": record.explanation,
                "warning_indicators": record.warning_indicators,
                "created_at": (
                    record.created_at.isoformat()
                    if record.created_at
                    else None
                )
            })

        return {
            "success": True,
            "count": len(result),
            "history": result
        }

    finally:

        db.close()


# ============================================================
# 12. GET ONE ANALYSIS BY ID
# ============================================================

@app.get("/history/{analysis_id}")
def get_analysis(analysis_id: int):

    db = SessionLocal()

    try:

        record = (
            db.query(Analysis)
            .filter(Analysis.id == analysis_id)
            .first()
        )

        if not record:

            return {
                "success": False,
                "message": "Analysis not found"
            }

        return {
            "success": True,
            "analysis": {
                "id": record.id,
                "analysis_type": record.analysis_type,
                "input_text": record.input_text,
                "file_name": record.file_name,
                "assessment": record.assessment,
                "confidence": record.confidence,
                "explanation": record.explanation,
                "warning_indicators": record.warning_indicators,
                "created_at": (
                    record.created_at.isoformat()
                    if record.created_at
                    else None
                )
            }
        }

    finally:

        db.close()


# ============================================================
# 13. DELETE ONE ANALYSIS
# ============================================================

@app.delete("/history/{analysis_id}")
def delete_analysis(analysis_id: int):

    db = SessionLocal()

    try:

        record = (
            db.query(Analysis)
            .filter(Analysis.id == analysis_id)
            .first()
        )

        if not record:

            return {
                "success": False,
                "message": "Analysis not found"
            }

        db.delete(record)

        db.commit()

        return {
            "success": True,
            "message": "Analysis deleted successfully"
        }

    finally:

        db.close()


# ============================================================
# 14. DATABASE STATUS
# ============================================================

@app.get("/database")
def database_status():

    db = SessionLocal()

    try:

        count = db.query(Analysis).count()

        return {
            "database": "SQLite",
            "database_file": "factshield.db",
            "status": "connected",
            "total_analyses": count
        }

    finally:

        db.close()


# ============================================================
# 15. RUN SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )