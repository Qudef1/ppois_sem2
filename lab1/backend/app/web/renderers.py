from __future__ import annotations

from fastapi import Request
from fastapi.responses import RedirectResponse

from app.container import container
from app.services.theater import TheaterService


def render_staff_dashboard(request: Request, service: TheaterService, message: str = "", is_error: bool = False):
    payload = service.dashboard()
    payload.update({"request": request, "message": message, "is_error": is_error})
    return container.templates.TemplateResponse(request=request, name="index.html", context=payload)


def render_user_catalog(request: Request, service: TheaterService, message: str = "", is_error: bool = False):
    payload = {
        "request": request,
        "name": service.theater.name,
        "settings_catalog": service.user_settings_catalog(),
        "message": message,
        "is_error": is_error,
    }
    return container.templates.TemplateResponse(request=request, name="user_catalog.html", context=payload)


def render_user_hall(
    request: Request,
    service: TheaterService,
    setting_idx: int,
    hall_id: str | None = None,
    message: str = "",
    is_error: bool = False,
):
    hall_view = service.user_setting_hall_view(setting_idx, hall_id)
    if hall_view is None:
        return RedirectResponse("/tickets", status_code=303)
    payload = {
        "request": request,
        "name": service.theater.name,
        "message": message,
        "is_error": is_error,
        "hall_view": hall_view,
    }
    return container.templates.TemplateResponse(request=request, name="user_hall.html", context=payload)
