import pytest
from datetime import datetime
from src.theater import Theater, Setting, Repetition, Seat, Ticket, AuditoryHall, Stage, Costume, CostumeRoom
from src.staff import Actor, Director, CostumeDesigner
from src.managers import StaffManager, HallManager, PerformanceManager, TicketManager, ResourceManager


@pytest.fixture
def theater():
    """Create a basic theater instance"""
    return Theater("Bolshoi Theater")


@pytest.fixture
def sample_actor():
    """Create a sample actor"""
    return Actor("Leonardo DiCaprio", 48, 50000.0, "Romeo")


@pytest.fixture
def sample_director():
    """Create a sample director"""
    return Director("Baz Luhrmann", 61, 100000.0)


@pytest.fixture
def sample_setting(sample_actor, sample_director):
    """Create a sample setting"""
    setting = Setting(365.0, "Romeo and Juliet", datetime.now(), sample_director)
    setting.add_cast(sample_actor)
    return setting


@pytest.fixture
def sample_hall():
    """Create a sample hall"""
    return AuditoryHall("Main Hall", 3, 10, 15, "hall_001")


@pytest.fixture
def sample_ticket(sample_setting, sample_hall):
    """Create a sample ticket"""
    ticket = Ticket(150.0, sample_setting, 0, 0, 0, sample_hall.hall_id)
    ticket.set_ticket_id("ticket_001")
    return ticket


@pytest.fixture
def sample_stage():
    """Create a sample stage"""
    return Stage("Main Stage", 500, ["Lights", "Sound System", "Curtain"])


@pytest.fixture
def sample_costume():
    """Create a sample costume"""
    return Costume("Romeo Costume", "M", "Red and Gold")


@pytest.fixture
def sample_costume_room():
    """Create a sample costume room"""
    return CostumeRoom("Costume Room 1")