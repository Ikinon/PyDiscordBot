from typing import Optional


def human_readable_time(seconds: int) -> Optional[str]:
    if seconds == 0:
        return None
    hour = seconds // 3600 if seconds // 3600 != 0 else ""
    minutes = (seconds // 60) % 60 if (seconds // 60) % 60 != 0 else ""
    seconds = seconds - (hour * 3600 if hour != "" else 0) - (minutes * 60 if minutes != "" else 0)
    return f"{str(hour) + 'h ' if hour else ''}{str(minutes) + 'm ' if minutes else ''} {str(seconds) + 's'}"
