"""
Утилитные модули для приложения.

Содержит:
- Класс PaginationHelper для логики пагинации.
- Класс DataGenerator для генерации тестовых данных.
"""

import random
import string
from datetime import date, timedelta
from typing import Any, Optional

from config import FIELD_SCHEMA, FieldConfig, FieldType


class PaginationHelper:
    """
    Класс-помощник для расчётов пагинации.

    Инкапсулирует логику вычисления страниц, смещений и границ.
    """

    def __init__(self, total_items: int = 0, page_size: int = 10):
        """
        Инициализация помощника пагинации.

        Args:
            total_items: Общее количество элементов.
            page_size: Количество элементов на странице.
        """
        self._total_items = total_items
        self._page_size = max(1, page_size)
        self._current_page = 1

    @property
    def total_items(self) -> int:
        """Получить общее количество элементов."""
        return self._total_items

    @total_items.setter
    def total_items(self, value: int) -> None:
        """Установить общее количество элементов."""
        self._total_items = max(0, value)
        # Корректируем текущую страницу при уменьшении количества
        if self._current_page > self.total_pages and self.total_pages > 0:
            self._current_page = self.total_pages

    @property
    def page_size(self) -> int:
        """Получить размер страницы."""
        return self._page_size

    @page_size.setter
    def page_size(self, value: int) -> None:
        """Установить размер страницы."""
        self._page_size = max(1, value)
        # Пересчитываем текущую страницу
        if self._current_page > self.total_pages and self.total_pages > 0:
            self._current_page = self.total_pages

    @property
    def current_page(self) -> int:
        """Получить текущую страницу (1-based)."""
        return self._current_page

    @current_page.setter
    def current_page(self, value: int) -> None:
        """Установить текущую страницу."""
        if self.total_pages > 0:
            self._current_page = max(1, min(value, self.total_pages))
        else:
            self._current_page = 1

    @property
    def total_pages(self) -> int:
        """Получить общее количество страниц."""
        if self._total_items == 0:
            return 0
        return (self._total_items + self._page_size - 1) // self._page_size

    @property
    def offset(self) -> int:
        """Получить смещение для SQL-запроса (0-based)."""
        return (self._current_page - 1) * self._page_size

    @property
    def has_previous(self) -> bool:
        """Есть ли предыдущая страница."""
        return self._current_page > 1

    @property
    def has_next(self) -> bool:
        """Есть ли следующая страница."""
        return self._current_page < self.total_pages

    @property
    def start_index(self) -> int:
        """Получить индекс первого элемента на странице (1-based для UI)."""
        if self._total_items == 0:
            return 0
        return self.offset + 1

    @property
    def end_index(self) -> int:
        """Получить индекс последнего элемента на странице (1-based для UI)."""
        if self._total_items == 0:
            return 0
        return min(self.offset + self._page_size, self._total_items)

    def next_page(self) -> int:
        """Перейти на следующую страницу. Вернуть новый номер страницы."""
        if self.has_next:
            self._current_page += 1
        return self._current_page

    def previous_page(self) -> int:
        """Перейти на предыдущую страницу. Вернуть новый номер страницы."""
        if self.has_previous:
            self._current_page -= 1
        return self._current_page

    def first_page(self) -> int:
        """Перейти на первую страницу. Вернуть новый номер страницы."""
        self._current_page = 1
        return self._current_page

    def last_page(self) -> int:
        """Перейти на последнюю страницу. Вернуть новый номер страницы."""
        self._current_page = self.total_pages if self.total_pages > 0 else 1
        return self._current_page

    def get_page_range(self, items: list[Any]) -> list[Any]:
        """
        Получить срез элементов для текущей страницы.

        Args:
            items: Полный список элементов.

        Returns:
            Список элементов для текущей страницы.
        """
        start = self.offset
        end = start + self._page_size
        return items[start:end]


class DataGenerator:
    """
    Генератор тестовых данных согласно конфигурации полей.

    Создаёт осмысленные данные для тестирования приложения.
    """

    # Данные для генерации
    FIRST_NAMES_M = [
        "Александр", "Дмитрий", "Максим", "Сергей", "Андрей",
        "Алексей", "Артём", "Илья", "Кирилл", "Михаил"
    ]
    FIRST_NAMES_F = [
        "Анна", "Мария", "Елена", "Дарья", "Алина",
        "Ирина", "Екатерина", "Арина", "Полина", "Ольга"
    ]
    LAST_NAMES_M = [
        "Иванов", "Смирнов", "Кузнецов", "Попов", "Васильев",
        "Петров", "Соколов", "Михайлов", "Новиков", "Фёдоров"
    ]
    LAST_NAMES_F = [
        "Иванова", "Смирнова", "Кузнецова", "Попова", "Васильева",
        "Петрова", "Соколова", "Михайлова", "Новикова", "Фёдорова"
    ]
    MIDDLE_NAMES_M = [
        "Александрович", "Дмитриевич", "Максимович", "Сергеевич", "Андреевич",
        "Алексеевич", "Артёмович", "Ильич", "Кириллович", "Михайлович"
    ]
    MIDDLE_NAMES_F = [
        "Александровна", "Дмитриевна", "Максимовна", "Сергеевна", "Андреевна",
        "Алексеевна", "Артёмовна", "Ильинична", "Кирилловна", "Михайловна"
    ]
    DIAGNOSES = [
        "ОРВИ", "Грипп", "Гастрит", "Гипертония", "Остеохондроз",
        "Бронхит", "Пневмония", "Анемия", "Диабет 2 типа", "Здоров",
        "Мигрень", "Аллергия", "Астма", "Аритмия", "Гастроэзофагеальная рефлюксная болезнь"
    ]

    def __init__(self, schema: list[FieldConfig] = FIELD_SCHEMA):
        """
        Инициализация генератора.

        Args:
            schema: Конфигурация полей для генерации данных.
        """
        self._schema = schema
        self._random = random.Random()

    def set_seed(self, seed: int) -> None:
        """Установить seed для воспроизводимости данных."""
        self._random.seed(seed)

    def generate_record(self, record_id: Optional[int] = None) -> dict[str, Any]:
        """
        Сгенерировать одну запись.

        Args:
            record_id: ID записи (если None, генерируется случайно).

        Returns:
            Словарь с данными записи.
        """
        record: dict[str, Any] = {}
        if record_id is not None:
            record["id"] = record_id

        # Определяем пол первым, так как от него зависят ФИО
        gender = self._random.choice(["М", "Ж"])

        for field_config in self._schema:
            value = self._generate_field_value(field_config, gender)
            record[field_config.name] = value

        return record

    def _generate_field_value(
        self, field_config: FieldConfig, gender: str
    ) -> Any:
        """
        Сгенерировать значение для одного поля.

        Args:
            field_config: Конфигурация поля.
            gender: Пол ("М" или "Ж") для генерации ФИО.

        Returns:
            Сгенерированное значение.
        """
        field_type = field_config.field_type

        if field_type == FieldType.STRING:
            return self._generate_string(field_config, gender)
        elif field_type == FieldType.INTEGER:
            return self._generate_integer(field_config)
        elif field_type == FieldType.FLOAT:
            return self._generate_float(field_config)
        elif field_type == FieldType.DATE:
            return self._generate_date(field_config)
        elif field_type == FieldType.ENUM:
            return self._generate_enum(field_config)
        else:
            return None

    def _generate_string(self, field_config: FieldConfig, gender: str) -> str:
        """Сгенерировать строковое значение."""
        name = field_config.name

        if name == "full_name":
            return self._generate_full_name(gender)
        elif name == "policy_number":
            return self._generate_policy_number()
        elif name == "diagnosis":
            return self._random.choice(self.DIAGNOSES)
        else:
            # Генерируем случайную строку
            length = self._random.randint(5, 20)
            return "".join(
                self._random.choices(string.ascii_letters + " ", k=length)
            )

    def _generate_integer(self, field_config: FieldConfig) -> int:
        """Сгенерировать целочисленное значение."""
        min_val = field_config.min_value if field_config.min_value is not None else 0
        max_val = field_config.max_value if field_config.max_value is not None else 100

        # Для возраста используем более реалистичный диапазон
        if field_config.name == "age":
            return self._random.randint(1, 100)

        return self._random.randint(min_val, max_val)

    def _generate_float(self, field_config: FieldConfig) -> float:
        """Сгенерировать значение с плавающей точкой."""
        min_val = field_config.min_value if field_config.min_value is not None else 0.0
        max_val = field_config.max_value if field_config.max_value is not None else 100.0

        # Для роста и веса используем реалистичные значения
        if field_config.name == "height":
            return round(self._random.uniform(150.0, 200.0), 1)
        elif field_config.name == "weight":
            return round(self._random.uniform(45.0, 120.0), 1)

        return round(self._random.uniform(min_val, max_val), 2)

    def _generate_date(self, field_config: FieldConfig) -> date:
        """Сгенерировать дату."""
        today = date.today()

        if field_config.name == "birth_date":
            # Дата рождения: от 1 до 100 лет назад
            years_ago = self._random.randint(1, 100)
            return today.replace(year=today.year - years_ago)
        elif field_config.name == "last_visit_date":
            # Последний визит: от 1 дня до 2 лет назад
            days_ago = self._random.randint(1, 730)
            return today - timedelta(days=days_ago)
        else:
            # Случайная дата в пределах года
            days_offset = self._random.randint(-365, 365)
            return today + timedelta(days=days_offset)

    def _generate_enum(self, field_config: FieldConfig) -> str:
        """Сгенерировать значение enum."""
        if field_config.enum_values:
            return self._random.choice(field_config.enum_values)
        return ""

    def _generate_full_name(self, gender: str) -> str:
        """Сгенерировать ФИО."""
        if gender == "М":
            first = self._random.choice(self.FIRST_NAMES_M)
            last = self._random.choice(self.LAST_NAMES_M)
            middle = self._random.choice(self.MIDDLE_NAMES_M)
        else:
            first = self._random.choice(self.FIRST_NAMES_F)
            last = self._random.choice(self.LAST_NAMES_F)
            middle = self._random.choice(self.MIDDLE_NAMES_F)

        return f"{last} {first} {middle}"

    def _generate_policy_number(self) -> str:
        """Сгенерировать номер полиса ОМС."""
        # Формат: 18 цифр
        return "".join(str(self._random.randint(0, 9)) for _ in range(18))

    def generate_records(self, count: int = 50) -> list[dict[str, Any]]:
        """
        Сгенерировать список записей.

        Args:
            count: Количество записей для генерации.

        Returns:
            Список словарей с данными записей.
        """
        records = []
        for i in range(1, count + 1):
            records.append(self.generate_record(record_id=i))
        return records
