from datetime import datetime, date, time, timedelta


def parse_to_date_str(value) -> str | None:
    if value is None or value == "":
        return None

    if isinstance(value, (datetime, date)):
        return value.strftime("%d/%m/%Y")

    if isinstance(value, (int, float)):
        try:
            dt = datetime(1899, 12, 30) + timedelta(days=int(value))
            return dt.strftime("%d/%m/%Y")
        except:
            return None

    if isinstance(value, str):
        value = value.strip()

        formatos = [
            "%d/%m/%Y",
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%Y/%m/%d",
            "%d.%m.%Y",
            "%Y.%m.%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
        ]

        for fmt in formatos:
            try:
                return datetime.strptime(value, fmt).strftime("%d/%m/%Y")
            except ValueError:
                continue

    return None


def parse_time_str(value) -> str | None:
    if value is None or value == "":
        return None

    if isinstance(value, datetime):
        return value.strftime("%H:%M")

    if isinstance(value, time):
        return value.strftime("%H:%M")

    if isinstance(value, str):
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                return datetime.strptime(value, fmt).strftime("%H:%M")
            except ValueError:
                continue

    return None


def parse_to_date(value) -> date | None:
    if value is None or value == "":
        return None

    if isinstance(value, (datetime, date)):
        return value.date() if isinstance(value, datetime) else value

    if isinstance(value, (int, float)):
        try:
            return datetime(1899, 12, 30) + timedelta(days=int(value))
        except:
            return None

    if isinstance(value, str):
        value = value.strip()

        formatos = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%Y/%m/%d",
            "%d.%m.%Y",
            "%Y.%m.%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
        ]

        for fmt in formatos:
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue

    return None
