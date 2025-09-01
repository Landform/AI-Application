# my-ai-log-viewer/backend/app/main.py
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlmodel import Session, select
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
from sqlalchemy import func, text
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from .database import get_session, create_db_and_tables
from .models import EmployeeSystemActivity

app = FastAPI(
    title="Employee Activity Log Viewer",
    version="1.0.0"
)

# CORS configuration for local development
origins = [
    "http://localhost:3002",
    "http://127.0.0.1:3002",
]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

summarizer = None
SUMMARY_MODEL_NAME = "t5-small"

# List of applications considered productive for analysis
PRODUCTIVE_APPS = [
    'Code.exe', 'Code',
    'WINWORD.EXE', 'EXCEL.EXE', 'POWERPNT.EXE', 'OUTLOOK.EXE',
    'firefox.exe',
    'chrome.exe',
    'explorer.exe',
    'powershell.exe',
    'cmd.exe',
    'Visual Studio Code',
    'Mozilla Firefox',
    'Google Chrome',
]

@app.on_event("startup")
async def on_startup():
    logger.info("Application startup...")
    create_db_and_tables()
    global summarizer
    try:
        logger.info(f"Loading AI model: {SUMMARY_MODEL_NAME}...")
        summarizer = pipeline("summarization", model=SUMMARY_MODEL_NAME, tokenizer=SUMMARY_MODEL_NAME)
        logger.info("AI model loaded successfully!")
    except Exception as e:
        logger.error(f"ERROR: AI model loading failed: {e}", exc_info=True)
        summarizer = None

@app.get("/logs/", response_model=List[EmployeeSystemActivity])
async def get_employee_system_logs(
    session: Session = Depends(get_session),
    employee_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    application_name: Optional[str] = Query(None),
    limit: int = Query(100),
    offset: int = Query(0),
    order_by_timestamp_desc: bool = Query(True)
):
    statement = select(EmployeeSystemActivity)
    if employee_id:
        statement = statement.where(EmployeeSystemActivity.employee_id == employee_id)
    if event_type:
        statement = statement.where(EmployeeSystemActivity.event_type == event_type)
    if application_name:
        statement = statement.where(EmployeeSystemActivity.application_name.ilike(f"%{application_name}%"))
    if order_by_timestamp_desc:
        statement = statement.order_by(EmployeeSystemActivity.timestamp.desc()) # type: ignore
    else:
        statement = statement.order_by(EmployeeSystemActivity.timestamp.asc()) # type: ignore
    statement = statement.limit(limit).offset(offset)
    logs = session.exec(statement).all()
    return logs

# --- Pydantic Models for API Payloads ---
class SummarizeRequest(BaseModel):
    log_ids: List[int]

class InfographicData(BaseModel):
    deep_work_hours: float
    context_switches: int
    overtime_events: int

class OvertimeDataPoint(BaseModel):
    category: str
    execution_events: int
    communication_events: int

class HeatmapDataPoint(BaseModel):
    day: str
    hour: int
    focus_score: float

# --- API Endpoints ---

@app.post("/summarize_logs/")
async def summarize_logs(request: SummarizeRequest, session: Session = Depends(get_session)):
    if not summarizer:
        raise HTTPException(status_code=503, detail="AI model is not available.")
    if not request.log_ids:
        raise HTTPException(status_code=400, detail="No log IDs provided.")

    statement = select(EmployeeSystemActivity).where(EmployeeSystemActivity.id.in_(request.log_ids)).order_by(EmployeeSystemActivity.timestamp.asc()) # type: ignore
    logs_to_summarize = session.exec(statement).all()

    if not logs_to_summarize:
        return {"summary": "No logs found for the given IDs."}

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
        return {"summary": "Not enough context to summarize."}

    prompt = "summarize: " + " ".join(narrative_points)

    try:
        summary_result = summarizer(prompt, min_length=15, max_length=100, truncation=True)
        summary_text = summary_result[0]['summary_text']
        return {
            "employee_id": logs_to_summarize[0].employee_id,
            "num_logs_summarized": len(logs_to_summarize),
            "summary": summary_text
        }
    except Exception as e:
        logger.error(f"CRITICAL: AI summarization pipeline failed. Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="AI model failed to process request.")

@app.get("/api/dashboard/infographic-data", response_model=InfographicData)
async def get_infographic_data(
    session: Session = Depends(get_session),
    target_date_str: Optional[str] = Query(None)
):
    now_utc = datetime.now(timezone.utc)
    day_start_utc = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end_utc = day_start_utc + timedelta(days=1)
    core_hours_start_utc = day_start_utc.replace(hour=9)
    core_hours_end_utc = day_start_utc.replace(hour=18)

    statement = select(EmployeeSystemActivity).where(
        EmployeeSystemActivity.timestamp >= day_start_utc,
        EmployeeSystemActivity.timestamp < day_end_utc
    ).order_by(EmployeeSystemActivity.timestamp.asc())
    
    logs = session.exec(statement).all()

    if not logs:
        return InfographicData(deep_work_hours=0, context_switches=0, overtime_events=0)

    deep_work_seconds = 0
    context_switches = 0
    overtime_events = 0
    last_app_name = logs[0].application_name
    last_productive_timestamp = None

    for i, log in enumerate(logs):
        log_timestamp_utc = log.timestamp.replace(tzinfo=timezone.utc)

        if not (core_hours_start_utc <= log_timestamp_utc < core_hours_end_utc):
            overtime_events += 1

        if log.event_type == 'app_focus' and log.application_name != last_app_name:
            context_switches += 1
        last_app_name = log.application_name

        is_productive = any(prod_app in (log.application_name or "") for prod_app in PRODUCTIVE_APPS)
        
        if is_productive:
            if last_productive_timestamp is None:
                last_productive_timestamp = log_timestamp_utc
            if i == len(logs) - 1:
                duration = (log_timestamp_utc - last_productive_timestamp).total_seconds()
                deep_work_seconds += duration
        else:
            if last_productive_timestamp is not None:
                duration = (log_timestamp_utc - last_productive_timestamp).total_seconds()
                if duration > 120:
                    deep_work_seconds += duration
            last_productive_timestamp = None

    calculated_data = InfographicData(
        deep_work_hours=round(deep_work_seconds / 3600, 1),
        context_switches=context_switches,
        overtime_events=overtime_events
    )
    logger.info(f"--- Calculated Infographic Data: {calculated_data.dict()} ---")
    
    return calculated_data

@app.get("/api/dashboard/overtime-analysis", response_model=List[OvertimeDataPoint])
async def get_overtime_analysis(session: Session = Depends(get_session)):
    core_hours_end = 10 # Temporarily set to 10 AM for easy testing
    
    COMMUNICATION_APPS = ['OUTLOOK.EXE', 'slack.exe', 'teams.exe']

    query = text(f"""
        SELECT
            CASE
                WHEN application_name = ANY(:comm_apps) THEN 'Communication'
                WHEN application_name = ANY(:prod_apps) THEN 'Core Development'
                ELSE 'Other'
            END as category,
            SUM(CASE WHEN event_type IN ('keyboard', 'mouse_click') THEN 1 ELSE 0 END) as execution_events,
            SUM(CASE WHEN event_type = 'app_focus' THEN 1 ELSE 0 END) as communication_events
        FROM employee_system_activity
        WHERE EXTRACT(HOUR FROM timestamp) >= {core_hours_end}
        GROUP BY category
        ORDER BY category;
    """)
    
    results = session.exec(query, params={"comm_apps": COMMUNICATION_APPS, "prod_apps": PRODUCTIVE_APPS}).all()

    return [OvertimeDataPoint(
        category=row.category,
        execution_events=row.execution_events,
        communication_events=row.communication_events
    ) for row in results]

# In main.py, replace the existing get_focus_heatmap function

@app.get("/api/dashboard/focus-heatmap", response_model=List[HeatmapDataPoint])
async def get_focus_heatmap(session: Session = Depends(get_session)):
    """
    [TEMP DEBUG VERSION] Calculates an activity score per minute for the last hour
    to make the heatmap populate quickly for testing.
    """
    one_hour_ago = datetime.now() - timedelta(hours=1)

    # This query groups events by application and by the minute they occurred.
    query = text("""
        SELECT
            application_name as day, -- We'll re-use the 'day' field for app name
            EXTRACT(MINUTE FROM timestamp)::integer as hour, -- Re-use 'hour' for minute
            COUNT(*)::float / 20.0 as focus_score -- Scale score based on 20 events
        FROM employee_system_activity
        WHERE timestamp >= :start_date
        GROUP BY application_name, hour
        ORDER BY application_name, hour;
    """)

    results = session.exec(query, params={"start_date": one_hour_ago}).all()

    # If no data, return a dummy point so the chart doesn't break
    if not results:
        return [HeatmapDataPoint(day="No Data", hour=0, focus_score=0.1)]

    return [HeatmapDataPoint(
        day=row.day or "Unknown", # Use app name as the 'day' label
        hour=row.hour,            # Use minute as the 'hour' label
        focus_score=min(1.0, row.focus_score)
    ) for row in results]

    return [HeatmapDataPoint(
        day=row.day_of_week.strip(),
        hour=int(row.hour_of_day),
        focus_score=min(1.0, row.focus_score)
    ) for row in results]

@app.get("/health/")
def health_check():
    return {"status": "ok"}