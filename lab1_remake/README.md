# Theater Management System

This is a comprehensive theater management system with CLI interface that allows managing various aspects of a theater including staff, performances, halls, and tickets.

## Features

- Manage theater halls with sectors, rows, and seats
- Create and manage performances and settings
- Handle staff including actors and directors
- Sell tickets and manage seating
- Save and load theater state to/from JSON files
- CLI interface for easy interaction

## Components

### Core Classes

- `Theater`: Main class that orchestrates all components
- `AuditoryHall`: Represents a theater hall with seating arrangement
- `Setting`: Represents a theatrical performance setting
- `Ticket`: Represents a ticket for a specific seat and performance
- `Staff`: Base class for theater personnel (actors, directors)
- `Stage`: Represents a theater stage with equipment
- `Costume`: Represents costumes for performances

### Managers

- `StaffManager`: Handles staff-related operations
- `HallManager`: Manages theater halls
- `PerformanceManager`: Manages performances and settings
- `TicketManager`: Handles ticket operations
- `ResourceManager`: Manages resources like stages and costumes

## Usage

To run the CLI interface:

```bash
cd src
python main_menu.py
```

The CLI provides the following options:

1. Add hall - Create a new theater hall with specified dimensions
2. Add setting - Create a new performance setting
3. Add actor - Add a new actor to the staff
4. Add director - Add a new director to the staff
5. Sell ticket - Sell an existing ticket
6. Show theater info - Display summary information about the theater
7. Save theater state - Save all theater data to a JSON file
8. Load theater state - Load theater data from a JSON file
9. Show halls - List all available halls
10. Show settings - List all available settings/performance
11. Show staff - List all staff members
12. Create ticket - Create a new ticket for a specific seat and performance

## Data Persistence

The system supports saving and loading its complete state to/from JSON files, allowing for persistence between sessions.

## Architecture

The system follows a modular architecture with separate managers for different aspects of theater management. The main Theater class coordinates between all managers to provide a unified interface.