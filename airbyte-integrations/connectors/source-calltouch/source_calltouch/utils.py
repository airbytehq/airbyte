from datetime import datetime, timedelta


def get_yesterday_date_mdy() -> str:
    """Returns yesterday date (mm/dd/yyyy for requests report)."""
    return (datetime.now() - timedelta(1)).date().strftime("%m/%d/%Y")


def get_yesterday_date_dmy() -> str:
    """Returns yesterday date (dd/mm/yyyy for calls report)."""
    return (datetime.now() - timedelta(1)).date().strftime("%d/%m/%Y")


def get_last_month_date_mdy() -> str:
    """Returns last month date (mm/dd/yyyy for requests report)."""
    return (datetime.now() - timedelta(30)).date().strftime("%m/%d/%Y")


def get_last_month_date_dmy() -> str:
    """Returns last month date (dd/mm/yyyy for calls report)."""
    return (datetime.now() - timedelta(30)).date().strftime("%d/%m/%Y")


def get_today_minus_n_days_date_dmy(days: int):
    return (datetime.now() - timedelta(days)).date().strftime("%d/%m/%Y")


def get_today_minus_n_days_date_mdy(days: int):
    return (datetime.now() - timedelta(days)).date().strftime("%m/%d/%Y")


def date_to_request_report_date(iso_date: str) -> str:
    """
    Format date to request report format
    :param iso_date: Date in format dd/mm/yyyy
    :return: Date in format mm/dd/yyyy
    """
    day, month, year = str(iso_date).split("/")
    date = "/".join((month, day, year))
    return date
