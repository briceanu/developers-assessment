from fastapi import APIRouter, status
from app.schemas import TaskCreateIn, TaskOut
from .service import TaskService
from fastapi import APIRouter
from app.api.deps import SessionDep
from fastapi import status


router = APIRouter(prefix="/assessment_task", tags=["tasks"])


@router.post("/create-task",
             status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreateIn,
    session: SessionDep,
):
    """
    Create a new worklog.
    """
    return TaskService.create_task(session, task_in)


@router.get("/get-all-tasks",
            status_code=status.HTTP_200_OK,
            response_model=list[TaskOut])
def get_all_tasks(
    session: SessionDep,
) -> list[TaskOut]:
    """
    Get all tasks.
    """
    return TaskService.get_all_tasks(session)
