"""Модель одного дедлайна."""

from datetime import date


class Deadline:
    """Один дедлайн: что сдать, по какому предмету, когда и сдано ли."""

    def __init__(self, subject, title, due, kind, done=False):
        self.subject = subject  # предмет, например, это омжет быть "Матанализ"
        self.title = title      # задание, привер - "ДЗ 5"
        self.due = due          # дата сдачи, объект date
        self.kind = kind        # тип: дз, тест, проект, экзамен...
        self.done = done        # True, если какое-то задание уже сдано

    @property
    def days_left(self):
        """Сколько дней осталось до дедлайна (меньше нуля, если прошёл)."""
        return (self.due - date.today()).days

    @property
    def is_overdue(self):
        """Просрочено: дата прошла, а задание не сдано."""
        return not self.done and self.days_left < 0

    def key(self):
        """По этому ключу узнаём одно и то же задание при повторном импорте."""
        return (self.subject.lower(), self.title.lower())

    def __str__(self):
        mark = "x" if self.done else " "
        due_text = self.due.strftime("%d.%m.%Y")
        return f"[{mark}] {due_text} | {self.subject} | {self.title} ({self.kind})"