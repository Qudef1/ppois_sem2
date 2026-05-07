from fastapi import Depends, FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles

from app.container import container
from app.dependencies import get_theater_service
from app.theater_service import TheaterService

app = FastAPI(title="Theater Web UI", version="1.0.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


def _render(request: Request, service: TheaterService, message: str = "", is_error: bool = False):
    payload = service.dashboard()
    payload.update({"request": request, "message": message, "is_error": is_error})
    return container.templates.TemplateResponse(request=request, name="index.html", context=payload)


@app.get("/")
async def index(request: Request, service: TheaterService = Depends(get_theater_service)):
    return _render(request, service)


@app.post("/theater/rename")
async def rename_theater(
    request: Request,
    new_name: str = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.rename_theater(new_name)
    return _render(request, service, result.message, not result.ok)


@app.post("/halls")
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
    return _render(request, service, result.message, not result.ok)


@app.post("/staff/actors")
async def add_actor(
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    salary: float = Form(...),
    role: str = Form(""),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.add_actor(name, age, salary, role)
    return _render(request, service, result.message, not result.ok)


@app.post("/staff/directors")
async def add_director(
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    salary: float = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.add_director(name, age, salary)
    return _render(request, service, result.message, not result.ok)


@app.post("/settings")
async def add_setting(
    request: Request,
    name: str = Form(...),
    durability: float = Form(...),
    date: str = Form(...),
    director_name: str = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.add_setting(name, durability, date, director_name)
    return _render(request, service, result.message, not result.ok)


@app.post("/costumes")
async def create_costume(
    request: Request,
    name: str = Form(...),
    size: str = Form(...),
    color: str = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.create_costume(name, size, color)
    return _render(request, service, result.message, not result.ok)


@app.post("/settings/bind")
async def bind_setting_to_hall(
    request: Request,
    setting_name: str = Form(...),
    hall_id: str = Form(...),
    base_price: float = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.bind_setting_to_hall(setting_name, hall_id, base_price)
    return _render(request, service, result.message, not result.ok)


@app.post("/settings/cast")
async def add_actor_to_setting(
    request: Request,
    actor_name: str = Form(...),
    setting_name: str = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.add_actor_to_setting(actor_name, setting_name)
    return _render(request, service, result.message, not result.ok)


@app.post("/costumes/assign")
async def assign_costume_to_actor(
    request: Request,
    costume_name: str = Form(...),
    actor_name: str = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.assign_costume_to_actor(costume_name, actor_name)
    return _render(request, service, result.message, not result.ok)


@app.post("/repetitions")
async def add_repetition(
    request: Request,
    setting_name: str = Form(...),
    date: str = Form(...),
    durability: float = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.add_repetition(setting_name, date, durability)
    return _render(request, service, result.message, not result.ok)


@app.post("/repetitions/mark")
async def mark_actors(
    request: Request,
    repetition_name: str = Form(...),
    actor_names: list[str] = Form([]),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.mark_actors_at_repetition(repetition_name, actor_names)
    return _render(request, service, result.message, not result.ok)


@app.post("/tickets/sell")
async def sell_ticket(
    request: Request,
    ticket_id: str = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.sell_ticket(ticket_id)
    return _render(request, service, result.message, not result.ok)


@app.post("/state/save")
async def save_state(
    request: Request,
    path: str = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.save_state(path)
    return _render(request, service, result.message, not result.ok)


@app.post("/state/load")
async def load_state(
    request: Request,
    path: str = Form(...),
    service: TheaterService = Depends(get_theater_service),
):
    result = service.load_state(path)
    return _render(request, service, result.message, not result.ok)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/info")
async def theater_info(service: TheaterService = Depends(get_theater_service)):
    return service.info_all()


@app.get("/info/summary")
async def theater_summary(service: TheaterService = Depends(get_theater_service)):
    return service.info_summary()


@app.get("/info/staff")
async def theater_staff(service: TheaterService = Depends(get_theater_service)):
    return service.info_staff()


@app.get("/info/halls")
async def theater_halls(service: TheaterService = Depends(get_theater_service)):
    return service.info_halls()


@app.get("/info/performances")
async def theater_performances(service: TheaterService = Depends(get_theater_service)):
    return service.info_settings()


@app.get("/info/tickets")
async def theater_tickets(service: TheaterService = Depends(get_theater_service)):
    return service.info_tickets()


@app.get("/info/resources")
async def theater_resources(service: TheaterService = Depends(get_theater_service)):
    return service.info_resources()
