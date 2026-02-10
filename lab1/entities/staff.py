import theater
from typing import List
class Person:

    def __init__(self,name:str,age:int):
        self.name = name
        self.__age = age

    def get_age(self) -> int:
        return self.__age

class Staff(Person):
    def __init__(self,name: str, age: int, salary: float):
        super().__init__(name,age)
        self.__salary = salary

    def attend_repetition(self,repetition:theater.Repetition):
        repetition.check_list(self)

    def __get_salary(self) -> float:
        return self.__salary

class Actor(Staff):
    def __init__(self, name: str, age: int, salary: float, role: str = None):
        super().__init__(name,age,salary)
        self.role = role

class Director(Staff):
    def __init__(self, name: str, age: int, salary: float):
        super().__init__(name,age,salary)
        self.__directed_settings:  List[theater.Setting] = []

    def direct_setting(self,setting:theater.Setting):
        self.__directed_settings.append(setting)

class CostumeDesigner(Staff):
    def __init__(self, name: str, age: int, salary: float):
        super().__init__(name, age, salary)
        self.__created_costumes: List[theater.Costume] = []

    def create_costume(self, costume: theater.Costume):
        self.__created_costumes.append(costume)



