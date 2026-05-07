from __future__ import annotations

from typing import Any

from app.services.theater.helpers import build_hall_sectors_view, tickets_for_setting


class TheaterQueriesMixin:
    def dashboard(self) -> dict[str, Any]:
        tickets = self._theater.ticket_manager.tickets
        sold = [ticket for ticket in tickets if ticket.is_sold]
        return {
            "theater": self._theater,
            "name": self._theater.name,
            "actors": self.actors,
            "directors": self.directors,
            "settings": self.settings,
            "repetitions": self.repetitions,
            "halls": self.halls,
            "costumes": self._theater.resource_manager.costumes,
            "tickets": tickets,
            "sold_tickets": sold,
            "available_tickets": [ticket for ticket in tickets if not ticket.is_sold],
        }

    def user_settings_catalog(self) -> list[dict[str, Any]]:
        catalog: list[dict[str, Any]] = []
        all_tickets = self._theater.ticket_manager.tickets
        for idx, setting in enumerate(self.settings):
            setting_tickets = tickets_for_setting(all_tickets, setting.name)
            if not setting_tickets:
                continue
            available = [ticket for ticket in setting_tickets if not ticket.is_sold]
            hall_ids = sorted({ticket.hall_id for ticket in setting_tickets})
            min_price = min(ticket.price for ticket in available) if available else 0.0
            catalog.append(
                {
                    "setting_idx": idx,
                    "name": setting.name,
                    "date": setting.date.isoformat() if hasattr(setting.date, "isoformat") else str(setting.date),
                    "director": setting.director.name if setting.director else "Н/Д",
                    "duration_hours": setting.durability,
                    "total_tickets": len(setting_tickets),
                    "available_tickets": len(available),
                    "halls": hall_ids,
                    "min_price": min_price,
                }
            )
        return catalog

    def user_setting_hall_view(self, setting_idx: int, hall_id: str | None = None) -> dict[str, Any] | None:
        if setting_idx < 0 or setting_idx >= len(self.settings):
            return None

        setting = self.settings[setting_idx]
        setting_tickets = tickets_for_setting(self._theater.ticket_manager.tickets, setting.name)
        if not setting_tickets:
            return None

        hall_ids = sorted({ticket.hall_id for ticket in setting_tickets})
        selected_hall_id = hall_id if hall_id in hall_ids else hall_ids[0]
        hall = next((item for item in self.halls if item.hall_id == selected_hall_id), None)
        if hall is None:
            return None

        hall_tickets = [ticket for ticket in setting_tickets if ticket.hall_id == selected_hall_id]
        sold_count = sum(1 for ticket in hall_tickets if ticket.is_sold)
        return {
            "setting_idx": setting_idx,
            "setting_name": setting.name,
            "date": setting.date.isoformat() if hasattr(setting.date, "isoformat") else str(setting.date),
            "director": setting.director.name if setting.director else "Н/Д",
            "hall_id": selected_hall_id,
            "halls": hall_ids,
            "capacity": len(hall_tickets),
            "sold_count": sold_count,
            "available_count": len(hall_tickets) - sold_count,
            "sectors": build_hall_sectors_view(hall, hall_tickets),
        }

    def info_summary(self) -> dict[str, Any]:
        halls = self.halls
        tickets = self._theater.ticket_manager.tickets
        sold = [ticket for ticket in tickets if ticket.is_sold]
        return {
            "theater_name": self._theater.name,
            "staff_count": len(self._theater.staff_manager.staff),
            "halls_count": len(halls),
            "total_capacity": sum(hall.capacity for hall in halls),
            "settings_count": len(self.settings),
            "repetitions_count": len(self.repetitions),
            "tickets_count": len(tickets),
            "sold_tickets_count": len(sold),
            "available_tickets_count": len(tickets) - len(sold),
            "stages_count": len(self._theater.resource_manager.stages),
            "costume_rooms_count": len(self._theater.resource_manager.costume_rooms),
            "costumes_count": len(self._theater.resource_manager.costumes),
        }

    def info_staff(self) -> dict[str, Any]:
        return {
            "total": len(self._theater.staff_manager.staff),
            "actors": [
                {
                    "name": actor.name,
                    "age": actor.get_age(),
                    "salary": actor.get_salary(),
                    "role": actor.role,
                    "costumes_count": len(actor.get_costumes()),
                }
                for actor in self.actors
            ],
            "directors": [
                {
                    "name": director.name,
                    "age": director.get_age(),
                    "salary": director.get_salary(),
                    "directed_settings_count": len(director.directed_settings),
                }
                for director in self.directors
            ],
        }

    def info_halls(self) -> dict[str, Any]:
        halls_data: list[dict[str, Any]] = []
        for hall in self.halls:
            occupied = sum(1 for sector in hall.seats for row in sector for seat in row if seat.is_occupied)
            halls_data.append(
                {
                    "name": hall.name,
                    "hall_id": hall.hall_id,
                    "sectors": hall.sectors,
                    "rows_per_sector": hall.rows_per_sector,
                    "seats_per_row": hall.seats_per_row,
                    "capacity": hall.capacity,
                    "occupied": occupied,
                    "available": hall.capacity - occupied,
                }
            )
        return {"halls": halls_data}

    def info_settings(self) -> dict[str, Any]:
        settings_data = [
            {
                "name": setting.name,
                "duration_hours": setting.durability,
                "date": setting.date.isoformat() if hasattr(setting.date, "isoformat") else str(setting.date),
                "director": setting.director.name if setting.director else None,
                "cast_count": len(setting.cast),
                "hall": setting.hall.name if setting.hall else None,
            }
            for setting in self.settings
        ]
        repetitions_data = [
            {
                "name": repetition.name,
                "duration_hours": repetition.durability,
                "date": repetition.date.isoformat() if hasattr(repetition.date, "isoformat") else str(repetition.date),
                "setting": repetition.setting.name if repetition.setting else None,
                "attendance_count": len(repetition.attendance_list),
            }
            for repetition in self.repetitions
        ]
        return {"settings": settings_data, "repetitions": repetitions_data}

    def info_tickets(self) -> dict[str, Any]:
        tickets = self._theater.ticket_manager.tickets
        sold = [ticket for ticket in tickets if ticket.is_sold]
        return {
            "total": len(tickets),
            "sold": len(sold),
            "available": len(tickets) - len(sold),
            "revenue": sum(ticket.price for ticket in sold),
            "tickets": [
                {
                    "ticket_id": ticket.ticket_id,
                    "setting": ticket.setting.name if ticket.setting else None,
                    "hall_id": ticket.hall_id,
                    "sector": ticket.sector,
                    "row": ticket.row,
                    "seat": ticket.seat,
                    "price": ticket.price,
                    "is_sold": ticket.is_sold,
                }
                for ticket in tickets
            ],
        }

    def info_resources(self) -> dict[str, Any]:
        rm = self._theater.resource_manager
        return {
            "stages": [
                {
                    "name": stage.name,
                    "capacity": stage.capacity,
                    "equipment": stage.equipment,
                    "is_available": stage.is_available,
                }
                for stage in rm.stages
            ],
            "costume_rooms": [{"name": room.name, "costume_ids": room.costume_ids} for room in rm.costume_rooms],
            "costumes": [{"name": costume.name, "size": costume.size, "color": costume.color} for costume in rm.costumes],
        }

    def info_all(self) -> dict[str, Any]:
        return {
            "summary": self.info_summary(),
            "staff": self.info_staff(),
            "halls": self.info_halls(),
            "performances": self.info_settings(),
            "tickets": self.info_tickets(),
            "resources": self.info_resources(),
        }
