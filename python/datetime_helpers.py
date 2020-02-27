def beginning_of_month(now):
    return dt.datetime(day=1, month=now.month, year=now.year)


def end_of_month(now):
    return dt.datetime(day=calendar.monthrange(now.year, now.month)[1],
                       month=now.month, year=now.year)


def decrement_month(now):
    last = beginning_of_month(now) - dt.timedelta(days=1)
    return datetime.combine(
            dt.datetime(day=now.day, month=last.month, year=last.year),
            now.time())


def increment_month(now):
    first = end_of_month(now) + dt.timedelta(days=1)
    return datetime.combine(
            dt.datetime(day=now.day, month=first.month, year=first.year),
            now.time())


def increment_year(now, years=1):
    return datetime.combine(dt.datetime(day=now.day, month=now.month, year=now.year+years),
                            now.time())


def decrement_year(now, years=1):
    return increment_year(now, -years)


