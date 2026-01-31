from datetime import date
from typing import List
from app.schemas import TaskCreateIn, TaskOut

from fastapi import HTTPException
from sqlalchemy import select
from sqlmodel import Session, select
from app.models import Task


class TaskService:
    @staticmethod
    def create_task(session: Session, task_in: TaskCreateIn):
        """
        Create new task.
        """
        task = Task.model_validate(task_in)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def get_all_tasks(session: Session) -> list[TaskOut]:
        """
        Get all the tasks.
        """
        tasks = session.exec(select(Task)).all()
        return [
            TaskOut(
                id=task.id,
                title=task.title,
                description=task.description,
                created_at=task.created_at,
            )
            for task in tasks
        ]
