# my-ai-log-viewer/backend/app/models.py
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

# This SQLModel maps to the 'employee_system_activity' table in PostgreSQL
class EmployeeSystemActivity(SQLModel, table=True):
    __tablename__ = "employee_system_activity"

    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    event_type: str
    application_name: Optional[str] = None
    window_title: Optional[str] = None
    event_detail: Optional[str] = None
    screenshot_path: Optional[str] = None