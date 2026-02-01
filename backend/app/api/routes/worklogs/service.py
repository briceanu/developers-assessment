import uuid
from app.schemas import (
    DeleteTimeSegmentOut,
    TimeSegmentOut,
    UpdateTimeSegmentIn,
    WorkLogCreateIn,
    TimeSegmentIn,
    WorkLogOut,
    UpdateTimeSegmentOut,
)
from fastapi import HTTPException
from sqlmodel import Session, col, delete, select
from app.models import WorkLog, TimeSegment, Task
from app.api.deps import CurrentUser
from sqlalchemy.orm import selectinload


class WorklogService:
    @staticmethod
    def create_worklog(
        session: Session, worklog_in: WorkLogCreateIn, current_user: CurrentUser
    ):
        """
        Create new worklog.
        """
        # validating against the db the task_id provided by the user
        task = session.exec(
            select(Task.id).where(Task.id == worklog_in.task_id)
        ).first()
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"No task with the id {worklog_in.task_id} found.",
            )
        # add together all the worked time
        total_duration_minutes = sum(
            (ts.end_time - ts.start_time).total_seconds() / 60
            for ts in worklog_in.time_segments
        )

        worklog = WorkLog(
            user_id=current_user.id,
            task_id=worklog_in.task_id,
            total_duration_minutes=total_duration_minutes,
            time_segments=[
                TimeSegment(
                    user_id=current_user.id,
                    start_time=ts.start_time,
                    end_time=ts.end_time,
                    description=ts.description,
                    notes=ts.notes,
                )
                for ts in worklog_in.time_segments
            ],
        )

        session.add(worklog)
        session.commit()
        session.refresh(worklog)
        return worklog

    @staticmethod
    def get_all_wroklogs(session: Session) -> list[WorkLogOut]:
        """
        Get all the worklogs.
        - `remittanceStatus`: Filter by remittance status. Accepts `REMITTED` or `UNREMITTED`.
        """
        worklogs = session.exec(
            select(WorkLog).options(
                selectinload(WorkLog.time_segments))
        ).all()

        return [
            WorkLogOut(
                id=worklog.id,
                user_id=worklog.user_id,
                task_id=worklog.task_id,
                created_at=worklog.created_at,
                updated_at=worklog.updated_at,
                total_duration_minutes=worklog.total_duration_minutes,
                segment_count=len(worklog.time_segments),
                time_segments=[
                    TimeSegmentOut(
                        id=ts.id,
                        worklog_id=ts.worklog_id,
                        user_id=ts.user_id,
                        start_time=ts.start_time,
                        end_time=ts.end_time,
                        description=ts.description,
                        notes=ts.notes,
                        recorded_at=ts.recorded_at,
                    )
                    for ts in worklog.time_segments
                ],
            )
            for worklog in worklogs
        ]

    # a time segment can be questioned, removed, or adjusted.

    def get_all_user_time_segments(
        session: Session, current_user: CurrentUser
    ) -> list[TimeSegmentOut]:
        """gets all the user time segments"""
        time_segments = session.exec(
            select(TimeSegment).where(TimeSegment.user_id == current_user.id)
        ).all()
        return [
            TimeSegmentOut(
                id=ts.id,
                worklog_id=ts.worklog_id,
                user_id=ts.user_id,
                start_time=ts.start_time,
                end_time=ts.end_time,
                duration_minutes=ts.duration_minutes,
                duration=ts.duration,
                description=ts.description,
                notes=ts.notes,
                recorded_at=ts.recorded_at,
            )
            for ts in time_segments
        ]

    def delete_time_segment(
        session: Session, current_user: CurrentUser, time_segment_id: uuid.UUID
    ) -> DeleteTimeSegmentOut:
        # Fetch the time segment
        time_segment = session.get(TimeSegment, time_segment_id)

        if not time_segment:
            raise HTTPException(
                status_code=404,
                detail=f"No time segment with the id {time_segment_id} found.",
            )

        # Check that the current user owns this time segment
        if time_segment.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Not allowed to remove this time segment."
            )

        # Delete and commit
        session.delete(time_segment)
        session.commit()

        # Return confirmation
        return DeleteTimeSegmentOut(success="Time segment deleted successfully")

    def upadate_time_segment(
        session: Session,
        time_segment_id: uuid.UUID,
        current_user: CurrentUser,
        update_time_segment_data: UpdateTimeSegmentIn,
    ) -> UpdateTimeSegmentOut:
        # get segment from DB
        time_segment = session.get(TimeSegment, time_segment_id)
        if not time_segment:
            raise HTTPException(
                status_code=404,
                detail=f"No time segment with the id {time_segment_id} found.",
            )
        # check if the segment belongs to the logged in user
        if time_segment.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Not allowed to update this time segment."
            )

        update_data = update_time_segment_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(time_segment, field, value)

        session.commit()
        session.refresh(time_segment)
        return UpdateTimeSegmentOut(description="Your data has been updated.")
