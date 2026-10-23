"""Чтение чужого CSV с дедлайнами и чистка грязных данных."""

import csv
from datetime import date, datetime

from models import Deadline

DATE_FORMATS = ["%d.%m.%Y", "%d.%m.%y", "%Y-%m-%d", "%d/%m/%Y"]
ENCODINGS = ["utf-8-sig", "cp1251"]
KNOWN_KINDS = {"дз", "тест", "проект", "экзамен", "контрольная"}
DEFAULT_KIND = "другое"
REQUIRED_COLUMNS = {"предмет", "задание", "дата"}