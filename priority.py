"""Мои правила: что горит сильнее и как выглядит отчёт."""

URGENT_DAYS = 3  # "скоро" = не больше чем через 3 дня
KIND_WEIGHTS = {"экзамен": 3, "проект": 3, "контрольная": 2, "дз": 2, "тест": 1, "другое": 1}
GROUP_ORDER = ["Просрочено", "Сегодня", "Скоро", "Потом"]


def group_of(deadline):
    """В какую группу попадает несданный дедлайн."""
    if deadline.days_left < 0:
        return "Просрочено"
    if deadline.days_left == 0:
        return "Сегодня"
    if deadline.days_left <= URGENT_DAYS:
        return "Скоро"
    return "Потом"


def sort_key(deadline):
    """Сначала ближайшие. При одной дате выше то, что важнее по типу."""
    return (deadline.days_left, -KIND_WEIGHTS.get(deadline.kind, 1))


def plan_by_groups(deadlines):
    """Возвращает словарь {группа: [несданные дедлайны по порядку]}."""
    groups = {name: [] for name in GROUP_ORDER}
    active = [deadline for deadline in deadlines if not deadline.done]
    for deadline in sorted(active, key=sort_key):
        groups[group_of(deadline)].append(deadline)
    return groups


def make_report(deadlines):
    """Собирает текст отчёта: сколько сдано, просрочено и что висит по предметам."""
    done = [deadline for deadline in deadlines if deadline.done]
    overdue = [deadline for deadline in deadlines if deadline.is_overdue]

    left_by_subject = {}
    for deadline in deadlines:
        if not deadline.done:
            left_by_subject[deadline.subject] = left_by_subject.get(deadline.subject, 0) + 1

    lines = [
        "Отчёт по дедлайнам",
        f"Всего заданий: {len(deadlines)}",
        f"Сдано: {len(done)}",
        f"Просрочено: {len(overdue)}",
        "Осталось сдать по предметам:",
    ]
    for subject, count in sorted(left_by_subject.items()):
        lines.append(f"  {subject}: {count}")
    if not left_by_subject:
        lines.append("  ничего, всё сдано")
    return "\n".join(lines)