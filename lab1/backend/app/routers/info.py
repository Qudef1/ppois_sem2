from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import get_theater_service
from app.services.theater import TheaterService

router = APIRouter(tags=["info"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/info")
async def theater_info(service: TheaterService = Depends(get_theater_service)):
    return service.info_all()


@router.get("/info/summary")
async def theater_summary(service: TheaterService = Depends(get_theater_service)):
    return service.info_summary()


@router.get("/info/staff")
async def theater_staff(service: TheaterService = Depends(get_theater_service)):
    return service.info_staff()


@router.get("/info/halls")
async def theater_halls(service: TheaterService = Depends(get_theater_service)):
    return service.info_halls()


@router.get("/info/performances")
async def theater_performances(service: TheaterService = Depends(get_theater_service)):
    return service.info_settings()


@router.get("/info/tickets")
async def theater_tickets(service: TheaterService = Depends(get_theater_service)):
    return service.info_tickets()


@router.get("/info/resources")
async def theater_resources(service: TheaterService = Depends(get_theater_service)):
    return service.info_resources()
