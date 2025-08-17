# my-ai-log-viewer/backend/app/main.py
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlmodel import Session, select
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline

from .database import get_session, create_db_and_tables
from .models import EmployeeSystemActivity

# Init FastAPI app
app = FastAPI(
    title="Employee Activity Log Viewer with AI Summary",
    description="API for fetching and summarizing employee logs.",
    version="1.0.0"
)

# CORS configuration to allow frontend to communicate with backend
origins = [
    "http://localhost",       # For local access after compose up
    "http://localhost:3001",  # Frontend mapped port
    "http://frontend"         # Docker internal service name for frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global summarizer pipeline (will be loaded once on startup)
summarizer = None
SUMMARY_MODEL_NAME = "sshleifer/distilbart-cnn-12-6"

@app.on_event("startup")
async def on_startup():
    print("Application startup...")
    # Verify database connection and create tables
    try:
        with Session(get_session()):
            print("Database connection successful!")
        create_db_and_tables()
        print("Database tables created/checked successfully.")
    except Exception as e:
        print(f"ERROR: Failed to connect to database or create tables on startup: {e}")
        raise RuntimeError(f"Database setup failed: {e}")

    # Load AI model
    global summarizer
    try:
        print(f"Loading AI summarization model: {SUMMARY_MODEL_NAME}...")
        summarizer = pipeline("summarization", model=SUMMARY_MODEL_NAME, tokenizer=SUMMARY_MODEL_NAME)
        print("AI summarization model loaded successfully!")
    except Exception as e:
        print(f"ERROR: Failed to load AI model on startup: {e}")
        raise RuntimeError(f"AI model loading failed: {e}")


@app.get("/logs/", response_model=List[EmployeeSystemActivity])
async def get_employee_system_logs(
    session: Session = Depends(get_session),
    employee_id: Optional[str] = Query(None, description="Filter by employee ID"),
    start_date: Optional[datetime] = Query(None, description="Filter logs from this date (YYYY-MM-DDTHH:MM:SS)"),
    end_date: Optional[datetime] = Query(None, description="Filter logs up to this date (YYYY-MM-DDTHH:MM:SS)"),
    event_type: Optional[str] = Query(None, description="Filter by event type (e.g., 'keyboard', 'mouse_click', 'app_focus')"),
    application_name: Optional[str] = Query(None, description="Filter by application name"),
    limit: int = Query(100, ge=1, le=1000, description="Number of logs to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    order_by_timestamp_desc: bool = Query(True, description="Order by timestamp descending (newest first)")
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
        statement = statement.order_by(EmployeeSystemActivity.timestamp.desc())
    else:
        statement = statement.order_by(EmployeeSystemActivity.timestamp.asc())

    statement = statement.limit(limit).offset(offset)

    try:
        logs = session.exec(statement).all()
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve logs: {e}")

@app.post("/summarize_logs/")
async def summarize_logs(
    log_ids: List[int],
    session: Session = Depends(get_session)
):
    """
    Summarizes a selection of employee activity logs using AI.
    """
    if not summarizer:
        raise HTTPException(status_code=503, detail="AI summarizer model is not loaded or ready.")

    if not log_ids:
        raise HTTPException(status_code=400, detail="No log IDs provided for summarization.")

    statement = select(EmployeeSystemActivity).where(EmployeeSystemActivity.id.in_(log_ids)).order_by(EmployeeSystemActivity.timestamp.asc())
    try:
        logs_to_summarize = session.exec(statement).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve logs for summarization: {e}")

    if not logs_to_summarize:
        return {"summary": "No logs found for the given IDs."}

    full_text_for_summary = []
    current_employee = None
    for log in logs_to_summarize:
        if not current_employee:
            current_employee = log.employee_id

        log_entry_desc = (
            f"[{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] "
            f"{log.event_type} in '{log.application_name}' (Window: '{log.window_title}'). "
            f"Details: '{log.event_detail or ''}'."
        )
        full_text_for_summary.append(log_entry_desc)

    text_input = " ".join(full_text_for_summary)

    MAX_INPUT_CHARS = 3000
    if len(text_input) > MAX_INPUT_CHARS:
        text_input = text_input[:MAX_INPUT_CHARS] + "..."
        print(f"Warning: Input text for summarization truncated to {MAX_INPUT_CHARS} characters.")

    try:
        summary_result = summarizer(text_input, min_length=50, max_length=200, do_sample=False)
        summary_text = summary_result[0]['summary_text']
        return {
            "employee_id": current_employee,
            "num_logs_summarized": len(logs_to_summarize),
            "summary": summary_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI summarization failed: {e}. Check backend logs for more details.")

@app.get("/health/")
async def health_check():
    return {"status": "ok", "message": "API is running", "ai_model_loaded": summarizer is not None}