"""
Конфигурация полей для лабораторной работы.

Модуль описывает схему данных для конкретного варианта.
В данном примере — Вариант 5: Пациенты.

Для изменения варианта отредактируйте FIELD_SCHEMA и при необходимости
ENUM_VALUES.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum


class FieldType(Enum):
    """Типы полей для схемы данных."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    DATE = "date"
    ENUM = "enum"


@dataclass
class FieldConfig:
    """
    Конфигурация одного поля.

    Attributes:
        name: Имя поля (для БД и кода).
        label: Отображаемое имя поля (для UI).
        field_type: Тип поля.
        required: Обязательно ли поле для заполнения.
        min_value: Минимальное значение (для чисел и дат).
        max_value: Максимальное значение (для чисел и дат).
        enum_values: Список допустимых значений для типа ENUM.
        default: Значение по умолчанию.
    """
    name: str
    label: str
    field_type: FieldType
    required: bool = True
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    enum_values: list[str] = field(default_factory=list)
    default: Any = None


# =============================================================================
# КОНФИГУРАЦИЯ ВАРИАНТА 5: ПАЦИЕНТЫ
# =============================================================================
# Поля:
#   - ФИО (string)
#   - Дата рождения (date)
#   - Пол (enum: М, Ж)
#   - Номер полиса (string)
#   - Возраст (integer)
#   - Рост (float)
#   - Вес (float)
#   - Дата последнего визита (date)
#   - Диагноз (string)
#   - Статус (enum: амбулаторный, стационарный, выписан)
# =============================================================================

FIELD_SCHEMA: list[FieldConfig] = [
    FieldConfig(
        name="full_name",
        label="ФИО",
        field_type=FieldType.STRING,
        required=True,
    ),
    FieldConfig(
        name="birth_date",
        label="Дата рождения",
        field_type=FieldType.DATE,
        required=True,
    ),
    FieldConfig(
        name="gender",
        label="Пол",
        field_type=FieldType.ENUM,
        required=True,
        enum_values=["М", "Ж"],
        default="М",
    ),
    FieldConfig(
        name="policy_number",
        label="Номер полиса",
        field_type=FieldType.STRING,
        required=True,
    ),
    FieldConfig(
        name="age",
        label="Возраст",
        field_type=FieldType.INTEGER,
        required=True,
        min_value=0,
        max_value=150,
    ),
    FieldConfig(
        name="height",
        label="Рост (см)",
        field_type=FieldType.FLOAT,
        required=True,
        min_value=50.0,
        max_value=250.0,
    ),
    FieldConfig(
        name="weight",
        label="Вес (кг)",
        field_type=FieldType.FLOAT,
        required=True,
        min_value=2.0,
        max_value=300.0,
    ),
    FieldConfig(
        name="last_visit_date",
        label="Дата последнего визита",
        field_type=FieldType.DATE,
        required=False,
    ),
    FieldConfig(
        name="diagnosis",
        label="Диагноз",
        field_type=FieldType.STRING,
        required=False,
    ),
    FieldConfig(
        name="status",
        label="Статус",
        field_type=FieldType.ENUM,
        required=True,
        enum_values=["амбулаторный", "стационарный", "выписан"],
        default="амбулаторный",
    ),
]

# Мета-информация о варианте
VARIANT_INFO = {
    "number": 5,
    "title": "Пациенты",
    "description": "Управление записями о пациентах медицинского учреждения",
}

# Настройки приложения
APP_SETTINGS = {
    "app_name": "Менеджер записей: Пациенты",
    "db_filename": "patients.db",
    "xml_filename": "patients.xml",
    "default_page_size": 10,
    "page_sizes": [5, 10, 20, 50, 100],
}


def get_field_by_name(name: str) -> Optional[FieldConfig]:
    """Получить конфигурацию поля по имени."""
    for field in FIELD_SCHEMA:
        if field.name == name:
            return field
    return None


def get_field_names() -> list[str]:
    """Получить список всех имён полей."""
    return [f.name for f in FIELD_SCHEMA]


def get_field_labels() -> list[str]:
    """Получить список всех отображаемых имён полей."""
    return [f.label for f in FIELD_SCHEMA]
