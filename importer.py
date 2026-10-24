"""Чтение чужого CSV с дедлайнами и чистка грязных данных."""

import csv
from datetime import date, datetime

from models import Deadline

DATE_FORMATS = ["%d.%m.%Y", "%d.%m.%y", "%Y-%m-%d", "%d/%m/%Y"]
ENCODINGS = ["utf-8-sig", "cp1251"]
KNOWN_KINDS = {"дз", "тест", "проект", "экзамен", "контрольная"}
DEFAULT_KIND = "другое"
REQUIRED_COLUMNS = {"предмет", "задание", "дата"}


def parse_date(text):
    """Превращает строку вроде '24.10.2026 23:59' в дату.

    Если дату понять нельзя, выбрасывает ValueError.
    """
    text = text.strip()
    if text == "":
        raise ValueError("пустая дата")

    day_part = text.split()[0]  # отбрасываем время: "24.10.2026 23:59" -> "24.10.2026"
    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(day_part, date_format).date()
        except ValueError:
            continue  # этот формат не подошёл, пробуем следующий

    # Год не написан, например "28.10": берём текущий год
    pieces = day_part.split(".")
    if len(pieces) == 2 and pieces[0].isdigit() and pieces[1].isdigit():
        day, month = int(pieces[0]), int(pieces[1])
        try:
            return date(date.today().year, month, day)
        except ValueError:
            raise ValueError(f"такой даты не бывает: '{text}'")

    raise ValueError(f"не понимаю дату '{text}'")


def normalize_kind(text):
    """'  ДЗ ' -> 'дз'. Неизвестный тип -> 'другое'."""
    kind = text.strip().lower()
    if kind in KNOWN_KINDS:
        return kind
    return DEFAULT_KIND


def read_text(path):
    """Читает файл, пробуя по очереди несколько кодировок."""
    for encoding in ENCODINGS:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue  # не та кодировка, пробуем следующую
    raise ValueError(f"не получилось прочитать {path.name}: неизвестная кодировка")


def read_rows(path):
    """Возвращает строки CSV как список словарей.

    Русский Excel разделяет колонки точкой с запятой, остальные запятой,
    поэтому разделитель угадываем по первой строке.
    """
    lines = read_text(path).splitlines()
    if not lines:
        raise ValueError("файл пустой")
    delimiter = ";" if lines[0].count(";") > lines[0].count(",") else ","
    return list(csv.DictReader(lines, delimiter=delimiter))

def normalize_row(row):
    """Чистит названия колонок и значения от пробелов и регистра колонок."""
    clean = {}
    for column, value in row.items():
        if column is None:
            continue  # лишние ячейки без заголовка
        clean[column.strip().lower()] = (value or "").strip()
    return clean


def row_to_deadline(row):
    """Делает Deadline из одной чистой строки или выбрасывает ValueError."""
    subject = row.get("предмет", "")
    title = row.get("задание", "")
    if subject == "" or title == "":
        raise ValueError("нет предмета или названия задания")
    due = parse_date(row.get("дата", ""))
    kind = normalize_kind(row.get("тип", ""))
    return Deadline(subject, title, due, kind)


def import_file(path):
    """Читает CSV и возвращает (список дедлайнов, список проблем).

    Плохая строка не ломает импорт: она попадает в список проблем.
    """
    rows = read_rows(path)
    if not rows:
        raise ValueError("в файле есть заголовок, но нет строк с данными")

    columns = set(normalize_row(rows[0]).keys())
    missing = REQUIRED_COLUMNS - columns
    if missing:
        raise ValueError(f"в файле нет колонок: {', '.join(sorted(missing))}")

    deadlines = []
    problems = []
    for line_number, raw_row in enumerate(rows, start=2):  # строка 1 это заголовок
        row = normalize_row(raw_row)
        if not any(row.values()):
            continue  # совсем пустая строка
        try:
            deadlines.append(row_to_deadline(row))
        except ValueError as error:
            problems.append(f"строка {line_number}: {error}")
    return deadlines, problems