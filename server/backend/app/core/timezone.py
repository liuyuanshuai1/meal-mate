from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.config import get_settings


def now_tz() -> datetime:
    return datetime.now(ZoneInfo(get_settings().tz))
