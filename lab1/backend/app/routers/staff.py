from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request

from app.dependencies import get_theater_service
from app.services.theater import TheaterService
from app.web.renderers import render_staff_dashboard

router = APIRouter(tags=["staff"])


@router.get("/")
async def index(request: Request, service: TheaterService = Depends(get_theater_service)):
    return render_staff_dashboard(request, service)


@router.post("/theater/rename")
async def rename_theater(
    request: Request,
    new_name: str = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.rename_theater(new_name)
    return render_staff_dashboard(request, service, result.message, not result.ok)


@router.post("/halls")
async def add_hall(
    request: Request,
    name: str = Form(...),
    sectors: int = Form(...),
    rows_per_sector: int = Form(...),
    seats_per_row: int = Form(...),
    hall_id: str = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.add_hall(name, sectors, rows_per_sector, seats_per_row, hall_id)
    return render_staff_dashboard(request, service, result.message, not result.ok)


@router.post("/staff/actors")
async def add_actor(
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    salary: float = Form(...),
    role: str = Form(""),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.add_actor(name, age, salary, role)
    return render_staff_dashboard(request, service, result.message, not result.ok)


@router.post("/staff/directors")
async def add_director(
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    salary: float = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.add_director(name, age, salary)
    return render_staff_dashboard(request, service, result.message, not result.ok)


@router.post("/settings")
async def add_setting(
    request: Request,
    name: str = Form(...),
    durability: float = Form(...),
    date: str = Form(...),
    director_name: str = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.add_setting(name, durability, date, director_name)
    return render_staff_dashboard(request, service, result.message, not result.ok)


@router.post("/costumes")
async def create_costume(
    request: Request,
    name: str = Form(...),
    size: str = Form(...),
    color: str = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.create_costume(name, size, color)
    return render_staff_dashboard(request, service, result.message, not result.ok)


@router.post("/settings/bind")
async def bind_setting_to_hall(
    request: Request,
    setting_name: str = Form(...),
    hall_id: str = Form(...),
    base_price: float = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.bind_setting_to_hall(setting_name, hall_id, base_price)
    return render_staff_dashboard(request, service, result.message, not result.ok)


@router.post("/settings/cast")
async def add_actor_to_setting(
    request: Request,
    actor_name: str = Form(...),
    setting_name: str = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.add_actor_to_setting(actor_name, setting_name)
    return render_staff_dashboard(request, service, result.message, not result.ok)


@router.post("/costumes/assign")
async def assign_costume_to_actor(
    request: Request,
    costume_name: str = Form(...),
    actor_name: str = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.assign_costume_to_actor(costume_name, actor_name)
    return render_staff_dashboard(request, service, result.message, not result.ok)


@router.post("/repetitions")
async def add_repetition(
    request: Request,
    setting_name: str = Form(...),
    date: str = Form(...),
    durability: float = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.add_repetition(setting_name, date, durability)
    return render_staff_dashboard(request, service, result.message, not result.ok)


@router.post("/repetitions/mark")
async def mark_actors(
    request: Request,
    repetition_name: str = Form(...),
    actor_names: list[str] = Form([]),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.mark_actors_at_repetition(repetition_name, actor_names)
    return render_staff_dashboard(request, service, result.message, not result.ok)


@router.post("/tickets/sell")
async def sell_ticket(
    request: Request,
    ticket_id: str = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.sell_ticket(ticket_id)
    return render_staff_dashboard(request, service, result.message, not result.ok)


@router.post("/state/save")
async def save_state(
    request: Request,
    path: str = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.save_state(path)
    return render_staff_dashboard(request, service, result.message, not result.ok)


@router.post("/state/load")
async def load_state(
    request: Request,
    path: str = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.load_state(path)
    return render_staff_dashboard(request, service, result.message, not result.ok)
