"""Сохранение дедлайнов между запусками в файл CSV."""

import csv
from datetime import date
from pathlib import Path

from models import Deadline

FIELDS = ["subject", "title", "due", "kind", "done"]


class DeadlineStore:
    """Все дедлайны программы и их файл на диске."""

    def __init__(self, path):
        self.path = Path(path)
        self.deadlines = []
        self.broken_lines = []  # номера строк, которые не удалось прочитать

    def load(self):
        """Читает файл. Если файла нет, это первый запуск: список пустой."""
        if not self.path.exists():
            return
        with open(self.path, encoding="utf-8", newline="") as file:
            for line_number, row in enumerate(csv.DictReader(file), start=2):
                try:
                    self.deadlines.append(self._row_to_deadline(row))
                except (KeyError, ValueError, TypeError):
                    self.broken_lines.append(line_number)

    def _row_to_deadline(self, row):
        due = date.fromisoformat(row["due"])
        return Deadline(row["subject"], row["title"], due, row["kind"], row["done"] == "1")

    def save(self):
        """Записывает все дедлайны в файл (папку создаёт, если её нет)."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writeheader()
            for deadline in self.deadlines:
                writer.writerow({
                    "subject": deadline.subject,
                    "title": deadline.title,
                    "due": deadline.due.isoformat(),
                    "kind": deadline.kind,
                    "done": "1" if deadline.done else "0",
                })

    def find(self, key):
        """Ищет дедлайн с таким же ключом. Не нашли -> None."""
        for deadline in self.deadlines:
            if deadline.key() == key:
                return deadline
        return None

    def merge(self, new_deadlines):
        """Добавляет новые дедлайны и обновляет даты перенесённых.

        Возвращает три числа: сколько добавлено, перенесено и без изменений.
        Отметка "сдано" у старых заданий не сбрасывается.
        """
        added, moved, unchanged = 0, 0, 0
        for new in new_deadlines:
            old = self.find(new.key())
            if old is None:
                self.deadlines.append(new)
                added += 1
            elif old.due != new.due:
                old.due = new.due
                moved += 1
            else:
                unchanged += 1
        return added, moved, unchanged