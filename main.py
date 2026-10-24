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