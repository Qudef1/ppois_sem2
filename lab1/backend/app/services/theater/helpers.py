from __future__ import annotations

from typing import Any


def tickets_for_setting(all_tickets: list[Any], setting_name: str) -> list[Any]:
    return [ticket for ticket in all_tickets if ticket.setting and ticket.setting.name == setting_name]


def build_hall_sectors_view(hall: Any, hall_tickets: list[Any]) -> list[dict[str, Any]]:
    ticket_map = {(ticket.sector, ticket.row, ticket.seat): ticket for ticket in hall_tickets}
    sectors: list[dict[str, Any]] = []

    for sector_idx in range(hall.sectors):
        rows: list[dict[str, Any]] = []
        for row_idx in range(hall.rows_per_sector):
            seats: list[dict[str, Any]] = []
            for seat_idx in range(hall.seats_per_row):
                ticket = ticket_map.get((sector_idx, row_idx, seat_idx))
                if ticket is None:
                    seats.append(
                        {
                            "exists": False,
                            "ticket_id": None,
                            "seat_label": seat_idx + 1,
                            "row_label": row_idx + 1,
                            "sector_label": sector_idx + 1,
                            "price": 0.0,
                            "status": "none",
                        }
                    )
                    continue

                seats.append(
                    {
                        "exists": True,
                        "ticket_id": ticket.ticket_id,
                        "seat_label": seat_idx + 1,
                        "row_label": row_idx + 1,
                        "sector_label": sector_idx + 1,
                        "price": ticket.price,
                        "status": "sold" if ticket.is_sold else "available",
                    }
                )

            rows.append({"row_label": row_idx + 1, "seats": seats})
        sectors.append({"sector_label": sector_idx + 1, "rows": rows})

    return sectors
