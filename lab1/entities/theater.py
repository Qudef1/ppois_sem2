import staff
from typing import List

class TheaterCapacityError(Exception):
    pass

class Action:
    def __init__(self,durability:float,date:str):
        self.durability = durability
        self.date = date

class Setting(Action):
    def __init__(self,durability:float,name:str,date:str):
        super().__init__(durability,date)
        self.name = name
        self.cast: List[staff.Staff] = []


class Repetition(Action):
    def __init__(self,durability:float,setting:Setting,importance:str,date:str = ""):
        super().__init__(durability,date)
        self.importance = importance
        self.setting = setting
        self.__attendance_list: List[staff.Staff] = []
    
    def check_list(self,staff_member:staff.Staff):
        self.__attendance_list.append(staff_member)

class Seat:
    def __init__(self, seat_number: int):
        self.seat_number = seat_number
        self.is_occupied = False

class Ticket:
    def __init__(self, ticket_id: str, price: float, setting: Setting, sector: int, row: int, seat: int, hall: 'AuditoryHall'):
        self.ticket_id = ticket_id
        self.price = price
        self.setting = setting
        self.sector = sector
        self.row = row
        self.seat = seat
        self.hall = hall
        self.is_sold = False
    
    def sell_ticket(self) -> bool:
        if not self.is_sold and self.hall.is_seat_available(self.sector, self.row, self.seat):
            if self.hall.occupy_seat(self.sector, self.row, self.seat):
                self.is_sold = True
                return True
        return False
    
    def get_seat_location(self) -> str:
        return f"Sector {self.sector}, Row {self.row}, Seat {self.seat}"

class Costume:
    def __init__(self, name: str, size: str, color: str):
        self.name = name
        self.size = size
        self.color = color
    
    def make_costume(self,actor:staff.Actor):
        actor.role = self.name

class CostumeRoom:
    def __init__(self, name: str, costumes: List[Costume] = None):
        self.name = name
        self.costumes = costumes if costumes else []
    
    def val_costume(self, costume: Costume):
        self.costumes.append(costume)
    
    def get_costume(self, name: str) -> Costume:
        for costume in self.costumes:
            if costume.name == name:
                return costume
        return None

class Stage:
    def __init__(self, name: str, capacity: int, equipment: List[str] = None):
        self.name = name
        self.capacity = capacity
        self.equipment = equipment if equipment else []
        self.is_available = True
    
    def setup_stage(self, setting: Setting):
        self.is_available = False
    
    def free_stage(self):
        self.is_available = True

class AuditoryHall:
    def __init__(self, name: str, sectors: int, rows_per_sector: int, seats_per_row: int):
        self.name = name
        self.sectors = sectors
        self.rows_per_sector = rows_per_sector
        self.seats_per_row = seats_per_row
        self.seats = [[
                [Seat(s) for s in range(seats_per_row)]
                for r in range(rows_per_sector)]
            for sec in range(sectors)]
        self.audience_count = 0
        self.capacity = sectors * rows_per_sector * seats_per_row
    
    def is_seat_available(self, sector: int, row: int, seat: int) -> bool:
        if 0 <= sector < self.sectors and 0 <= row < self.rows_per_sector and 0 <= seat < self.seats_per_row:
            return not self.seats[sector][row][seat].is_occupied
        return False
    
    def occupy_seat(self, sector: int, row: int, seat: int) -> bool:
        if self.is_seat_available(sector, row, seat):
            self.seats[sector][row][seat].is_occupied = True
            self.audience_count += 1
            return True
        return False
    
    def free_seat(self, sector: int, row: int, seat: int):
        if 0 <= sector < self.sectors and 0 <= row < self.rows_per_sector and 0 <= seat < self.seats_per_row:
            if self.seats[sector][row][seat].is_occupied:
                self.seats[sector][row][seat].is_occupied = False
                self.audience_count -= 1
    
    def empty_hall(self):
        for sector in self.seats:
            for row in sector:
                for seat in row:
                    seat.is_occupied = False
        self.audience_count = 0
    
    def get_available_seats_count(self) -> int:
        return self.capacity - self.audience_count

class StaffManager:
    def __init__(self):
        self.staff: List[staff.Staff] = []
    
    def add_staff(self, staff_member: staff.Staff):
        self.staff.append(staff_member)
    
    def get_staff(self) -> List[staff.Staff]:
        return self.staff

class PerformanceManager:
    def __init__(self):
        self.set_list: List[Setting] = []
        self.__repetition_list: List[Repetition] = []
    
    def add_setting(self, setting: Setting):
        self.set_list.append(setting)
    
    def add_repetition(self, repetition: Repetition):
        self.__repetition_list.append(repetition)
    
    def get_settings(self) -> List[Setting]:
        return self.set_list
    
    def get_repetitions(self) -> List[Repetition]:
        return self.__repetition_list

class TicketManager:
    def __init__(self):
        self.__tickets: List[Ticket] = []
    
    def create_ticket(self, ticket_id: str, price: float, setting: Setting, sector: int, row: int, seat: int, hall: AuditoryHall) -> Ticket:
        if hall.is_seat_available(sector, row, seat):
            ticket = Ticket(ticket_id, price, setting, sector, row, seat, hall)
            self.__tickets.append(ticket)
            return ticket
        return None
    
    def sell_ticket(self, ticket: Ticket) -> bool:
        if ticket in self.__tickets:
            return ticket.sell_ticket()
        return False
    
    def get_sold_tickets(self) -> List[Ticket]:
        return [t for t in self.__tickets if t.is_sold]
    
    def get_all_tickets(self) -> List[Ticket]:
        return self.__tickets
    
    def get_available_tickets(self) -> List[Ticket]:
        return [t for t in self.__tickets if not t.is_sold]

class PerformanceExecutor:
    def conduct_performance(self, setting: Setting, stage: Stage):
        if stage.is_available:
            stage.setup_stage(setting)
            setting.play()
            stage.free_stage()

class AudienceManager:
    def interact_with_audience(self, hall: AuditoryHall, audience_count: int):
        hall.add_audience(audience_count)

class ResourceManager:
    def __init__(self):
        self.stages: List[Stage] = []
        self.costume_rooms: List[CostumeRoom] = []
        self.auditory_halls: List[AuditoryHall] = []
    
    def add_stage(self, stage: Stage):
        self.stages.append(stage)
    
    def add_costume_room(self, costume_room: CostumeRoom):
        self.costume_rooms.append(costume_room)
    
    def add_auditory_hall(self, hall: AuditoryHall):
        self.auditory_halls.append(hall)
    
    def get_available_stage(self) -> Stage:
        for stage in self.stages:
            if stage.is_available:
                return stage
        return None

class Theater:
    def __init__(self, name: str):
        self.name = name
        self.staff_manager = StaffManager()
        self.performance_manager = PerformanceManager()
        self.ticket_manager = TicketManager()
        self.performance_executor = PerformanceExecutor()
        self.audience_manager = AudienceManager()
        self.resource_manager = ResourceManager()
    
    def get_staff_manager(self) -> StaffManager:
        return self.staff_manager
    
    def get_performance_manager(self) -> PerformanceManager:
        return self.performance_manager
    
    def get_ticket_manager(self) -> TicketManager:
        return self.ticket_manager
    
    def get_performance_executor(self) -> PerformanceExecutor:
        return self.performance_executor
    
    def get_audience_manager(self) -> AudienceManager:
        return self.audience_manager
    
    def get_resource_manager(self) -> ResourceManager:
        return self.resource_manager
    
