from datetime import date, timedelta


def get_yesterday_datetime():
    yesterday = date.today() - timedelta(days=1)
    yesterday_strf = yesterday.strftime("%Y-%m-%d")
    return (yesterday_strf + " 00:00:00", yesterday_strf + " 23:59:59")


def get_today_minus_n_days_date(days: int):
    yesterday = date.today() - timedelta(days=1)
    yesterday_strf = yesterday.strftime("%Y-%m-%d")

    minus_n_days = date.today() - timedelta(days=days)
    minus_n_days_strf = minus_n_days.strftime("%Y-%m-%d")
    return (minus_n_days_strf + " 00:00:00", yesterday_strf + " 00:00:00")


def difference_in_days_between_two_datetimes(date1: str, date2: str):
    splitted_date1 = list(map(int, date1.split(" ")[0].split("-")))
    splitted_date2 = list(map(int, date2.split(" ")[0].split("-")))
    date1 = date(splitted_date1[0], splitted_date1[1], splitted_date1[2])
    date2 = date(splitted_date2[0], splitted_date2[1], splitted_date2[2])
    return (date2 - date1).days
