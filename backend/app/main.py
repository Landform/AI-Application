# my-ai-log-viewer/backend/app/main.py
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlmodel import Session, select
from pydantic import BaseModel
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from .database import get_session, create_db_and_tables, engine
from .models import EmployeeSystemActivity

app = FastAPI(
    title="Employee Activity Log Viewer with AI Summary",
    version="1.0.0"
)

origins = [
    "http://localhost", "http://localhost:3001", "http://localhost:3002",
    "http://frontend", "http://127.0.0.1", "http://127.0.0.1:3001", "http://127.0.0.1:3002",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

summarizer = None
SUMMARY_MODEL_NAME = "sshleifer/distilbart-cnn-12-6"

@app.on_event("startup")
async def on_startup():
    logger.info("Application startup...")
    try:
        create_db_and_tables()
        logger.info("Database connection and table creation successful!")
    except Exception as e:
        logger.error(f"ERROR: Failed to connect to database or create tables on startup: {e}")
        raise RuntimeError(f"Database setup failed: {e}")

    global summarizer
    try:
        logger.info(f"Loading AI summarization model: {SUMMARY_MODEL_NAME}...")
        summarizer = pipeline("summarization", model=SUMMARY_MODEL_NAME, tokenizer=SUMMARY_MODEL_NAME)
        logger.info("AI summarization model loaded successfully!")
    except Exception as e:
        logger.error(f"ERROR: Failed to load AI model on startup: {e}")
        raise RuntimeError(f"AI model loading failed: {e}")


@app.get("/logs/", response_model=List[EmployeeSystemActivity])
async def get_employee_system_logs(session: Session = Depends(get_session), employee_id: Optional[str] = Query(None), start_date: Optional[datetime] = Query(None), end_date: Optional[datetime] = Query(None), event_type: Optional[str] = Query(None), application_name: Optional[str] = Query(None), limit: int = Query(100), offset: int = Query(0), order_by_timestamp_desc: bool = Query(True)):
    statement = select(EmployeeSystemActivity)
    if employee_id:
        statement = statement.where(EmployeeSystemActivity.employee_id == employee_id)
    if start_date:
        statement = statement.where(EmployeeSystemActivity.timestamp >= start_date)
    if end_date:
        statement = statement.where(EmployeeSystemActivity.timestamp <= end_date)
    if event_type:
        statement = statement.where(EmployeeSystemActivity.event_type == event_type)
    if application_name:
        statement = statement.where(EmployeeSystemActivity.application_name.ilike(f"%{application_name}%"))
    statement = statement.order_by(EmployeeSystemActivity.timestamp.desc() if order_by_timestamp_desc else EmployeeSystemActivity.timestamp.asc()).limit(limit).offset(offset)
    logs = session.exec(statement).all()
    return logs
    

class SummarizeRequest(BaseModel):
    log_ids: List[int]

@app.post("/summarize_logs/")
async def summarize_logs(
    request: SummarizeRequest,
    session: Session = Depends(get_session)
):
    if not request.log_ids:
        raise HTTPException(status_code=400, detail="No log IDs provided.")

    statement = select(EmployeeSystemActivity).where(
        EmployeeSystemActivity.id.in_(request.log_ids) # type: ignore
    ).order_by(EmployeeSystemActivity.timestamp.asc())
    
    logs_to_summarize = session.exec(statement).all()

    if not logs_to_summarize:
        return {"summary": "No logs found for the given IDs."}

    # --- NEW: Build a very simple, clean string for the AI ---
    simple_actions = []
    for log in logs_to_summarize:
        app = log.application_name or "an unknown application"
        if log.event_type == "app_focus":
            simple_actions.append(f"User focused on {app}.")
        elif log.event_type == "mouse_click":
            simple_actions.append(f"User clicked in {app}.")
        elif log.event_type == "keyboard":
            simple_actions.append(f"User typed in {app}.")

    # Use a set to get unique actions, then join them. This prevents massive repetition.
    unique_actions = list(dict.fromkeys(simple_actions))
    text_input = " ".join(unique_actions)
    # --- END OF NEW LOGIC ---

    if not text_input:
        return {"summary": "No actions to summarize from the selected logs."}

    # Log the exact text being sent to the AI
    logger.info(f"--- Sending text to AI for summarization ---\n{text_input}\n-----------------------------------------")

    try:
        # Use slightly different summarization parameters
        summary_result = summarizer(text_input, min_length=15, max_length=100, truncation=True)
        summary_text = summary_result[0]['summary_text']

        logger.info(f"--- AI generated summary ---\n{summary_text}\n-----------------------------------------")

        return {
            "employee_id": logs_to_summarize[0].employee_id,
            "num_logs_summarized": len(logs_to_summarize),
            "summary": summary_text
        }
    except Exception as e:
        logger.error(f"CRITICAL: AI summarization pipeline failed. Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="AI model failed to process the request.")


@app.get("/health/")
async def health_check():
    return {"status": "ok", "message": "API is running", "ai_model_loaded": summarizer is not None}