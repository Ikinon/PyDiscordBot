import re
from datetime import timedelta, datetime
from typing import Optional


def human_readable_time(seconds: int) -> Optional[str]:
    if seconds == 0:
        return None
    hour = seconds // 3600 if seconds // 3600 != 0 else ""
    minutes = (seconds // 60) % 60 if (seconds // 60) % 60 != 0 else ""
    seconds = seconds - (hour * 3600 if hour != "" else 0) - (minutes * 60 if minutes != "" else 0)
    return f"{str(hour) + 'h ' if hour else ''}{str(minutes) + 'm ' if minutes else ''} {str(seconds) + 's'}"


def human_readable_datetime(time: datetime) -> str:
    return time.strftime("%A %d %B %Y at %H:%M UTC")  # day date month year time


def parse_text_time(time_str: str) -> Optional[timedelta]:
    regex = re.compile(r'^((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?$')
    parts = regex.match(time_str)
    try:
        assert parts
    except AssertionError:
        return None
    # thanks to the person online who provided below
    time_params = {name: int(param) for name, param in parts.groupdict().items() if param}
    return timedelta(**time_params)
