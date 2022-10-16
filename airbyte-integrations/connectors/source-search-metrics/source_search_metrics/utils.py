#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from datetime import datetime


def to_datetime_str(date: datetime) -> str:
    """
    Returns the formated datetime string.
    :: Output example: '20210715T' FORMAT : "%Y%m%d"
    """
    return date.strftime("%Y%m%d")
