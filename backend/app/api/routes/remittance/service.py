from datetime import date, datetime
from typing import List
from app.api.deps import CurrentUser
from app.schemas import RemittanceSchemaOut, TaskCreateIn, TaskOut, TimeSegmentOut

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlmodel import Session, select
from app.models import Remittance, Task, TimeSegment, User, WorkLog
from sqlalchemy import and_


class RemittanceService:
    @staticmethod
    def create_remittances(
        session: Session,
        amount_per_hour: float,
        start_date: datetime,
        end_date: datetime,
    ) -> RemittanceSchemaOut:
        """
        Create remitance for users.
        """
        remittances = []

        # Fetch all user IDs
        user_ids = session.exec(select(WorkLog.user_id)).all()

        for user_id in user_ids:
            # Sum duration in minutes in SQL
            total_minutes_worked = session.exec(
                select(func.coalesce(func.sum(WorkLog.total_duration_minutes), 0))
                .where(
                    and_(
                        TimeSegment.user_id == user_id,
                        TimeSegment.start_time >= start_date,
                        TimeSegment.end_time <= end_date,
                    )
                )
                .join(TimeSegment, TimeSegment.user_id == WorkLog.user_id)
            ).one()

            # Calculate payment
            total_payment = total_minutes_worked / 60 * amount_per_hour

            # Create remittance
            remittance = Remittance(
                user_id=user_id,
                total_amount=total_payment,
                status="PENDING",
                period_start=start_date,
                period_end=end_date,
            )
            remittances.append(remittance)
            session.add_all(remittances)
            session.commit()

        return RemittanceSchemaOut(detail='Data successfully saved.')

    @staticmethod
    def get_all_remittences(
        session: Session
    ):
        """gets all remittances"""
        remittances = session.exec(select(Remittance)).all()
        return remittances
