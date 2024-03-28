#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from datetime import datetime, timedelta


def convert_custom_reports_fields_to_list(custom_reports_fields: str) -> list:
    return custom_reports_fields.split(",") if custom_reports_fields else []


def validate_custom_fields(custom_fields, available_fields):
    denied_fields = []
    for custom_field in custom_fields:
        has_access_to_custom_field = any(available_field.get("name") == custom_field for available_field in available_fields)
        if not has_access_to_custom_field:
            denied_fields.append(custom_field)

    return denied_fields


def daterange(date1, date2):
    for n in range(int((date2 - date1).days)+1):
        yield date1 + timedelta(n) 
    
def generate_dates_to_today(date_from_str:str):
    format = '%Y-%m-%d'
    date_from = datetime.strptime(date_from_str, format)-timedelta(days=60)
    date_to = datetime.today()

    for dt in daterange(date_from, date_to):
        yield dt.strftime(format)
