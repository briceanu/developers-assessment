from uuid import UUID
from enum import Enum
from typing import Optional
from datetime import date, timedelta
from pydantic import BaseModel
from datetime import date, datetime, timezone
from typing import Annotated, List, Optional
import uuid
# from app.schemas import RemittanceStatus
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel, Enum
from sqlmodel import SQLModel, Field, Relationship

# Shared properties


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = True
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(
        default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(
        back_populates="owner", cascade_delete=True)
    # add relationships
    worklogs: list["WorkLog"] = Relationship(
        back_populates="user",  # matches WorkLog.user
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    remittances: list["Remittance"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

# Properties to return via API, id is always required


class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(
        default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


# # implementation

# -----------------------------
# Task Model
# -----------------------------
class Task(SQLModel, table=True):
    """A task that workers can log time against."""
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(index=True)
    description: Optional[str] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    worklogs: List["WorkLog"] = Relationship(back_populates="task")

# -----------------------------
# WorkLog Model
# -----------------------------


class WorkLog(SQLModel, table=True):
    """Container for all work done against a task by a user."""
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    task_id: UUID = Field(foreign_key="task.id", index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    total_duration_minutes: float = Field(nullable=False)

    # Relationships
    user: "User" = Relationship(back_populates="worklogs")
    task: Task = Relationship(back_populates="worklogs")
    time_segments: List["TimeSegment"] = Relationship(
        back_populates="worklog", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


# -----------------------------
# TimeSegment Model
# -----------------------------


class TimeSegment(SQLModel, table=True):
    """A single time recording session."""
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    worklog_id: UUID = Field(foreign_key="worklog.id", index=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    notes: Optional[str] = None
    recorded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    worklog: WorkLog = Relationship(back_populates="time_segments")


# -----------------------------
# Remittance Model
# -----------------------------


class Remittance(SQLModel, table=True):
    """Payment batch for a user covering a period."""
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    total_amount: float
    status: str = Field(default="PENDING")
    period_start: datetime
    period_end: datetime
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    paid_at: Optional[datetime] = None

    # Relationships
    user: "User" = Relationship(back_populates="remittances")
