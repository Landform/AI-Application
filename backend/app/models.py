# my-ai-log-viewer/backend/app/models.py
from datetime import datetime
from typing import Optional, Literal # Keep Literal if you added it previously
from sqlmodel import Field, SQLModel

# This SQLModel maps to the 'employee_system_activity' table in PostgreSQL
class EmployeeSystemActivity(SQLModel, table=True):
    # This line tells Pylance to ignore the specific type incompatibility warning
    __tablename__: Literal["employee_system_activity"] = "employee_system_activity"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    event_type: str
    application_name: Optional[str] = None
    window_title: Optional[str] = None
    event_detail: Optional[str] = None
    screenshot_path: Optional[str] = None