from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from fastapi import HTTPException

from app import database
from app.schemas import (
    CommentCreate,
    TicketCreate,
    TicketPriority,
    TicketStatus,
    TicketUpdate,
)


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    TicketStatus.OPEN.value: {
        TicketStatus.OPEN.value,
        TicketStatus.IN_PROGRESS.value,
        TicketStatus.CLOSED.value,
    },
    TicketStatus.IN_PROGRESS.value: {
        TicketStatus.IN_PROGRESS.value,
        TicketStatus.CLOSED.value,
    },
    TicketStatus.CLOSED.value: {
        TicketStatus.CLOSED.value,
    },
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def matches_status(ticket: dict[str, Any], value: Optional[str]) -> bool:
    if value is None:
        return True
    return ticket["status"] == value


def matches_priority(ticket: dict[str, Any], value: Optional[str]) -> bool:
    if value is None:
        return True
    return ticket["priority"] == value


def create_ticket(db_path: Path, payload: TicketCreate) -> dict[str, Any]:
    return database.insert_ticket(
        db_path=db_path,
        title=payload.title,
        description=payload.description,
        priority=payload.priority.value,
        assignee_id=payload.assignee_id,
        created_at=utc_now_iso(),
    )


def get_tickets(
    db_path: Path,
    status: Optional[TicketStatus] = None,
    priority: Optional[TicketPriority] = None,
) -> list[dict[str, Any]]:
    tickets = database.fetch_all_tickets(db_path)
    status_val = status.value if status is not None else None
    priority_val = priority.value if priority is not None else None
    return [
        t
        for t in tickets
        if matches_status(t, status_val) and matches_priority(t, priority_val)
    ]


def get_ticket(db_path: Path, ticket_id: int) -> dict[str, Any]:
    ticket = database.fetch_ticket_by_id(db_path, ticket_id)
    if ticket is None:
        raise NotFoundError(f"Ticket {ticket_id} not found")
    return ticket


def update_ticket(db_path: Path, ticket_id: int, payload: TicketUpdate) -> dict[str, Any]:
    ticket = get_ticket(db_path, ticket_id)
    if ticket["status"] == TicketStatus.CLOSED.value:
        raise ConflictError("Cannot edit a CLOSED ticket")

    updates: dict[str, Any] = {}
    for field_name in payload.model_fields_set:
        if field_name == "assignee_id":
            continue
        val = getattr(payload, field_name)
        updates[field_name] = val.value if isinstance(val, TicketPriority) else val

    if updates:
        ticket = database.update_ticket_fields(db_path, ticket_id, updates)

    if "assignee_id" in payload.model_fields_set:
        if payload.assignee_id is not None and payload.assignee_id not in {1, 2}:
            raise HTTPException(status_code=422, detail="Unknown assignee_id")
        ticket = database.update_ticket_fields(
            db_path, ticket_id, {"assignee_id": payload.assignee_id}
        )
    return ticket


def change_ticket_status(
    db_path: Path, ticket_id: int, new_status: TicketStatus
) -> dict[str, Any]:
    ticket = get_ticket(db_path, ticket_id)
    current = ticket["status"]
    target = new_status.value

    if target not in ALLOWED_TRANSITIONS[current]:
        raise ConflictError(f"Invalid status transition from {current} to {target}")

    if current == target:
        return ticket

    return database.update_ticket_fields(db_path, ticket_id, {"status": target})


def add_comment(db_path: Path, ticket_id: int, payload: CommentCreate) -> dict[str, Any]:
    get_ticket(db_path, ticket_id)
    return database.insert_comment(
        db_path=db_path,
        ticket_id=ticket_id,
        author_id=payload.author_id,
        body=payload.body,
        created_at=utc_now_iso(),
    )


def get_comments(db_path: Path, ticket_id: int) -> list[dict[str, Any]]:
    get_ticket(db_path, ticket_id)
    return database.fetch_comments_by_ticket(db_path, ticket_id)