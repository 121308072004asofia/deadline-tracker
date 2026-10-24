"""Трекер дедлайнов. Запуск: python main.py"""

from pathlib import Path

from importer import import_file, normalize_kind, parse_date
from models import Deadline
from priority import make_report, plan_by_groups
from storage import DeadlineStore

BASE_DIR = Path(__file__).parent
STATE_FILE = BASE_DIR / "data" / "deadlines.csv"
REPORT_FILE = BASE_DIR / "report.txt"

MENU = """
1 - показать, что горит
2 - загрузить дедлайны из CSV
3 - отметить задание сданным
4 - добавить дедлайн вручную
5 - отчёт
0 - выход"""

def describe_days(days_left):
    """Человеческая подпись к количеству дней."""
    if days_left < 0:
        return f"просрочено на {-days_left} дн."
    if days_left == 0:
        return "сегодня!"
    return f"осталось {days_left} дн."


def show_plan(store):
    """Печатает несданные дедлайны по группам и возвращает их в порядке номеров."""
    numbered = []
    for group_name, items in plan_by_groups(store.deadlines).items():
        if not items:
            continue
        print(f"\n== {group_name} ==")
        for deadline in items:
            numbered.append(deadline)
            print(f"{len(numbered)}. {deadline} - {describe_days(deadline.days_left)}")
    if not numbered:
        print("\nНесданных дедлайнов нет.")
    return numbered


def ask_text(prompt):
    """Спрашивает, пока не введут непустой текст."""
    while True:
        answer = input(prompt).strip()
        if answer:
            return answer
        print("Поле не может быть пустым.")


def ask_number(prompt, maximum):
    """Спрашивает номер от 1 до maximum. Пустой ввод = отмена (None)."""
    while True:
        answer = input(prompt).strip()
        if answer == "":
            return None
        try:
            number = int(answer)
        except ValueError:
            print("Нужно ввести число.")
            continue
        if 1 <= number <= maximum:
            return number
        print(f"Нет задания с номером {number}.")