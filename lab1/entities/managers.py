from typing import List, Dict, Any
from staff import Staff, Actor, Director, CostumeDesigner

class StaffManager:
    def __init__(self):
        self.staff: List[Staff] = []

    def add_staff(self, staff_member: Staff):
        self.staff.append(staff_member)

    def get_staff(self) -> List[Staff]:
        return self.staff

    def to_dict(self) -> Dict[str, Any]:
        return {"staff": [s.to_dict() for s in self.staff]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StaffManager":
        manager = cls()
        for staff_data in data.get("staff", []):
            # определить тип
            if "role" in staff_data:
                staff_obj = Actor.from_dict(staff_data)
            elif "directed_settings" in staff_data:
                staff_obj = Director.from_dict(staff_data)
            elif "created_costumes" in staff_data:
                staff_obj = CostumeDesigner.from_dict(staff_data)
            else:
                staff_obj = Staff.from_dict(staff_data)
            manager.add_staff(staff_obj)
        return manager