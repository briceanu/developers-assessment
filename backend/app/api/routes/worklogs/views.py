from typing import List
import uuid
from fastapi import APIRouter, status
from app.schemas import RemittanceStatusSchemaIn, TimeSegmentOut, UpdateTimeSegmentIn, UpdateTimeSegmentOut, WorkLogCreateIn, WorkLogOut
from .service import WorklogService
from fastapi import APIRouter
from app.api.deps import CurrentUser, SessionDep
from fastapi import status


router = APIRouter(prefix="/assessment_task", tags=["worklogs"])


@router.post(
    "/create-wroklog",
    status_code=status.HTTP_201_CREATED,
)
def create_wroklog_for_user(
    worklog_in: WorkLogCreateIn, session: SessionDep, current_user: CurrentUser
):
    """
    Create a new worklog.
    """
    return WorklogService.create_worklog(
        session=session, worklog_in=worklog_in, current_user=current_user
    )


@router.get(
    "/list-all-worklogs", status_code=status.HTTP_200_OK, response_model=List[WorkLogOut]
)
def get_all_worklogs(
    session: SessionDep,
    remittance_status: RemittanceStatusSchemaIn
) -> list[WorkLogOut]:
    """
    Get all worklogs.
    """
    return WorklogService.get_all_wroklogs(session, remittance_status)


@router.get(
    "/get-all-user-time-segments",
    status_code=status.HTTP_200_OK,
    response_model=List[TimeSegmentOut],
)
def get_all_user_time_segments(
    session: SessionDep, current_user: CurrentUser
) -> list[TimeSegmentOut]:
    """
    Get all user's time segments.
    """
    return WorklogService.get_all_user_time_segments(session, current_user)


@router.delete("/remove-time-segment", status_code=status.HTTP_200_OK)
def delete_time_segment(
    time_segment_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
):
    """
    Delete time segment.
    """
    return WorklogService.delete_time_segment(
        session=session, time_segment_id=time_segment_id, current_user=current_user
    )


@router.patch("/update-time-segment", status_code=status.HTTP_200_OK,
              response_model=UpdateTimeSegmentOut)
def update_time_segment(
    time_segment_id: uuid.UUID, session: SessionDep, current_user: CurrentUser,
    update_time_segment_data: UpdateTimeSegmentIn,
) -> UpdateTimeSegmentOut:
    """
    Update time segment.
    """
    return WorklogService.upadate_time_segment(
        session=session, time_segment_id=time_segment_id, current_user=current_user,
        update_time_segment_data=update_time_segment_data
    )
