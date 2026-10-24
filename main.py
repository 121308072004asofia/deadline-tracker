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


def import_from_csv(store):
    path_text = input("Путь к CSV-файлу: ").strip().strip('"')  # Windows копирует путь в кавычках
    if path_text == "":
        print("Путь не введён.")
        return
    try:
        new_deadlines, problems = import_file(Path(path_text))
    except FileNotFoundError:
        print(f"Файл не найден: {path_text}")
        return
    except OSError as error:
        print(f"Не получилось открыть файл: {error}")
        return
    except ValueError as error:
        print(f"Не получилось загрузить: {error}")
        return

    added, moved, unchanged = store.merge(new_deadlines)
    store.save()
    print(f"Добавлено: {added}, перенесено: {moved}, без изменений: {unchanged}")
    if problems:
        print(f"Пропущено строк: {len(problems)}")
        for problem in problems:
            print(f"  - {problem}")


def mark_done(store):
    numbered = show_plan(store)
    if not numbered:
        return
    number = ask_number("Номер сданного задания (Enter - отмена): ", len(numbered))
    if number is None:
        return
    deadline = numbered[number - 1]
    deadline.done = True
    store.save()
    print(f"Отмечено: {deadline.title}")


def add_manually(store):
    subject = ask_text("Предмет: ")
    title = ask_text("Задание: ")
    while True:
        try:
            due = parse_date(input("Дата (например 24.10.2026): "))
            break
        except ValueError as error:
            print(f"Ошибка: {error}. Попробуйте ещё раз.")
    kind = normalize_kind(input("Тип (дз, тест, проект, экзамен, контрольная): "))

    added, moved, _ = store.merge([Deadline(subject, title, due, kind)])
    store.save()
    if added:
        print("Дедлайн добавлен.")
    elif moved:
        print("Такое задание уже было, дата обновлена.")
    else:
        print("Такой дедлайн уже есть.")


def show_report(store):
    report = make_report(store.deadlines)
    print()
    print(report)
    REPORT_FILE.write_text(report, encoding="utf-8")
    print(f"\nОтчёт сохранён в {REPORT_FILE.name}")


def main():
    store = DeadlineStore(STATE_FILE)
    store.load()
    if store.broken_lines:
        print(f"Внимание: в {STATE_FILE.name} не прочитались строки {store.broken_lines}")
    show_plan(store)

    while True:
        print(MENU)
        choice = input("Выберите действие: ").strip()
        match choice:
            case "1":
                show_plan(store)
            case "2":
                import_from_csv(store)
            case "3":
                mark_done(store)
            case "4":
                add_manually(store)
            case "5":
                show_report(store)
            case "0":
                print("Пока!")
                break
            case _:
                print("Такой команды нет, введите цифру из меню.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nПрограмма остановлена.")