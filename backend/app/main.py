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

from .database import get_session, create_db_and_tables
from .models import EmployeeSystemActivity

app = FastAPI(
    title="Employee Activity Log Viewer with AI Summary",
    version="1.0.0"
)

# CORS configuration for your remote server
origins = [
    "http://localhost:3002",         # Kept for potential local testing
    "http://127.0.0.1:3002",       # Kept for potential local testing
    "http://192.168.1.214",          # Your remote server's base IP
    "http://192.168.1.214:3002",     # Your remote server's frontend port
    "http://frontend",                 # For Docker internal communication
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

summarizer = None
# Using the t5-small model for better instruction-following
SUMMARY_MODEL_NAME = "t5-small"

@app.on_event("startup")
async def on_startup():
    logger.info("Application startup...")
    try:
        create_db_and_tables()
        logger.info("Database connection and table creation successful!")
    except Exception as e:
        logger.error(f"ERROR: DB connection/creation failed: {e}")
        raise RuntimeError(f"Database setup failed: {e}")

    global summarizer
    try:
        logger.info(f"Loading AI model: {SUMMARY_MODEL_NAME}...")
        summarizer = pipeline("summarization", model=SUMMARY_MODEL_NAME, tokenizer=SUMMARY_MODEL_NAME)
        logger.info("AI model loaded successfully!")
    except Exception as e:
        logger.error(f"ERROR: AI model loading failed: {e}", exc_info=True)
        raise RuntimeError(f"AI model loading failed: {e}")

# --- CORRECTED /logs/ ENDPOINT WITH FULL FILTERING ---
@app.get("/logs/", response_model=List[EmployeeSystemActivity])
async def get_employee_system_logs(
    session: Session = Depends(get_session),
    employee_id: Optional[str] = Query(None, description="Filter by employee ID"),
    start_date: Optional[datetime] = Query(None, description="Filter logs from this date (YYYY-MM-DDTHH:MM:SS)"),
    end_date: Optional[datetime] = Query(None, description="Filter logs up to this date (YYYY-MM-DDTHH:MM:SS)"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    application_name: Optional[str] = Query(None, description="Filter by application name"),
    limit: int = Query(100, ge=1, le=1000, description="Number of logs to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    order_by_timestamp_desc: bool = Query(True, description="Order by timestamp descending")
):
    """
    Retrieve employee system activity logs with optional filters and pagination.
    """
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

    if order_by_timestamp_desc:
        statement = statement.order_by(EmployeeSystemActivity.timestamp.desc()) # type: ignore[attr-defined]
    else:
        statement = statement.order_by(EmployeeSystemActivity.timestamp.asc()) # type: ignore[attr-defined]

    statement = statement.limit(limit).offset(offset)
    
    logs = session.exec(statement).all()
    return logs

# Define a Pydantic model for the request body
class SummarizeRequest(BaseModel):
    log_ids: List[int]

# The intelligent summarization endpoint
@app.post("/summarize_logs/")
async def summarize_logs(
    request: SummarizeRequest,
    session: Session = Depends(get_session)
):
    if not summarizer:
        raise HTTPException(status_code=503, detail="AI summarizer model is not loaded or ready.")
    if not request.log_ids:
        raise HTTPException(status_code=400, detail="No log IDs provided.")

    statement = select(EmployeeSystemActivity).where(
        EmployeeSystemActivity.id.in_(request.log_ids)  # type: ignore[attr-defined]
    ).order_by(EmployeeSystemActivity.timestamp.asc())
    
    logs_to_summarize = session.exec(statement).all()

    if not logs_to_summarize:
        return {"summary": "No logs found for the given IDs."}

    # Build a narrative from the logs for the AI
    narrative_points = []
    last_window_title = None
    activity_in_window = set()

    for log in logs_to_summarize:
        if log.window_title != last_window_title and last_window_title is not None:
            if activity_in_window:
                actions = " and ".join(sorted(list(activity_in_window)))
                point = f"In the window titled '{last_window_title}', the user was {actions}."
                narrative_points.append(point)
            activity_in_window.clear()

        if log.event_type == "keyboard":
            activity_in_window.add("typing")
        elif log.event_type == "mouse_click":
            activity_in_window.add("clicking")
        
        last_window_title = log.window_title

    if activity_in_window and last_window_title:
        actions = " and ".join(sorted(list(activity_in_window)))
        point = f"Finally, in the window titled '{last_window_title}', the user was {actions}."
        narrative_points.append(point)

    if not narrative_points:
        return {"summary": "Not enough context from selected logs to generate a summary."}

    # Use prompt engineering for the T5 model
    prompt = "summarize: " + " ".join(narrative_points)
    
    logger.info(f"--- Sending text to AI ---\n{prompt}\n---------------------------")
    
    try:
        summary_result = summarizer(prompt, min_length=15, max_length=100, truncation=True)
        summary_text = summary_result[0]['summary_text']
        
        logger.info(f"--- AI generated summary ---\n{summary_text}\n--------------------------")
        
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
