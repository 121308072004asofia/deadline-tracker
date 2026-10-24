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