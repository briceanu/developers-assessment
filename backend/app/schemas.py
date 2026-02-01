from enum import Enum
from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import SQLModel
from pydantic import BaseModel, model_validator


class TaskCreateIn(BaseModel):
    title: str
    description: Optional[str] = None


class TaskOut(BaseModel):
    id: UUID
    title: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True


class TimeSegmentIn(SQLModel):
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    notes: Optional[str] = None
#     # Validation

    @model_validator(mode='before')
    def end_after_start(cls, values):
        if values['end_time'] <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return values


class WorkLogCreateIn(BaseModel):
    """Create a worklog container (no time segments yet)."""
    task_id: UUID
    time_segments: list[TimeSegmentIn]


class TimeSegmentOut(BaseModel):
    """Time segment with calculated duration."""
    id: UUID
    worklog_id: UUID
    user_id: UUID
    start_time: datetime
    end_time: datetime
    description: Optional[str]
    notes: Optional[str]
    recorded_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


class WorkLogOut(BaseModel):
    """WorkLog with calculated totals."""
    id: UUID
    user_id: UUID
    task_id: UUID
    created_at: datetime
    total_duration_minutes: float  # Calculated from time_segments
    segment_count: int             # Number of time segments
    time_segments: list[TimeSegmentOut]


class DeleteTimeSegmentOut(BaseModel):
    success: str


class UpdateTimeSegmentIn(BaseModel):
    start_time: datetime
    end_time: datetime
    description: Optional[str]
    notes: Optional[str]
    model_config = {'extra': 'forbid'}


class UpdateTimeSegmentOut(BaseModel):
    description: str


# ============================================================================
# USAGE EXAMPLE
# ============================================================================


class RemittanceStatusSchemaIn(str, Enum):
    REMITTED = "REMITTED"
    UNREMITTED = "UNREMITTED"


"""
Example workflow:

1. CREATE WORKLOG (just a container):
   POST /worklogs
   {
       "user_id": "uuid-here",
       "task_id": "uuid-here"
   }
   
2. ADD TIME SEGMENTS (the actual work):
   POST /time-segments
   {
       "worklog_id": "worklog-uuid",
       "start_time": "2026-01-29T10:00:00",
       "end_time": "2026-01-29T10:30:00",
       "description": "Initial development"
   }
   
   POST /time-segments
   {
       "worklog_id": "worklog-uuid",
       "start_time": "2026-01-29T13:30:00",
       "end_time": "2026-01-29T14:00:00",
       "description": "Bug fixes"
   }
   
   POST /time-segments
   {
       "worklog_id": "worklog-uuid",
       "start_time": "2026-01-29T15:00:00",
       "end_time": "2026-01-29T16:00:00",
       "description": "Testing"
   }
   
3. ADD ADJUSTMENT (optional):
   POST /adjustments
   {
       "worklog_id": "worklog-uuid",
       "amount": -10.0,
       "reason": "Quality deduction"
   }

4. VIEW WORKLOG:
   GET /worklogs/{worklog_id}
   Response:
   {
       "id": "worklog-uuid",
       "user_id": "user-uuid",
       "task_id": "task-uuid",
       "total_duration_minutes": 120.0,  # 30 + 30 + 60
       "total_amount": 110.0,             # 120 - 10
       "segment_count": 3
   }
"""
