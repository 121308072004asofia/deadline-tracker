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