from datetime import date, timedelta


def parse_iso(d: str) -> date:
    return date.fromisoformat(d)


def count_weekdays_inclusive(start_iso: str, end_iso: str) -> int:
    start = parse_iso(start_iso)
    end = parse_iso(end_iso)
    if end < start:
        raise ValueError("end date before start date")
    days = 0
    current = start
    while current <= end:
        if current.weekday() < 5:  # 0=Mon .. 4=Fri
            days += 1
        current += timedelta(days=1)
    return days
