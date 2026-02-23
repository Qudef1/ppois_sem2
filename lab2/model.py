"""
Модуль данных приложения (Model в MVC).

Содержит:
- SchemaConfig: описание схемы данных.
- RecordModel: управление данными, БД, XML.
- SAX-парсер для чтения XML.
- DOM-генератор для записи XML.
"""

import sqlite3
import xml.sax
import xml.sax.handler
from datetime import date
from pathlib import Path
from typing import Any, Callable, Optional
from xml.dom import minidom
from xml.dom.minidom import Document, Element

from config import FIELD_SCHEMA, FieldConfig, FieldType, get_field_by_name


class SchemaConfig:
    """
    Конфигурация схемы данных.

    Предоставляет методы для работы с конфигурацией полей.
    """

    def __init__(self, fields: list[FieldConfig] = FIELD_SCHEMA):
        """
        Инициализация конфигурации схемы.

        Args:
            fields: Список конфигураций полей.
        """
        self._fields = fields
        self._fields_by_name: dict[str, FieldConfig] = {
            f.name: f for f in fields
        }

    @property
    def fields(self) -> list[FieldConfig]:
        """Получить список всех полей."""
        return self._fields

    @property
    def field_names(self) -> list[str]:
        """Получить список имён полей."""
        return [f.name for f in self._fields]

    def get_field(self, name: str) -> Optional[FieldConfig]:
        """Получить конфигурацию поля по имени."""
        return self._fields_by_name.get(name)

    def get_sql_type(self, field_type: FieldType) -> str:
        """Получить SQL-тип для типа поля."""
        type_mapping = {
            FieldType.STRING: "TEXT",
            FieldType.INTEGER: "INTEGER",
            FieldType.FLOAT: "REAL",
            FieldType.DATE: "TEXT",  # Храним как ISO-строку
            FieldType.ENUM: "TEXT",
        }
        return type_mapping.get(field_type, "TEXT")

    def validate_value(
        self, field_name: str, value: Any
    ) -> tuple[bool, Optional[str]]:
        """
        Проверить значение поля на валидность.

        Args:
            field_name: Имя поля.
            value: Значение для проверки.

        Returns:
            Кортеж (валидно, сообщение об ошибке).
        """
        field = self.get_field(field_name)
        if not field:
            return False, f"Поле '{field_name}' не найдено"

        # Проверка на обязательность
        if field.required and (value is None or value == ""):
            return False, f"Поле '{field.label}' обязательно"

        if value is None or value == "":
            return True, None  # Необязательное поле пустое

        # Проверка типа
        if field.field_type == FieldType.INTEGER:
            if not isinstance(value, int):
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    return False, f"Поле '{field.label}' должно быть целым числом"

        elif field.field_type == FieldType.FLOAT:
            if not isinstance(value, (int, float)):
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    return False, f"Поле '{field.label}' должно быть числом"

        elif field.field_type == FieldType.DATE:
            if not isinstance(value, date):
                return False, f"Поле '{field.label}' должно быть датой"

        # Проверка диапазона
        if field.min_value is not None and value < field.min_value:
            return False, f"Значение должно быть >= {field.min_value}"
        if field.max_value is not None and value > field.max_value:
            return False, f"Значение должно быть <= {field.max_value}"

        # Проверка enum
        if field.field_type == FieldType.ENUM:
            if field.enum_values and value not in field.enum_values:
                return False, f"Значение должно быть одним из: {field.enum_values}"

        return True, None


class XMLSAXHandler(xml.sax.handler.ContentHandler):
    """
    SAX-обработчик для чтения XML.

    Парсит XML файл и собирает записи в список словарей.
    """

    def __init__(self):
        """Инициализация обработчика."""
        super().__init__()
        self._records: list[dict[str, Any]] = []
        self._current_record: Optional[dict[str, Any]] = None
        self._current_field: Optional[str] = None
        self._current_value: str = ""

    @property
    def records(self) -> list[dict[str, Any]]:
        """Получить распарсенные записи."""
        return self._records

    def startElement(self, name: str, attrs: Any) -> None:
        """Обработка начального тега."""
        if name == "record":
            self._current_record = {}
            if "id" in attrs:
                try:
                    self._current_record["id"] = int(attrs["id"])
                except ValueError:
                    self._current_record["id"] = None
        elif name == "field":
            self._current_field = attrs.get("name")
            self._current_value = ""

    def endElement(self, name: str) -> None:
        """Обработка конечного тега."""
        if name == "record":
            if self._current_record:
                self._records.append(self._current_record)
            self._current_record = None
        elif name == "field":
            if self._current_record is not None and self._current_field:
                self._current_record[self._current_field] = self._current_value.strip()
            self._current_field = None
            self._current_value = ""

    def characters(self, content: str) -> None:
        """Обработка текстового содержимого."""
        if self._current_field:
            self._current_value += content


class XMLDOMWriter:
    """
    DOM-писатель для записи XML.

    Создаёт XML документ с использованием minidom.
    """

    def __init__(self, schema: SchemaConfig):
        """
        Инициализация писателя.

        Args:
            schema: Конфигурация схемы данных.
        """
        self._schema = schema

    def write(
        self, records: list[dict[str, Any]], filepath: Path
    ) -> None:
        """
        Записать записи в XML файл.

        Args:
            records: Список записей для записи.
            filepath: Путь к файлу.
        """
        doc = minidom.Document()

        # Корневой элемент
        root = doc.createElement("records")
        root.setAttribute("count", str(len(records)))
        doc.appendChild(root)

        for record in records:
            record_elem = doc.createElement("record")
            if "id" in record and record["id"] is not None:
                record_elem.setAttribute("id", str(record["id"]))
            root.appendChild(record_elem)

            # Поля записи
            for field_name in self._schema.field_names:
                if field_name == "id":
                    continue

                field_elem = doc.createElement("field")
                field_elem.setAttribute("name", field_name)

                value = record.get(field_name, "")
                if value is None:
                    value = ""

                # Конвертация в строку
                if isinstance(value, date):
                    value = value.isoformat()

                text_node = doc.createTextNode(str(value))
                field_elem.appendChild(text_node)
                record_elem.appendChild(field_elem)

        # Запись в файл
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            doc.writexml(f, indent="  ", addindent="  ", newl="\n", encoding="utf-8")


class RecordModel:
    """
    Модель данных для управления записями.

    Отвечает за:
    - Работу с SQLite базой данных.
    - Синхронизацию с XML файлом.
    - CRUD операции.
    """

    def __init__(
        self,
        db_path: Path,
        xml_path: Path,
        schema: SchemaConfig,
    ):
        """
        Инициализация модели.

        Args:
            db_path: Путь к SQLite базе данных.
            xml_path: Путь к XML файлу.
            schema: Конфигурация схемы данных.
        """
        self._db_path = db_path
        self._xml_path = xml_path
        self._schema = schema
        self._conn: Optional[sqlite3.Connection] = None
        self._xml_writer = XMLDOMWriter(schema)

        self._init_db()

    def _init_db(self) -> None:
        """Инициализация базы данных и создание таблиц."""
        try:
            self._conn = sqlite3.connect(str(self._db_path))
            self._conn.row_factory = sqlite3.Row
            self._create_table()
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка инициализации БД: {e}")

    def _create_table(self) -> None:
        """Создание таблицы для записей."""
        if not self._conn:
            return

        columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]

        for field in self._schema.fields:
            sql_type = self._schema.get_sql_type(field.field_type)
            nullable = "" if field.required else "NULL"
            columns.append(f"{field.name} {sql_type} {nullable}")

        columns_sql = ", ".join(columns)
        create_sql = f"CREATE TABLE IF NOT EXISTS records ({columns_sql})"

        try:
            self._conn.execute(create_sql)
            self._conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка создания таблицы: {e}")

    def close(self) -> None:
        """Закрытие соединения с БД."""
        if self._conn:
            self._conn.close()
            self._conn = None

    # ==================== CRUD операции ====================

    def get_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> list[dict[str, Any]]:
        """
        Получить все записи с пагинацией.

        Args:
            limit: Максимальное количество записей.
            offset: Смещение.

        Returns:
            Список записей.
        """
        return self._query(limit=limit, offset=offset)

    def get_count(self) -> int:
        """Получить общее количество записей."""
        if not self._conn:
            return 0

        try:
            cursor = self._conn.execute("SELECT COUNT(*) FROM records")
            return cursor.fetchone()[0]
        except sqlite3.Error:
            return 0

    def get_by_id(self, record_id: int) -> Optional[dict[str, Any]]:
        """
        Получить запись по ID.

        Args:
            record_id: ID записи.

        Returns:
            Запись или None.
        """
        if not self._conn:
            return None

        try:
            cursor = self._conn.execute(
                "SELECT * FROM records WHERE id = ?", (record_id,)
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_dict(row)
            return None
        except sqlite3.Error:
            return None

    def insert(self, record: dict[str, Any]) -> int:
        """
        Вставить новую запись.

        Args:
            record: Данные записи.

        Returns:
            ID вставленной записи.
        """
        if not self._conn:
            raise RuntimeError("База данных не инициализирована")

        # Валидация
        for field_name in self._schema.field_names:
            if field_name == "id":
                continue
            value = record.get(field_name)
            is_valid, error = self._schema.validate_value(field_name, value)
            if not is_valid:
                raise ValueError(error)

        # Конвертация значений
        converted = self._convert_for_db(record)

        columns = ", ".join(f.name for f in self._schema.fields if f.name != "id")
        placeholders = ", ".join("?" for _ in self._schema.fields if f.name != "id")
        values = [converted[f.name] for f in self._schema.fields if f.name != "id"]

        try:
            cursor = self._conn.execute(
                f"INSERT INTO records ({columns}) VALUES ({placeholders})",
                values,
            )
            self._conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка вставки записи: {e}")

    def update(self, record_id: int, record: dict[str, Any]) -> bool:
        """
        Обновить запись.

        Args:
            record_id: ID записи.
            record: Новые данные.

        Returns:
            True если успешно.
        """
        if not self._conn:
            raise RuntimeError("База данных не инициализирована")

        # Валидация
        for field_name, value in record.items():
            if field_name == "id":
                continue
            is_valid, error = self._schema.validate_value(field_name, value)
            if not is_valid:
                raise ValueError(error)

        # Конвертация значений
        converted = self._convert_for_db(record)

        set_parts = []
        values = []
        for field_name, value in converted.items():
            if field_name == "id":
                continue
            set_parts.append(f"{field_name} = ?")
            values.append(value)

        values.append(record_id)

        try:
            self._conn.execute(
                f"UPDATE records SET {', '.join(set_parts)} WHERE id = ?",
                values,
            )
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка обновления записи: {e}")

    def delete(self, record_id: int) -> bool:
        """
        Удалить запись по ID.

        Args:
            record_id: ID записи.

        Returns:
            True если успешно.
        """
        if not self._conn:
            raise RuntimeError("База данных не инициализирована")

        try:
            self._conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка удаления записи: {e}")

    def delete_by_condition(self, conditions: dict[str, Any]) -> int:
        """
        Удалить записи по условию.

        Args:
            conditions: Словарь {поле: значение} для условия WHERE.

        Returns:
            Количество удалённых записей.
        """
        if not self._conn:
            raise RuntimeError("База данных не инициализирована")

        if not conditions:
            return 0

        where_parts = []
        values = []

        for field_name, value in conditions.items():
            where_parts.append(f"{field_name} = ?")
            values.append(value)

        where_sql = " AND ".join(where_parts)

        try:
            cursor = self._conn.execute(
                f"DELETE FROM records WHERE {where_sql}", values
            )
            self._conn.commit()
            return cursor.rowcount
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка удаления по условию: {e}")

    def search(
        self,
        conditions: dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """
        Поиск записей по условиям.

        Args:
            conditions: Словарь {поле: значение} для условия WHERE.
            limit: Максимальное количество записей.
            offset: Смещение.

        Returns:
            Список найденных записей.
        """
        if not self._conn:
            return []

        if not conditions:
            return self.get_all(limit=limit, offset=offset)

        where_parts = []
        values = []

        for field_name, value in conditions.items():
            where_parts.append(f"{field_name} LIKE ?")
            values.append(f"%{value}%")

        where_sql = " AND ".join(where_parts)

        query = f"SELECT * FROM records WHERE {where_sql}"

        if limit:
            query += f" LIMIT {limit}"
        if offset:
            query += f" OFFSET {offset}"

        try:
            cursor = self._conn.execute(query, values)
            return [self._row_to_dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def search_with_operators(
        self,
        conditions: list[tuple[str, str, Any]],
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """
        Поиск с операторами сравнения.

        Args:
            conditions: Список кортежей (поле, оператор, значение).
            limit: Максимальное количество записей.
            offset: Смещение.

        Returns:
            Список найденных записей.
        """
        if not self._conn:
            return []

        if not conditions:
            return self.get_all(limit=limit, offset=offset)

        where_parts = []
        values = []

        for field_name, operator, value in conditions:
            if operator == "=":
                where_parts.append(f"{field_name} = ?")
            elif operator == "!=":
                where_parts.append(f"{field_name} != ?")
            elif operator == ">":
                where_parts.append(f"{field_name} > ?")
            elif operator == ">=":
                where_parts.append(f"{field_name} >= ?")
            elif operator == "<":
                where_parts.append(f"{field_name} < ?")
            elif operator == "<=":
                where_parts.append(f"{field_name} <= ?")
            elif operator == "LIKE":
                where_parts.append(f"{field_name} LIKE ?")
                value = f"%{value}%"
            else:
                where_parts.append(f"{field_name} = ?")

            values.append(value)

        where_sql = " AND ".join(where_parts)
        query = f"SELECT * FROM records WHERE {where_sql}"

        if limit:
            query += f" LIMIT {limit}"
        if offset:
            query += f" OFFSET {offset}"

        try:
            cursor = self._conn.execute(query, values)
            return [self._row_to_dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    # ==================== XML операции ====================

    def save_to_xml(self, filepath: Optional[Path] = None) -> None:
        """
        Сохранить все записи в XML файл.

        Args:
            filepath: Путь к файлу (если None, используется xml_path).
        """
        filepath = filepath or self._xml_path
        records = self.get_all()
        self._xml_writer.write(records, filepath)

    def load_from_xml(self, filepath: Optional[Path] = None) -> int:
        """
        Загрузить записи из XML файла.

        Args:
            filepath: Путь к файлу (если None, используется xml_path).

        Returns:
            Количество загруженных записей.
        """
        filepath = filepath or self._xml_path

        if not filepath.exists():
            raise FileNotFoundError(f"XML файл не найден: {filepath}")

        try:
            handler = XMLSAXHandler()
            parser = xml.sax.make_parser()
            parser.setContentHandler(handler)

            with open(filepath, "rb") as f:
                parser.parse(f)

            records = handler.records

            # Вставляем записи в БД
            count = 0
            for record in records:
                try:
                    # Проверяем, есть ли запись с таким ID
                    if "id" in record and record["id"]:
                        existing = self.get_by_id(record["id"])
                        if existing:
                            self.update(record["id"], record)
                        else:
                            self.insert(record)
                    else:
                        self.insert(record)
                    count += 1
                except (ValueError, RuntimeError):
                    # Пропускаем невалидные записи
                    continue

            return count
        except xml.sax.SAXException as e:
            raise RuntimeError(f"Ошибка парсинга XML: {e}")

    # ==================== Вспомогательные методы ====================

    def _query(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: str = "id",
    ) -> list[dict[str, Any]]:
        """Выполнить SQL запрос с пагинацией."""
        if not self._conn:
            return []

        query = f"SELECT * FROM records ORDER BY {order_by}"

        if limit:
            query += f" LIMIT {limit}"
        if offset:
            query += f" OFFSET {offset}"

        try:
            cursor = self._conn.execute(query)
            return [self._row_to_dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def _row_to_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        """Преобразовать строку БД в словарь."""
        result = dict(row)

        # Конвертация значений
        for field in self._schema.fields:
            value = result.get(field.name)
            if value is None:
                continue

            if field.field_type == FieldType.DATE and isinstance(value, str):
                try:
                    result[field.name] = date.fromisoformat(value)
                except ValueError:
                    pass
            elif field.field_type == FieldType.INTEGER and isinstance(value, int):
                pass
            elif field.field_type == FieldType.FLOAT and isinstance(value, (int, float)):
                result[field.name] = float(value)

        return result

    def _convert_for_db(self, record: dict[str, Any]) -> dict[str, Any]:
        """Конвертировать значения записи для записи в БД."""
        converted = record.copy()

        for field in self._schema.fields:
            value = converted.get(field.name)
            if value is None:
                continue

            if field.field_type == FieldType.DATE and isinstance(value, date):
                converted[field.name] = value.isoformat()

        return converted
