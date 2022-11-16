#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import json
import random


def read_json(filepath):
    with open(filepath, "r") as f:
        return json.loads(f.read())


def random_date_in_range(start_date: datetime.datetime, end_date: datetime.datetime = datetime.datetime.now()) -> datetime.datetime:
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    if days_between_dates < 2:
        days_between_dates = 2
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    return random_date


def format_airbyte_time(d: datetime):
    s = f"{d}"
    s = s.split(".")[0]
    s = s.replace(" ", "T")
    s += "+00:00"
    return s
