from app.container import container
from app.services.theater import TheaterService


def get_theater_service() -> TheaterService:
    return container.theater_service
