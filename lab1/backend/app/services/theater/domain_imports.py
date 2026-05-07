from __future__ import annotations

import sys
from pathlib import Path


LAB1_ROOT = Path(__file__).resolve().parents[4]
SRC_PATH = LAB1_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from actions import Repetition, Setting
from exception import TheaterException
from halls import AuditoryHall
from staff import Actor, Director
from theater import Theater

__all__ = [
    "Actor",
    "AuditoryHall",
    "Director",
    "Repetition",
    "Setting",
    "Theater",
    "TheaterException",
]
