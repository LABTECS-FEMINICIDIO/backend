from datetime import datetime, date, timedelta


def parse_to_date(value) -> date | None:
    if value is None or value == "":
        return None

    # Caso já venha como date/datetime
    if isinstance(value, (datetime, date)):
        return value.date() if isinstance(value, datetime) else value

    # Caso venha como número (Excel serial date)
    if isinstance(value, (int, float)):
        try:
            # 1899-12-30 é o "zero" do Excel
            return datetime(1899, 12, 30) + timedelta(days=int(value))
        except:
            return None

    # Caso venha como string
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
