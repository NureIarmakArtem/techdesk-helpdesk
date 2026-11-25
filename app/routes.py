from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, status

from app import database, services
from app.schemas import (
    CommentCreate,
    CommentResponse,
    StatusUpdate,
    TicketCreate,
    TicketPriority,
    TicketResponse,
    TicketStatus,
    TicketUpdate,
    UserResponse,
)

router = APIRouter()


def _db_path(request: Request) -> Path:
    return request.app.state.db_path


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/users", response_model=list[UserResponse])
def get_users(request: Request) -> list[dict]:
    return database.list_users(_db_path(request))


@router.post("/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(payload: TicketCreate, request: Request) -> dict:
    return services.create_ticket(_db_path(request), payload)


@router.get("/tickets", response_model=list[TicketResponse])
def list_tickets(
    request: Request,
    status: Optional[TicketStatus] = None,
    priority: Optional[TicketPriority] = None,
) -> list[dict]:
    return services.get_tickets(_db_path(request), status=status, priority=priority)


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, request: Request) -> dict:
    try:
        return services.get_ticket(_db_path(request), ticket_id)
    except services.NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/tickets/{ticket_id}", response_model=TicketResponse)
def patch_ticket(ticket_id: int, payload: TicketUpdate, request: Request) -> dict:
    try:
        return services.update_ticket(_db_path(request), ticket_id, payload)
    except services.NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except services.ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.patch("/tickets/{ticket_id}/status", response_model=TicketResponse)
def patch_ticket_status(ticket_id: int, payload: StatusUpdate, request: Request) -> dict:
    try:
        return services.change_ticket_status(_db_path(request), ticket_id, payload.status)
    except services.NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except services.ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post(
    "/tickets/{ticket_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(ticket_id: int, payload: CommentCreate, request: Request) -> dict:
    try:
        return services.add_comment(_db_path(request), ticket_id, payload)
    except services.NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/tickets/{ticket_id}/comments", response_model=list[CommentResponse])
def list_comments(ticket_id: int, request: Request) -> list[dict]:
    try:
        return services.get_comments(_db_path(request), ticket_id)
    except services.NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc