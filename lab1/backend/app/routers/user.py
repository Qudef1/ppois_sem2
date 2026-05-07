from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Query, Request

from app.dependencies import get_theater_service
from app.services.theater import TheaterService
from app.web.renderers import render_user_catalog, render_user_hall

router = APIRouter(tags=["user"])


@router.get("/tickets")
async def user_tickets_catalog(request: Request, service: TheaterService = Depends(get_theater_service)):
    return render_user_catalog(request, service)


@router.get("/tickets/setting/{setting_idx}")
async def user_setting_hall(
    request: Request,
    setting_idx: int,
    hall_id: str | None = Query(default=None),
    service: TheaterService = Depends(get_theater_service),
):
    return render_user_hall(request, service, setting_idx, hall_id)


@router.post("/tickets/purchase")
async def user_purchase_ticket(
    request: Request,
    setting_idx: int = Form(...),
    hall_id: str = Form(...),
    ticket_id: str = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.sell_ticket(ticket_id)
    return render_user_hall(request, service, setting_idx, hall_id, result.message, not result.ok)
