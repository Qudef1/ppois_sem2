from fastapi.templating import Jinja2Templates

from app.theater_service import TheaterService


class AppContainer:
    def __init__(self) -> None:
        self._theater_service = TheaterService()
        self._templates = Jinja2Templates(directory="app/templates")

    @property
    def theater_service(self) -> TheaterService:
        return self._theater_service

    @property
    def templates(self) -> Jinja2Templates:
        return self._templates


container = AppContainer()
