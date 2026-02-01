from datetime import datetime
from fastapi import APIRouter, Body, status
from app.schemas import RemittanceSchemaOut, TaskCreateIn, TaskOut
from .service import RemittanceService
from fastapi import APIRouter
from app.api.deps import CurrentUser, SessionDep
from fastapi import status
from typing import Annotated

router = APIRouter(prefix="/assessment_task", tags=["remittance"])


@router.post("/generate-remittances-for-all-users",
             status_code=status.HTTP_201_CREATED,
             response_model=RemittanceSchemaOut)
def create_remittance(
    amount_per_hour: Annotated[float, Body()],
    start_date: Annotated[datetime, Body()],
    end_date: Annotated[datetime, Body()],
    session: SessionDep,

) -> RemittanceSchemaOut:
    """
    Create a remittance.
    """
    return RemittanceService.create_remittances(session, amount_per_hour, start_date, end_date)


@router.get("/get-all-remittances",
            status_code=status.HTTP_200_OK)
def get_all_remittances(

    session: SessionDep,

):
    """
    get all remittances.
    """
    return RemittanceService.get_all_remittences(session)
