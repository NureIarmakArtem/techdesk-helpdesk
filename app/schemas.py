from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

ALLOWED_USER_IDS = {1, 2}


class TicketStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"


class TicketPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class UserResponse(BaseModel):
    id: int
    name: str


class TicketCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: str = ""
    priority: TicketPriority = TicketPriority.medium
    assignee_id: Optional[int] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        trimmed = value.strip()
        if not (3 <= len(trimmed) <= 120):
            raise ValueError("title must contain between 3 and 120 characters after trimming")
        return trimmed

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        if len(value) > 2000:
            raise ValueError("description must contain at most 2000 characters")
        return value

    @field_validator("assignee_id")
    @classmethod
    def validate_assignee(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and value not in ALLOWED_USER_IDS:
            raise ValueError(f"Unknown assignee_id: {value}. Allowed values: 1, 2.")
        return value


class TicketUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TicketPriority] = None
    assignee_id: Optional[int] = None

    @model_validator(mode="after")
    def validate_patch(self) -> "TicketUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided for update")

        for field_name in ("title", "description", "priority"):
            if field_name in self.model_fields_set and getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")

        if "title" in self.model_fields_set and self.title is not None:
            trimmed = self.title.strip()
            if not (3 <= len(trimmed) <= 120):
                raise ValueError("title must contain between 3 and 120 characters after trimming")
            self.title = trimmed

        if "description" in self.model_fields_set and self.description is not None:
            if len(self.description) > 2000:
                raise ValueError("description must contain at most 2000 characters")

        #if "assignee_id" in self.model_fields_set and self.assignee_id is not None:
        #    if self.assignee_id not in ALLOWED_USER_IDS:
        #        raise ValueError(f"Unknown assignee_id: {self.assignee_id}. Allowed values: 1, 2.")

        return self


class StatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: TicketStatus


class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    assignee_id: Optional[int]
    created_at: str


class CommentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    author_id: int
    body: str

    @field_validator("author_id")
    @classmethod
    def validate_author(cls, value: int) -> int:
        if value not in ALLOWED_USER_IDS:
            raise ValueError(f"Unknown author_id: {value}. Allowed values: 1, 2.")
        return value

    @field_validator("body")
    @classmethod
    def validate_body(cls, value: str) -> str:
        trimmed = value.strip()
        if not (1 <= len(trimmed) <= 1000):
            raise ValueError("body must contain between 1 and 1000 characters after trimming")
        return trimmed


class CommentResponse(BaseModel):
    id: int
    ticket_id: int
    author_id: int
    body: str
    created_at: str