import sys
from pathlib import Path

# Добавляем родительскую директорию в sys.path для импорта пакета
parent_dir = Path(__file__).resolve().parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from student_absences.controllers.main_controller import MainController

if __name__ == "__main__":
    controller = MainController()
    controller.run()