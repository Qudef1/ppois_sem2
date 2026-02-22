import pytest
import json
from datetime import datetime, timedelta
from src.theater import Theater, Setting, Repetition, Seat, Ticket, AuditoryHall, Stage, Costume, CostumeRoom
from src.staff import Actor, Director, CostumeDesigner
from src.managers import StaffManager, HallManager, PerformanceManager, TicketManager, ResourceManager
from conftest import theater, sample_actor, sample_director, sample_setting, sample_hall, sample_ticket, sample_stage, sample_costume, sample_costume_room


def test_theater_creation(theater):
    """Test theater creation"""
    assert theater.name == "Bolshoi Theater"
    assert theater.staff_manager is not None
    assert theater.resource_manager is not None
    assert theater.performance_manager is not None
    assert theater.ticket_manager is not None


def test_add_staff(theater, sample_actor, sample_director):
    """Test adding staff members"""
    theater.add_staff(sample_actor)
    theater.add_staff(sample_director)
    
    assert len(theater.staff_manager.get_staff()) == 2
    assert theater.staff_manager.get_staff()[0].name == "Leonardo DiCaprio"
    assert theater.staff_manager.get_staff()[1].name == "Baz Luhrmann"


def test_add_hall(theater, sample_hall):
    """Test adding a hall"""
    theater.add_hall(sample_hall)
    
    assert len(theater.resource_manager.hall_manager.halls) == 1
    assert theater.resource_manager.hall_manager.halls[0].name == "Main Hall"
    assert theater.resource_manager.hall_manager.halls[0].hall_id == "hall_001"


def test_add_setting(theater, sample_setting):
    """Test adding a setting"""
    theater.add_setting(sample_setting)
    
    assert len(theater.performance_manager.settings) == 1
    assert theater.performance_manager.settings[0].name == "Romeo and Juliet"
    assert theater.performance_manager.settings[0].director.name == "Baz Luhrmann"
    assert len(theater.performance_manager.settings[0].cast) == 1


def test_add_ticket(theater, sample_ticket):
    """Test adding a ticket"""
    theater.add_ticket(sample_ticket)
    
    assert len(theater.ticket_manager.tickets) == 1
    assert theater.ticket_manager.tickets[0].ticket_id == "ticket_001"
    assert theater.ticket_manager.tickets[0].price == 150.0


def test_sell_ticket(theater, sample_ticket, sample_hall):
    """Test selling a ticket"""
    theater.add_hall(sample_hall)
    theater.add_ticket(sample_ticket)
    
    # First sell should succeed
    result = theater.sell_ticket("ticket_001")
    assert result is True
    assert theater.ticket_manager.tickets[0].is_sold is True
    
    # Second sell should fail
    with pytest.raises(Exception):
        theater.sell_ticket("ticket_001")


def test_seat_availability(sample_hall):
    """Test seat availability logic"""
    assert sample_hall.is_seat_available(0, 0, 0) is True
    
    # Occupy seat and check again
    sample_hall.occupy_seat(0, 0, 0)
    assert sample_hall.is_seat_available(0, 0, 0) is False
    
    # Test invalid seat coordinates
    with pytest.raises(Exception):
        sample_hall.is_seat_available(10, 10, 10)


def test_ticket_link_hall(sample_hall):
    """Test ticket linking to hall"""
    ticket = Ticket(100.0, None, 0, 0, 0, sample_hall.hall_id)
    ticket.set_ticket_id("test_ticket")
    
    # Should raise error before linking
    with pytest.raises(RuntimeError):
        ticket.hall
    
    # Link hall and test
    ticket.link_hall(sample_hall)
    assert ticket.hall == sample_hall


def test_setting_serialization(sample_setting):
    """Test setting serialization and deserialization"""
    data = sample_setting.to_dict()
    restored = Setting.from_dict(data)
    
    assert restored.name == "Romeo and Juliet"
    assert restored.director.name == "Baz Luhrmann"
    assert len(restored.cast) == 1
    assert restored.cast[0].name == "Leonardo DiCaprio"


def test_ticket_serialization(sample_ticket):
    """Test ticket serialization and deserialization"""
    data = sample_ticket.to_dict()
    restored = Ticket.from_dict(data)
    
    assert restored.ticket_id == "ticket_001"
    assert restored.price == 150.0
    assert restored.sector == 0
    assert restored.row == 0
    assert restored.seat == 0


def test_hall_serialization(sample_hall):
    """Test hall serialization and deserialization"""
    data = sample_hall.to_dict()
    restored = AuditoryHall.from_dict(data)
    
    assert restored.name == "Main Hall"
    assert restored.sectors == 3
    assert restored.rows_per_sector == 10
    assert restored.seats_per_row == 15
    assert restored.hall_id == "hall_001"


def test_stage_serialization(sample_stage):
    """Test stage serialization and deserialization"""
    data = sample_stage.to_dict()
    restored = Stage.from_dict(data)
    
    assert restored.name == "Main Stage"
    assert restored.capacity == 500
    assert restored.equipment == ["Lights", "Sound System", "Curtain"]


def test_costume_serialization(sample_costume):
    """Test costume serialization and deserialization"""
    data = sample_costume.to_dict()
    restored = Costume.from_dict(data)
    
    assert restored.name == "Romeo Costume"
    assert restored.size == "M"
    assert restored.color == "Red and Gold"


def test_costume_room_serialization(sample_costume_room):
    """Test costume room serialization and deserialization"""
    data = sample_costume_room.to_dict()
    restored = CostumeRoom.from_dict(data)
    
    assert restored.name == "Costume Room 1"
    assert restored.costume_ids == []


def test_staff_serialization(sample_actor, sample_director):
    """Test staff serialization and deserialization"""
    actor_data = sample_actor.to_dict()
    director_data = sample_director.to_dict()
    
    restored_actor = Actor.from_dict(actor_data)
    restored_director = Director.from_dict(director_data)
    
    assert restored_actor.name == "Leonardo DiCaprio"
    assert restored_actor.role == "Romeo"
    assert restored_director.name == "Baz Luhrmann"


def test_manager_serialization():
    """Test manager serialization and deserialization"""
    staff_manager = StaffManager()
    staff_manager.add_staff(Actor("Actor1", 30, 50000.0))
    staff_manager.add_staff(Director("Director1", 50, 100000.0))
    
    data = staff_manager.to_dict()
    restored = StaffManager.from_dict(data)
    
    assert len(restored.get_staff()) == 2
    assert restored.get_staff()[0].name == "Actor1"
    assert restored.get_staff()[1].name == "Director1"


def test_invalid_seat_exception():
    """Test invalid seat exception"""
    hall = AuditoryHall("Test Hall", 1, 1, 1, "test_hall")
    
    # Test invalid coordinates
    with pytest.raises(Exception):
        hall.is_seat_available(1, 1, 1)
    
    # Test occupied seat
    hall.occupy_seat(0, 0, 0)
    with pytest.raises(Exception):
        hall.occupy_seat(0, 0, 0)


def test_ticket_not_found_exception():
    """Test ticket not found exception"""
    theater = Theater("Test Theater")
    ticket_manager = TicketManager()
    
    with pytest.raises(Exception):
        ticket_manager.sell_ticket("nonexistent_ticket", None)


def test_theater_save_load(tmp_path):
    """Test theater save and load functionality"""
    theater = Theater("Test Theater")
    
    # Add some data
    actor = Actor("Test Actor", 30, 50000.0)
    director = Director("Test Director", 50, 100000.0)
    hall = AuditoryHall("Test Hall", 2, 5, 10, "test_hall")
    setting = Setting(365.0, "Test Setting", datetime.now(), director)
    setting.add_cast(actor)
    ticket = Ticket(100.0, setting, 0, 0, 0, hall.hall_id)
    ticket.set_ticket_id("test_ticket")
    
    theater.add_staff(actor)
    theater.add_staff(director)
    theater.add_hall(hall)
    theater.add_setting(setting)
    theater.add_ticket(ticket)
    
    # Save to file
    filepath = tmp_path / "theater_state.json"
    theater.save_to_file(str(filepath))
    
    # Load from file
    new_theater = Theater("New Theater")
    new_theater.load_from_file(str(filepath))
    
    # Verify loaded data
    assert new_theater.name == "Test Theater"
    assert len(new_theater.staff_manager.get_staff()) == 2
    assert len(new_theater.resource_manager.hall_manager.halls) == 1
    assert len(new_theater.performance_manager.settings) == 1
    assert len(new_theater.ticket_manager.tickets) == 1
    
    # Verify actor-hall interaction
    loaded_actor = new_theater.staff_manager.get_staff()[0]
    loaded_hall = new_theater.resource_manager.hall_manager.get_hall_by_id("test_hall")
    
    # Test seat availability for actor's performance
    assert loaded_hall.is_seat_available(0, 0, 0) is True
    
    # Test ticket creation for actor's performance
    test_ticket = Ticket(150.0, setting, 0, 0, 0, loaded_hall.hall_id)
    test_ticket.set_ticket_id("test_ticket_2")
    new_theater.add_ticket(test_ticket)
    assert len(new_theater.ticket_manager.tickets) == 2
    
    # Test seat occupation
    test_ticket.sell_ticket()
    assert loaded_hall.is_seat_available(0, 0, 0) is False


def test_cli_interaction(tmp_path):
    """Test CLI interaction and actor-hall relationship"""
    from main_menu import TheaterCLI
    
    # Create CLI instance
    cli = TheaterCLI()
    
    # Test adding hall
    cli.add_hall()
    # Simulate user input for hall
    # Note: This would require mocking input() in real testing
    
    # Test adding actor
    cli.add_actor()
    # Simulate user input for actor
    
    # Test creating ticket
    cli.create_ticket()
    # Simulate user input for ticket
    
    # Test saving state
    cli.save_theater()
    
    # Test loading state
    cli.load_theater()


def test_actor_hall_interaction():
    """Test interaction between actors and halls"""
    # Create actor and hall
    actor = Actor("Test Actor", 30, 50000.0)
    hall = AuditoryHall("Test Hall", 2, 5, 10, "test_hall")
    
    # Create setting with actor
    director = Director("Test Director", 50, 100000.0)
    setting = Setting(365.0, "Test Play", datetime.now(), director)
    setting.add_cast(actor)
    
    # Create ticket for actor's performance
    ticket = Ticket(150.0, setting, 0, 0, 0, hall.hall_id)
    ticket.set_ticket_id("actor_ticket")
    
    # Test seat availability
    assert hall.is_seat_available(0, 0, 0) is True
    
    # Test ticket sale
    ticket.sell_ticket()
    assert hall.is_seat_available(0, 0, 0) is False
    assert ticket.is_sold is True
    
    # Test hall occupancy
    assert hall.audience_count == 1
    assert hall.capacity == 100


def test_full_workflow(tmp_path):
    """Test complete workflow from creation to persistence"""
    # Create theater
    theater = Theater("Complete Theater")
    
    # Add staff
    actor = Actor("Main Actor", 35, 60000.0, "Lead Role")
    director = Director("Chief Director", 45, 120000.0)
    theater.add_staff(actor)
    theater.add_staff(director)
    
    # Add hall
    hall = AuditoryHall("Main Hall", 3, 10, 15, "main_hall_001")
    theater.add_hall(hall)
    
    # Add setting
    setting = Setting(180.0, "Complete Play", datetime.now(), director)
    setting.add_cast(actor)
    theater.add_setting(setting)
    
    # Create and sell tickets
    ticket1 = Ticket(200.0, setting, 0, 0, 0, hall.hall_id)
    ticket1.set_ticket_id("ticket_001")
    ticket2 = Ticket(200.0, setting, 0, 0, 1, hall.hall_id)
    ticket2.set_ticket_id("ticket_002")
    
    theater.add_ticket(ticket1)
    theater.add_ticket(ticket2)
    
    # Sell tickets
    ticket1.sell_ticket()
    ticket2.sell_ticket()
    
    # Save to file
    filepath = tmp_path / "complete_theater.json"
    theater.save_to_file(str(filepath))
    
    # Load from file
    new_theater = Theater("Loaded Theater")
    new_theater.load_from_file(str(filepath))
    
    # Verify all data
    assert new_theater.name == "Complete Theater"
    assert len(new_theater.staff_manager.get_staff()) == 2
    assert len(new_theater.resource_manager.hall_manager.halls) == 1
    assert len(new_theater.performance_manager.settings) == 1
    assert len(new_theater.ticket_manager.tickets) == 2
    
    # Verify seat occupancy
    loaded_hall = new_theater.resource_manager.hall_manager.get_hall_by_id("main_hall_001")
    assert loaded_hall.audience_count == 2
    assert loaded_hall.is_seat_available(0, 0, 0) is False
    assert loaded_hall.is_seat_available(0, 0, 1) is False


def test_actor_performance_interaction():
    """Test actor's interaction with performance and hall"""
    # Create actor and director
    actor = Actor("Star Actor", 40, 80000.0, "Protagonist")
    director = Director("Renowned Director", 55, 150000.0)
    
    # Create setting
    setting = Setting(120.0, "Major Performance", datetime.now(), director)
    setting.add_cast(actor)
    
    # Create hall
    hall = AuditoryHall("Grand Hall", 4, 12, 20, "grand_hall_001")
    
    # Create tickets for actor's performance
    tickets = []
    for i in range(5):  # Create 5 tickets
        ticket = Ticket(250.0, setting, 0, 0, i, hall.hall_id)
        ticket.set_ticket_id(f"star_ticket_{i+1:03d}")
        tickets.append(ticket)
    
    # Test actor-hall interaction through tickets
    for ticket in tickets:
        # Test seat availability before sale
        assert hall.is_seat_available(0, 0, ticket.seat) is True
        
        # Sell ticket
        ticket.sell_ticket()
        
        # Test seat availability after sale
        assert hall.is_seat_available(0, 0, ticket.seat) is False
    
    # Verify hall occupancy
    assert hall.audience_count == 5
    assert hall.capacity == 960
    
    # Verify ticket sales
    sold_tickets = sum(1 for t in tickets if t.is_sold)
    assert sold_tickets == 5


# Romeo and Juliet comprehensive test case
@pytest.mark.parametrize("repetitions", [1, 3, 5])
def test_romeo_and_juliet_comprehensive(tmp_path, repetitions):
    """Comprehensive test with full Theater population using Romeo and Juliet"""
    theater = Theater("Verona Theater")
    
    # Create main characters
    romeo = Actor("Leonardo DiCaprio", 48, 80000.0, "Romeo")
    juliet = Actor("Claire Danes", 45, 75000.0, "Juliet")
    mercutio = Actor("John Leguizamo", 58, 60000.0, "Mercutio")
    tybalt = Actor("Harold Perrineau", 60, 55000.0, "Tybalt")
    
    # Create director
    director = Director("Baz Luhrmann", 61, 120000.0)
    
    # Create setting
    setting = Setting(365.0, "Romeo and Juliet", datetime(2024, 5, 15, 20, 0), director)
    setting.add_cast(romeo)
    setting.add_cast(juliet)
    setting.add_cast(mercutio)
    setting.add_cast(tybalt)
    
    # Create hall
    main_hall = AuditoryHall("Verona Main Hall", 3, 15, 20, "verona_main")
    
    # Create stage
    main_stage = Stage("Verona Main Stage", 800, ["LED Screens", "Surround Sound", "Hydraulic Lift"])
    
    # Create costumes
    romeo_costume = Costume("Romeo Costume", "M", "Red and Gold")
    juliet_costume = Costume("Juliet Costume", "S", "White and Blue")
    
    # Create costume room
    costume_room = CostumeRoom("Main Costume Room")
    costume_room.costume_ids.extend([romeo_costume.name, juliet_costume.name])
    
    # Create tickets
    tickets = []
    ticket_id = 1
    for sector in range(3):
        for row in range(15):
            for seat in range(20):
                if ticket_id <= 100:  # Create 100 tickets for testing
                    ticket = Ticket(
                        price=150.0 if sector == 0 else (120.0 if sector == 1 else 80.0),
                        setting=setting,
                        sector=sector,
                        row=row,
                        seat=seat,
                        hall_id=main_hall.hall_id
                    )
                    ticket.set_ticket_id(f"ticket_{ticket_id:03d}")
                    tickets.append(ticket)
                    ticket_id += 1
    
    # Add all to theater
    theater.add_staff(romeo)
    theater.add_staff(juliet)
    theater.add_staff(mercutio)
    theater.add_staff(tybalt)
    theater.add_staff(director)
    
    theater.add_hall(main_hall)
    theater.resource_manager.add_stage(main_stage)
    theater.resource_manager.add_costume(romeo_costume)
    theater.resource_manager.add_costume(juliet_costume)
    theater.resource_manager.add_costume_room(costume_room)
    
    theater.add_setting(setting)
    for ticket in tickets:
        theater.add_ticket(ticket)
    
    # Sell some tickets
    for i in range(20):
        tickets[i].sell_ticket()
    
    # Create repetitions
    repetitions_list = []
    for i in range(repetitions):
        rep_date = datetime(2024, 5, 15, 20, 0) + timedelta(days=i*7)
        repetition = Repetition(365.0, f"Repetition {i+1}", rep_date, setting)
        repetitions_list.append(repetition)
        theater.performance_manager.add_repetition(repetition)
    
    # Save to JSON
    filepath = tmp_path / "romeo_and_juliet_state.json"
    theater.save_to_file(str(filepath))
    
    # Verify counts
    assert len(theater.staff_manager.get_staff()) == 5
    assert len(theater.resource_manager.hall_manager.halls) == 1
    assert len(theater.performance_manager.settings) == 1
    assert len(theater.ticket_manager.tickets) == 100
    assert len(theater.performance_manager.repetitions) == repetitions
    
    # Verify ticket sales
    sold_tickets = sum(1 for t in theater.ticket_manager.tickets if t.is_sold)
    assert sold_tickets == 20
    
    # Verify hall occupancy
    occupied_seats = sum(
        1 for sector in main_hall.seats 
        for row in sector 
        for seat in row 
        if seat.is_occupied
    )
    assert occupied_seats == 20
    
    # Export test data to JSON for inspection
    test_data = {
        "test_name": "Romeo and Juliet Comprehensive Test",
        "theater_name": theater.name,
        "staff_count": len(theater.staff_manager.get_staff()),
        "hall_count": len(theater.resource_manager.hall_manager.halls),
        "setting_name": setting.name,
        "ticket_count": len(theater.ticket_manager.tickets),
        "sold_tickets": sold_tickets,
        "repetitions": repetitions,
        "occupied_seats": occupied_seats,
        "timestamp": datetime.now().isoformat()
    }
    
    with open(tmp_path / "test_summary.json", 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=4)
    
    print(f"\n=== Romeo and Juliet Test Summary ===")
    print(f"Theater: {test_data['theater_name']}")
    print(f"Staff: {test_data['staff_count']}")
    print(f"Halls: {test_data['hall_count']}")
    print(f"Setting: {test_data['setting_name']}")
    print(f"Tickets: {test_data['ticket_count']}")
    print(f"Sold: {test_data['sold_tickets']}")
    print(f"Repetitions: {test_data['repetitions']}")
    print(f"Occupied Seats: {test_data['occupied_seats']}")
    print(f"Timestamp: {test_data['timestamp']}")
    print(f"====================================")