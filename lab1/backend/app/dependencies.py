from app.container import container
from app.theater_service import TheaterService


def get_theater_service() -> TheaterService:
    return container.theater_service
